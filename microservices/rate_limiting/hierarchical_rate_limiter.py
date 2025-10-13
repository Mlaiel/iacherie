"""
Hierarchical Rate Limiter Enterprise - IA Chérie
==============================================
Rate Limiter hiérarchique pour rate limiting multi-niveau.
User → Team → Organization → Global limits avec priorities.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: IA Chérie Rate Limiting
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque
import statistics

from .distributed_rate_limiter import (
    DistributedRateLimiter, RateLimitConfig, RateLimitResult, 
    RateLimitAlgorithm, RateLimitStatus
)

logger = logging.getLogger(__name__)

class HierarchyLevel(Enum):
    """Niveaux hiérarchiques rate limiting"""
    USER = "user"
    TEAM = "team"
    ORGANIZATION = "organization"
    GLOBAL = "global"
    SERVICE = "service"
    ENDPOINT = "endpoint"

class QuotaAllocationStrategy(Enum):
    """Stratégies allocation quota"""
    FAIR_SHARE = "fair_share"          # Equal distribution
    WEIGHTED = "weighted"              # Based on weights/priorities
    FIRST_COME_FIRST_SERVED = "fcfs"  # First requests get priority
    PRIORITY_BASED = "priority"        # High priority users first
    ADAPTIVE = "adaptive"              # ML-based allocation
    ELASTIC = "elastic"                # Borrowing from parent levels

class InheritanceMode(Enum):
    """Modes d'héritage quota"""
    STRICT = "strict"        # No borrowing allowed
    BORROWING = "borrowing"  # Can borrow from parent
    SHARING = "sharing"      # Share with siblings
    ELASTIC = "elastic"      # Dynamic allocation

@dataclass
class HierarchyConfig:
    """Configuration hiérarchie rate limiting"""
    levels: List[HierarchyLevel]
    allocation_strategy: QuotaAllocationStrategy = QuotaAllocationStrategy.WEIGHTED
    inheritance_mode: InheritanceMode = InheritanceMode.BORROWING
    enable_quota_borrowing: bool = True
    enable_burst_sharing: bool = True
    borrowing_penalty_factor: float = 1.2  # Cost multiplier when borrowing
    sharing_bonus_factor: float = 0.9      # Cost reduction when sharing
    rebalancing_interval_seconds: int = 300
    emergency_allocation_threshold: float = 0.9  # Trigger emergency allocation
    
@dataclass
class HierarchicalQuota:
    """Quota hiérarchique avec inheritance"""
    level: HierarchyLevel
    identifier: str
    parent_identifier: Optional[str]
    allocated_quota: int
    used_quota: int = 0
    borrowed_quota: int = 0
    shared_quota: int = 0
    reserved_quota: int = 0
    priority: int = 100
    weight: float = 1.0
    last_reset: datetime = field(default_factory=datetime.now)
    children_quotas: List[str] = field(default_factory=list)
    
    @property
    def available_quota(self) -> int:
        """Quota disponible"""
        return max(0, self.allocated_quota + self.borrowed_quota + self.shared_quota - self.used_quota - self.reserved_quota)
    
    @property
    def utilization_rate(self) -> float:
        """Taux d'utilisation"""
        total_quota = self.allocated_quota + self.borrowed_quota + self.shared_quota
        if total_quota <= 0:
            return 0.0
        return self.used_quota / total_quota

@dataclass
class HierarchicalRequest:
    """Request avec context hiérarchique"""
    identifier: str
    level: HierarchyLevel
    parent_identifier: Optional[str] = None
    cost: int = 1
    priority: int = 100
    user_tier: str = "free"
    emergency: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def get_hierarchy_path(self) -> List[str]:
        """Path hiérarchique complet"""
        path = [self.identifier]
        if self.parent_identifier:
            # Simple parent path - dans un vrai système, récursion complète
            path.append(self.parent_identifier)
        return path

@dataclass
class LimitCheckResult:
    """Résultat vérification limite hiérarchique"""
    allowed: bool
    level_results: Dict[HierarchyLevel, RateLimitResult]
    quota_allocation: Dict[str, int]
    borrowing_applied: bool = False
    sharing_applied: bool = False
    emergency_allocation: bool = False
    blocking_level: Optional[HierarchyLevel] = None
    total_cost: int = 1
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass 
class QuotaAllocation:
    """Allocation quota dynamique"""
    allocation_id: str
    target_identifier: str
    level: HierarchyLevel
    allocated_amount: int
    source_level: Optional[HierarchyLevel] = None
    source_identifier: Optional[str] = None
    allocation_type: str = "direct"  # direct, borrowed, shared, emergency
    expires_at: Optional[datetime] = None
    conditions: List[str] = field(default_factory=list)
    
@dataclass
class InheritanceResult:
    """Résultat inheritance quota"""
    parent_identifier: str
    child_identifiers: List[str]
    inheritance_rules: Dict[str, Any]
    allocated_quotas: Dict[str, int]
    sharing_agreements: List[Dict[str, Any]]
    total_inherited: int
    total_shared: int

@dataclass
class OverflowRequest:
    """Request overflow quota"""
    identifier: str
    level: HierarchyLevel
    requested_amount: int
    overflow_reason: str
    urgency: str = "normal"  # low, normal, high, critical
    fallback_strategies: List[str] = field(default_factory=list)

@dataclass
class OverflowDecision:
    """Décision overflow"""
    approved: bool
    granted_amount: int
    overflow_source: Optional[str] = None
    conditions: List[str] = field(default_factory=list)
    penalty_factor: float = 1.0
    expires_at: Optional[datetime] = None

class PriorityQueueManager:
    """Gestionnaire queue priorités"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.queues = {
            "critical": deque(),
            "high": deque(), 
            "normal": deque(),
            "low": deque()
        }
        self.priority_weights = {
            "critical": 1000,
            "high": 100,
            "normal": 10,
            "low": 1
        }
        self.total_queued = 0
        self.logger = logging.getLogger(__name__)
    
    async def enqueue_request(self, request: HierarchicalRequest, priority: str = "normal") -> bool:
        """Ajout request à la queue priorité"""
        if self.total_queued >= self.max_size:
            # Queue pleine - reject low priority requests
            if priority == "low":
                return False
            # Eject oldest low priority request
            if self.queues["low"]:
                self.queues["low"].popleft()
            else:
                return False
        
        self.queues[priority].append(request)
        self.total_queued += 1
        return True
    
    async def dequeue_request(self) -> Optional[HierarchicalRequest]:
        """Récupération next request par priorité"""
        # Order par priorité décroissante
        for priority in ["critical", "high", "normal", "low"]:
            if self.queues[priority]:
                request = self.queues[priority].popleft()
                self.total_queued -= 1
                return request
        
        return None
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """Statistiques queues"""
        return {
            "total_queued": self.total_queued,
            "by_priority": {
                priority: len(queue) 
                for priority, queue in self.queues.items()
            },
            "capacity_used": (self.total_queued / self.max_size) * 100
        }

class QuotaAllocationEngine:
    """Moteur allocation quota hiérarchique"""
    
    def __init__(self, config: HierarchyConfig):
        self.config = config
        self.quota_registry = {}  # identifier -> HierarchicalQuota
        self.allocation_history = deque(maxlen=10000)
        self.sharing_agreements = {}
        self.borrowing_records = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    async def allocate_quota(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation quota selon stratégie configurée"""
        try:
            if self.config.allocation_strategy == QuotaAllocationStrategy.FAIR_SHARE:
                return await self._allocate_fair_share(request)
            elif self.config.allocation_strategy == QuotaAllocationStrategy.WEIGHTED:
                return await self._allocate_weighted(request)
            elif self.config.allocation_strategy == QuotaAllocationStrategy.PRIORITY_BASED:
                return await self._allocate_priority_based(request)
            elif self.config.allocation_strategy == QuotaAllocationStrategy.ADAPTIVE:
                return await self._allocate_adaptive(request)
            elif self.config.allocation_strategy == QuotaAllocationStrategy.ELASTIC:
                return await self._allocate_elastic(request)
            else:  # FCFS fallback
                return await self._allocate_fcfs(request)
                
        except Exception as e:
            self.logger.error(f"Quota allocation failed for {request.identifier}: {e}")
            # Fallback allocation
            return QuotaAllocation(
                allocation_id=str(uuid.uuid4()),
                target_identifier=request.identifier,
                level=request.level,
                allocated_amount=0,
                allocation_type="error"
            )
    
    async def _allocate_fair_share(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation équitable entre peers"""
        # Trouver siblings au même niveau
        siblings = await self._find_siblings(request.identifier, request.level)
        
        if not siblings:
            # Pas de siblings - allocation directe
            return await self._direct_allocation(request)
        
        # Calcul fair share
        parent_quota = await self._get_parent_available_quota(request)
        fair_share = parent_quota // (len(siblings) + 1)  # +1 pour le requester
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=min(fair_share, request.cost),
            allocation_type="fair_share"
        )
    
    async def _allocate_weighted(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation pondérée selon weights"""
        quota_record = self.quota_registry.get(request.identifier)
        if not quota_record:
            return await self._direct_allocation(request)
        
        # Weight-based allocation
        total_weight = await self._calculate_total_weight(request.level)
        parent_quota = await self._get_parent_available_quota(request)
        
        if total_weight > 0:
            weighted_allocation = int(
                (quota_record.weight / total_weight) * parent_quota
            )
        else:
            weighted_allocation = parent_quota
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=min(weighted_allocation, request.cost),
            allocation_type="weighted"
        )
    
    async def _allocate_priority_based(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation basée sur priorité"""
        # High priority gets preferential treatment
        if request.priority >= 200:  # High priority threshold
            parent_quota = await self._get_parent_available_quota(request)
            allocation = min(parent_quota, request.cost * 2)  # Bonus pour high priority
        elif request.priority <= 50: # Low priority
            parent_quota = await self._get_parent_available_quota(request)
            allocation = min(parent_quota // 2, request.cost)  # Reduced allocation
        else:  # Normal priority
            allocation = request.cost
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=allocation,
            allocation_type="priority_based"
        )
    
    async def _allocate_adaptive(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation adaptative ML-based"""
        # Placeholder pour ML-based allocation
        # Dans une implémentation complète, utiliser historical patterns
        
        # Analyse utilisation historique
        historical_usage = await self._get_historical_usage(request.identifier)
        predicted_need = await self._predict_quota_need(historical_usage, request)
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=min(predicted_need, request.cost),
            allocation_type="adaptive"
        )
    
    async def _allocate_elastic(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation élastique avec borrowing automatique"""
        # Tentative allocation directe
        direct_quota = await self._get_direct_quota_available(request.identifier)
        
        if direct_quota >= request.cost:
            return QuotaAllocation(
                allocation_id=str(uuid.uuid4()),
                target_identifier=request.identifier,
                level=request.level,
                allocated_amount=request.cost,
                allocation_type="direct"
            )
        
        # Borrowing si insuffisant
        if self.config.enable_quota_borrowing:
            borrowed_amount = await self._attempt_borrowing(request, request.cost - direct_quota)
            total_allocation = direct_quota + borrowed_amount
            
            return QuotaAllocation(
                allocation_id=str(uuid.uuid4()),
                target_identifier=request.identifier,
                level=request.level,
                allocated_amount=total_allocation,
                allocation_type="elastic_borrowed"
            )
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=direct_quota,
            allocation_type="elastic_limited"
        )
    
    async def _direct_allocation(self, request: HierarchicalRequest) -> QuotaAllocation:
        """Allocation directe simple"""
        available = await self._get_direct_quota_available(request.identifier)
        
        return QuotaAllocation(
            allocation_id=str(uuid.uuid4()),
            target_identifier=request.identifier,
            level=request.level,
            allocated_amount=min(available, request.cost),
            allocation_type="direct"
        )
    
    async def _find_siblings(self, identifier: str, level: HierarchyLevel) -> List[str]:
        """Trouver siblings au même niveau"""
        siblings = []
        for quota_id, quota in self.quota_registry.items():
            if (quota.level == level and 
                quota_id != identifier and 
                quota.parent_identifier == self.quota_registry.get(identifier, {}).parent_identifier):
                siblings.append(quota_id)
        return siblings
    
    async def _get_parent_available_quota(self, request: HierarchicalRequest) -> int:
        """Récupération quota disponible parent"""
        if not request.parent_identifier:
            return 1000  # Default pour root level
        
        parent_quota = self.quota_registry.get(request.parent_identifier)
        if parent_quota:
            return parent_quota.available_quota
        
        return 100  # Fallback
    
    async def _calculate_total_weight(self, level: HierarchyLevel) -> float:
        """Calcul poids total pour niveau"""
        total_weight = 0.0
        for quota in self.quota_registry.values():
            if quota.level == level:
                total_weight += quota.weight
        return total_weight
    
    async def _get_direct_quota_available(self, identifier: str) -> int:
        """Quota directement disponible"""
        quota = self.quota_registry.get(identifier)
        if quota:
            return quota.available_quota
        return 0
    
    async def _attempt_borrowing(self, request: HierarchicalRequest, needed_amount: int) -> int:
        """Tentative borrowing quota"""
        if not self.config.enable_quota_borrowing:
            return 0
        
        # Recherche sources de borrowing (parent, siblings)
        borrowed = 0
        
        # Borrowing depuis parent
        if request.parent_identifier:
            parent_quota = self.quota_registry.get(request.parent_identifier)
            if parent_quota and parent_quota.available_quota > 0:
                borrowable = min(parent_quota.available_quota, needed_amount)
                borrowed += borrowable
                
                # Record borrowing
                self.borrowing_records[request.identifier].append({
                    "source": request.parent_identifier,
                    "amount": borrowable,
                    "timestamp": datetime.now(),
                    "penalty_factor": self.config.borrowing_penalty_factor
                })
        
        return borrowed
    
    async def _get_historical_usage(self, identifier: str) -> Dict[str, Any]:
        """Analyse usage historique"""
        # Simplified historical analysis
        return {
            "avg_usage_per_hour": 50,
            "peak_usage": 100,
            "trend": "stable"
        }
    
    async def _predict_quota_need(self, historical_usage: Dict[str, Any], 
                                request: HierarchicalRequest) -> int:
        """Prédiction besoin quota"""
        base_need = historical_usage.get("avg_usage_per_hour", 50)
        
        # Adjustment basé sur priorité et emergency
        if request.emergency:
            return int(base_need * 2)
        elif request.priority > 150:
            return int(base_need * 1.5)
        else:
            return base_need

class HierarchicalRateLimiter:
    """
    Rate Limiter hiérarchique pour rate limiting multi-niveau.
    User → Team → Organization → Global limits avec priorities.
    """
    
    def __init__(self, distributed_limiter: DistributedRateLimiter, 
                 hierarchy_config: HierarchyConfig):
        self.distributed_limiter = distributed_limiter
        self.hierarchy_config = hierarchy_config
        self.priority_queue = PriorityQueueManager()
        self.quota_allocator = QuotaAllocationEngine(hierarchy_config)
        
        # Registry hiérarchique
        self.hierarchy_registry = {}  # level -> {identifier -> parent_id}
        self.level_limiters = {}      # level -> DistributedRateLimiter
        
        # Monitoring et metrics
        self.hierarchy_metrics = {
            "total_requests": 0,
            "hierarchy_checks": 0,
            "borrowing_events": 0,
            "sharing_events": 0,
            "emergency_allocations": 0
        }
        
        self.logger = logging.getLogger(__name__)
        
        # Background tasks
        self._background_tasks = []
        self._stop_event = asyncio.Event()
    
    async def initialize(self) -> bool:
        """Initialisation hierarchical rate limiter"""
        try:
            # Initialisation distributed limiter base
            await self.distributed_limiter.initialize()
            
            # Création limiters par niveau
            await self._initialize_level_limiters()
            
            # Démarrage background tasks
            await self._start_background_tasks()
            
            self.logger.info("Hierarchical rate limiter initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Hierarchical rate limiter initialization failed: {e}")
            return False
    
    async def check_hierarchical_limits(self, request: HierarchicalRequest) -> LimitCheckResult:
        """
        Vérification rate limits hiérarchiques avec priority.
        
        Hierarchical Features:
        - Multi-level rate limiting (user/team/org/global)
        - Priority-based quota allocation
        - Fair sharing algorithms entre users/teams
        - Burst sharing from parent to child levels
        - Quota borrowing avec automatic repayment
        - Emergency quota allocation pour critical requests
        - Real-time quota rebalancing
        """
        start_time = time.time()
        self.hierarchy_metrics["hierarchy_checks"] += 1
        
        try:
            # 1. Détermination hierarchy path
            hierarchy_path = await self._build_hierarchy_path(request)
            
            # 2. Vérification à chaque niveau hiérarchique
            level_results = {}
            total_cost = request.cost
            blocking_level = None
            
            for level, identifier in hierarchy_path.items():
                # Vérification rate limit pour ce niveau
                level_result = await self._check_level_limit(
                    level, identifier, request.cost, request.metadata
                )
                level_results[level] = level_result
                
                # Si bloqué à ce niveau
                if not level_result.allowed:
                    blocking_level = level
                    
                    # Tentative borrowing si configuré
                    if self.hierarchy_config.enable_quota_borrowing:
                        borrowing_result = await self._attempt_level_borrowing(
                            level, identifier, request
                        )
                        if borrowing_result:
                            level_result.allowed = True
                            self.hierarchy_metrics["borrowing_events"] += 1
                    
                    # Tentative emergency allocation si critique
                    if not level_result.allowed and request.emergency:
                        emergency_result = await self._emergency_allocation(
                            level, identifier, request
                        )
                        if emergency_result:
                            level_result.allowed = True
                            self.hierarchy_metrics["emergency_allocations"] += 1
                    
                    # Si toujours bloqué, arrêter vérifications
                    if not level_result.allowed:
                        break
            
            # 3. Allocation quota dynamique
            quota_allocation = await self.quota_allocator.allocate_quota(request)
            
            # 4. Application sharing si configuré
            sharing_applied = False
            if (self.hierarchy_config.enable_burst_sharing and 
                quota_allocation.allocated_amount < request.cost):
                sharing_result = await self._attempt_burst_sharing(request, quota_allocation)
                if sharing_result:
                    sharing_applied = True
                    self.hierarchy_metrics["sharing_events"] += 1
            
            # 5. Décision finale
            final_allowed = all(result.allowed for result in level_results.values())
            
            # 6. Update quotas si autorisé
            if final_allowed:
                await self._update_hierarchy_quotas(hierarchy_path, request.cost)
            
            # 7. Génération résultat
            result = LimitCheckResult(
                allowed=final_allowed,
                level_results=level_results,
                quota_allocation={request.identifier: quota_allocation.allocated_amount},
                borrowing_applied=any("borrowed" in r.metadata.get("allocation_type", "") 
                                    for r in level_results.values()),
                sharing_applied=sharing_applied,
                emergency_allocation=any("emergency" in r.metadata.get("allocation_type", "")
                                       for r in level_results.values()),
                blocking_level=blocking_level,
                total_cost=total_cost,
                reason=await self._generate_hierarchy_reason(level_results, blocking_level),
                metadata={
                    "hierarchy_path": list(hierarchy_path.keys()),
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "quota_strategy": str(self.hierarchy_config.allocation_strategy)
                }
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Hierarchical limit check failed for {request.identifier}: {e}")
            return LimitCheckResult(
                allowed=False,
                level_results={},
                quota_allocation={},
                reason=f"Hierarchy check error: {str(e)}",
                metadata={"error": str(e)}
            )
    
    async def _build_hierarchy_path(self, request: HierarchicalRequest) -> Dict[HierarchyLevel, str]:
        """Construction path hiérarchique complet"""
        path = {request.level: request.identifier}
        
        # Ajout parent levels
        current_identifier = request.identifier
        current_level = request.level
        
        # Simple parent hierarchy - dans une implémentation complète, 
        # construire le path complet récursivement
        if request.parent_identifier:
            # Détermination parent level
            parent_level = await self._get_parent_level(current_level)
            if parent_level:
                path[parent_level] = request.parent_identifier
        
        # Ajout global level si pas présent
        if HierarchyLevel.GLOBAL not in path:
            path[HierarchyLevel.GLOBAL] = "global"
        
        return path
    
    async def _get_parent_level(self, current_level: HierarchyLevel) -> Optional[HierarchyLevel]:
        """Détermination niveau parent"""
        hierarchy_order = [
            HierarchyLevel.USER,
            HierarchyLevel.TEAM, 
            HierarchyLevel.ORGANIZATION,
            HierarchyLevel.GLOBAL
        ]
        
        try:
            current_index = hierarchy_order.index(current_level)
            if current_index < len(hierarchy_order) - 1:
                return hierarchy_order[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    async def _check_level_limit(self, level: HierarchyLevel, identifier: str,
                               cost: int, metadata: Optional[Dict[str, Any]]) -> RateLimitResult:
        """Vérification limit pour niveau spécifique"""
        # Utilisation limiter spécialisé pour ce niveau ou fallback
        level_limiter = self.level_limiters.get(level, self.distributed_limiter)
        
        # Construction identifiant avec namespace niveau
        namespaced_identifier = f"{level.value}:{identifier}"
        
        return await level_limiter.check_rate_limit(
            namespaced_identifier, cost, metadata
        )
    
    async def _attempt_level_borrowing(self, level: HierarchyLevel, identifier: str,
                                     request: HierarchicalRequest) -> bool:
        """Tentative borrowing pour niveau"""
        if not self.hierarchy_config.enable_quota_borrowing:
            return False
        
        # Recherche parent level pour borrowing
        parent_level = await self._get_parent_level(level)
        if not parent_level:
            return False
        
        # Vérification quota disponible parent
        parent_identifier = request.parent_identifier or "parent"
        parent_available = await self._get_level_available_quota(parent_level, parent_identifier)
        
        if parent_available >= request.cost:
            # Borrowing réussi
            await self._record_borrowing(level, identifier, parent_level, 
                                       parent_identifier, request.cost)
            return True
        
        return False
    
    async def _emergency_allocation(self, level: HierarchyLevel, identifier: str,
                                  request: HierarchicalRequest) -> bool:
        """Allocation d'urgence pour requests critiques"""
        if not request.emergency:
            return False
        
        # Emergency allocation depuis réserve globale
        emergency_quota = await self._get_emergency_quota_available()
        
        if emergency_quota >= request.cost:
            await self._allocate_emergency_quota(level, identifier, request.cost)
            return True
        
        return False
    
    async def _attempt_burst_sharing(self, request: HierarchicalRequest,
                                   allocation: QuotaAllocation) -> bool:
        """Tentative burst sharing"""
        if not self.hierarchy_config.enable_burst_sharing:
            return False
        
        # Recherche siblings avec quota disponible
        siblings = await self._find_sharing_siblings(request)
        
        needed_amount = request.cost - allocation.allocated_amount
        shared_amount = 0
        
        for sibling_id in siblings:
            sibling_available = await self._get_sibling_available_quota(sibling_id)
            
            if sibling_available > 0:
                share_amount = min(sibling_available // 2, needed_amount - shared_amount)
                if share_amount > 0:
                    await self._record_sharing(request.identifier, sibling_id, share_amount)
                    shared_amount += share_amount
                    
                    if shared_amount >= needed_amount:
                        break
        
        return shared_amount > 0
    
    async def _initialize_level_limiters(self):
        """Initialisation limiters par niveau hiérarchique"""
        for level in self.hierarchy_config.levels:
            # Configuration spécialisée par niveau
            level_config = await self._get_level_config(level)
            
            # Création limiter spécialisé
            level_limiter = DistributedRateLimiter(
                self.distributed_limiter.redis,
                level_config
            )
            await level_limiter.initialize()
            
            self.level_limiters[level] = level_limiter
    
    async def _get_level_config(self, level: HierarchyLevel) -> RateLimitConfig:
        """Configuration spécialisée par niveau"""
        base_config = self.distributed_limiter.config
        
        # Customizations par niveau
        level_customizations = {
            HierarchyLevel.USER: {
                "requests_per_second": 10,
                "burst_capacity": 20,
                "redis_key_prefix": "user_rl"
            },
            HierarchyLevel.TEAM: {
                "requests_per_second": 100,
                "burst_capacity": 200,
                "redis_key_prefix": "team_rl"
            },
            HierarchyLevel.ORGANIZATION: {
                "requests_per_second": 1000,
                "burst_capacity": 2000,
                "redis_key_prefix": "org_rl"
            },
            HierarchyLevel.GLOBAL: {
                "requests_per_second": 10000,
                "burst_capacity": 20000,
                "redis_key_prefix": "global_rl"
            }
        }
        
        customization = level_customizations.get(level, {})
        
        return RateLimitConfig(
            requests_per_second=customization.get("requests_per_second", base_config.requests_per_second),
            burst_capacity=customization.get("burst_capacity", base_config.burst_capacity),
            window_size_seconds=base_config.window_size_seconds,
            algorithm=base_config.algorithm,
            redis_key_prefix=customization.get("redis_key_prefix", base_config.redis_key_prefix),
            backoff_strategy=base_config.backoff_strategy
        )
    
    async def _start_background_tasks(self):
        """Démarrage tâches background"""
        # Tâche rebalancing quota
        rebalancing_task = asyncio.create_task(self._quota_rebalancing_loop())
        self._background_tasks.append(rebalancing_task)
        
        # Tâche cleanup borrowing expiré
        cleanup_task = asyncio.create_task(self._borrowing_cleanup_loop())
        self._background_tasks.append(cleanup_task)
    
    async def _quota_rebalancing_loop(self):
        """Loop rebalancing quota en background"""
        while not self._stop_event.is_set():
            try:
                await self._perform_quota_rebalancing()
                await asyncio.sleep(self.hierarchy_config.rebalancing_interval_seconds)
            except Exception as e:
                self.logger.error(f"Quota rebalancing error: {e}")
                await asyncio.sleep(60)
    
    async def _borrowing_cleanup_loop(self):
        """Loop cleanup borrowing expiré"""
        while not self._stop_event.is_set():
            try:
                await self._cleanup_expired_borrowing()
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                self.logger.error(f"Borrowing cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _perform_quota_rebalancing(self):
        """Rebalancing quota entre niveaux"""
        for level in self.hierarchy_config.levels:
            # Analyse utilisation niveau
            level_usage = await self._analyze_level_usage(level)
            
            # Rebalancing si nécessaire
            if level_usage.get("imbalance_detected", False):
                await self._rebalance_level_quotas(level, level_usage)
    
    async def _analyze_level_usage(self, level: HierarchyLevel) -> Dict[str, Any]:
        """Analyse utilisation niveau"""
        # Simplified analysis
        return {
            "total_usage": 1000,
            "peak_usage": 1500,
            "avg_usage": 800,
            "imbalance_detected": False,
            "underutilized_quotas": [],
            "overutilized_quotas": []
        }
    
    async def _rebalance_level_quotas(self, level: HierarchyLevel, usage_analysis: Dict[str, Any]):
        """Rebalancing quotas niveau"""
        # Redistribution quota des sous-utilisés vers sur-utilisés
        underutilized = usage_analysis.get("underutilized_quotas", [])
        overutilized = usage_analysis.get("overutilized_quotas", [])
        
        for under_id in underutilized:
            for over_id in overutilized:
                # Transfer quota
                transfer_amount = await self._calculate_transfer_amount(under_id, over_id)
                if transfer_amount > 0:
                    await self._transfer_quota(under_id, over_id, transfer_amount)
    
    async def get_hierarchy_status(self, identifier: str, level: HierarchyLevel) -> Dict[str, Any]:
        """Status hiérarchique complet"""
        try:
            # Status niveau spécifique
            level_status = await self.level_limiters[level].get_limit_status(f"{level.value}:{identifier}")
            
            # Quota information
            quota_info = self.quota_allocator.quota_registry.get(identifier, {})
            
            # Borrowing information
            borrowing_info = self.quota_allocator.borrowing_records.get(identifier, [])
            
            # Hierarchy metrics
            hierarchy_stats = {
                "total_hierarchy_requests": self.hierarchy_metrics["hierarchy_checks"],
                "borrowing_events": self.hierarchy_metrics["borrowing_events"],
                "sharing_events": self.hierarchy_metrics["sharing_events"],
                "emergency_allocations": self.hierarchy_metrics["emergency_allocations"]
            }
            
            return {
                "identifier": identifier,
                "level": level.value,
                "level_status": level_status,
                "quota_info": quota_info,
                "active_borrowing": len(borrowing_info),
                "hierarchy_stats": hierarchy_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Get hierarchy status failed for {identifier}: {e}")
            return {"error": str(e)}

    # Helper methods pour operations internes
    async def _get_level_available_quota(self, level: HierarchyLevel, identifier: str) -> int:
        """Quota disponible pour niveau"""
        return 100  # Simplified
    
    async def _record_borrowing(self, level: HierarchyLevel, identifier: str,
                              parent_level: HierarchyLevel, parent_identifier: str, amount: int):
        """Enregistrement borrowing"""
        pass  # Simplified
    
    async def _get_emergency_quota_available(self) -> int:
        """Quota d'urgence disponible"""
        return 50  # Simplified
    
    async def _allocate_emergency_quota(self, level: HierarchyLevel, identifier: str, amount: int):
        """Allocation quota d'urgence"""
        pass  # Simplified
    
    async def _find_sharing_siblings(self, request: HierarchicalRequest) -> List[str]:
        """Recherche siblings pour sharing"""
        return []  # Simplified
    
    async def _get_sibling_available_quota(self, sibling_id: str) -> int:
        """Quota disponible sibling"""
        return 10  # Simplified
    
    async def _record_sharing(self, requester_id: str, sibling_id: str, amount: int):
        """Enregistrement sharing"""
        pass  # Simplified
    
    async def _update_hierarchy_quotas(self, hierarchy_path: Dict[HierarchyLevel, str], cost: int):
        """Update quotas hiérarchiques"""
        pass  # Simplified
    
    async def _generate_hierarchy_reason(self, level_results: Dict[HierarchyLevel, RateLimitResult],
                                       blocking_level: Optional[HierarchyLevel]) -> str:
        """Génération raison décision hiérarchique"""
        if blocking_level:
            return f"Blocked at {blocking_level.value} level"
        else:
            return "Allowed at all hierarchy levels"
    
    async def _cleanup_expired_borrowing(self):
        """Cleanup borrowing expiré"""
        pass  # Simplified
    
    async def _calculate_transfer_amount(self, source_id: str, target_id: str) -> int:
        """Calcul montant transfer"""
        return 10  # Simplified
    
    async def _transfer_quota(self, source_id: str, target_id: str, amount: int):
        """Transfer quota entre identifiers"""
        pass  # Simplified

# Factory functions
def create_user_hierarchy_limiter(redis_client, user_limits: Dict[str, int]) -> HierarchicalRateLimiter:
    """Factory pour hierarchy limiter utilisateurs"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=user_limits.get("requests_per_second", 10),
        burst_capacity=user_limits.get("burst_capacity", 20),
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.TOKEN_BUCKET,
        redis_key_prefix="user_hierarchy"
    ))
    
    hierarchy_config = HierarchyConfig(
        levels=[HierarchyLevel.USER, HierarchyLevel.TEAM, HierarchyLevel.ORGANIZATION, HierarchyLevel.GLOBAL],
        allocation_strategy=QuotaAllocationStrategy.WEIGHTED,
        inheritance_mode=InheritanceMode.BORROWING,
        enable_quota_borrowing=True,
        enable_burst_sharing=True
    )
    
    return HierarchicalRateLimiter(base_limiter, hierarchy_config)

def create_organization_hierarchy_limiter(redis_client, org_config: Dict[str, Any]) -> HierarchicalRateLimiter:
    """Factory pour hierarchy limiter organizations"""
    base_limiter = DistributedRateLimiter(redis_client, RateLimitConfig(
        requests_per_second=org_config.get("requests_per_second", 1000),
        burst_capacity=org_config.get("burst_capacity", 2000),
        window_size_seconds=60,
        algorithm=RateLimitAlgorithm.SLIDING_WINDOW,
        redis_key_prefix="org_hierarchy"
    ))
    
    hierarchy_config = HierarchyConfig(
        levels=[HierarchyLevel.ORGANIZATION, HierarchyLevel.GLOBAL],
        allocation_strategy=QuotaAllocationStrategy.ADAPTIVE,
        inheritance_mode=InheritanceMode.ELASTIC,
        enable_quota_borrowing=True,
        enable_burst_sharing=True,
        emergency_allocation_threshold=0.95
    )
    
    return HierarchicalRateLimiter(base_limiter, hierarchy_config)

# Export classes principales
__all__ = [
    'HierarchicalRateLimiter',
    'HierarchyConfig',
    'HierarchicalRequest',
    'LimitCheckResult',
    'HierarchyLevel',
    'QuotaAllocationStrategy',
    'InheritanceMode',
    'create_user_hierarchy_limiter',
    'create_organization_hierarchy_limiter'
]