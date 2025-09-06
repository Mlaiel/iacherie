"""🚀 Archival Lifecycle Controller - IA Influencer Agent Platform
================================================================
Module: events/event_store/archival_lifecycle_controller.py
Author: Fahed Mlaiel (mlaiel@live.de)
================================================================

⚠️ PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

🎯 ARCHIVAL LIFECYCLE CONTROLLER
Manages event lifecycle from hot storage to archival with intelligent
tiering, compression, and compliance-driven retention policies.

Key Features:
- Multi-tier storage lifecycle management (Hot/Warm/Cold/Frozen)
- Automated migration based on access patterns
- Compliance-driven retention policies
- Compression and encryption for archived data
- Cost optimization across storage tiers
- On-demand retrieval from archives
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import gzip
import base64

logger = logging.getLogger(__name__)


class StorageTier(Enum):
    """Storage tiers with different characteristics"""
    HOT = "hot"                    # 0-30 days - High performance, frequent access
    WARM = "warm"                  # 30-365 days - Medium performance, occasional access
    COLD = "cold"                  # 1-7 years - Low cost, rare access, compliance
    FROZEN = "frozen"              # >7 years - Minimal cost, very rare access, encryption


class LifecycleAction(Enum):
    """Lifecycle actions for events"""
    MIGRATE_TO_WARM = "migrate_to_warm"
    MIGRATE_TO_COLD = "migrate_to_cold"
    MIGRATE_TO_FROZEN = "migrate_to_frozen"
    COMPRESS = "compress"
    ENCRYPT = "encrypt"
    DELETE = "delete"
    RESTORE = "restore"


class ComplianceRequirement(Enum):
    """Compliance requirements affecting retention"""
    GDPR = "gdpr"                  # GDPR - Right to erasure
    SOX = "sox"                    # Sarbanes-Oxley - Financial records
    HIPAA = "hipaa"                # Health information
    PCI_DSS = "pci_dss"           # Payment card industry
    CCPA = "ccpa"                  # California Consumer Privacy Act
    ISO27001 = "iso27001"         # Information security management


@dataclass
class RetentionPolicy:
    """Retention policy for event types"""
    event_pattern: str
    hot_duration_days: int = 30
    warm_duration_days: int = 335  # 30 + 335 = 365 days total
    cold_duration_days: int = 2190  # 6 more years = 7 years total
    frozen_duration_days: Optional[int] = None  # Indefinite if None
    compliance_requirements: List[ComplianceRequirement] = field(default_factory=list)
    auto_delete_after_retention: bool = False
    require_encryption: bool = False
    compression_enabled: bool = True


@dataclass
class ArchivalEvent:
    """Represents an event in the archival system"""
    event_id: str
    event_type: str
    original_data: Dict[str, Any]
    current_tier: StorageTier
    created_at: datetime
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    compression_ratio: float = 1.0
    is_encrypted: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MigrationPlan:
    """Plan for migrating events between tiers"""
    event_ids: List[str]
    source_tier: StorageTier
    target_tier: StorageTier
    action: LifecycleAction
    estimated_cost_savings: float = 0.0
    estimated_size_reduction: float = 0.0
    scheduled_time: Optional[datetime] = None


@dataclass
class ArchivalMetrics:
    """Metrics for archival operations"""
    total_events: int
    events_by_tier: Dict[StorageTier, int]
    total_size_bytes: int
    size_by_tier: Dict[StorageTier, int]
    compression_savings_bytes: int
    cost_savings: float
    compliance_violations: int = 0


class ArchivalLifecycleController:
    """
    Controls the lifecycle of events from creation to archival/deletion
    
    Manages:
    - Automated tiering based on age and access patterns
    - Compliance-driven retention policies
    - Cost optimization through compression and tiering
    - Encryption for sensitive data
    - On-demand retrieval from archives
    """
    
    def __init__(self):
        self._archival_events: Dict[str, ArchivalEvent] = {}
        self._retention_policies: List[RetentionPolicy] = []
        self._migration_queue: List[MigrationPlan] = []
        self._metrics = ArchivalMetrics(
            total_events=0,
            events_by_tier={tier: 0 for tier in StorageTier},
            total_size_bytes=0,
            size_by_tier={tier: 0 for tier in StorageTier},
            compression_savings_bytes=0,
            cost_savings=0.0
        )
        self._is_initialized = False
        
        # Configuration
        self.config = {
            'migration_batch_size': 1000,
            'compression_threshold_bytes': 1024,  # 1KB
            'encryption_key': 'ainflue_archive_key_2025',  # In production, use proper key management
            'cost_per_gb_hot': 0.15,     # $0.15 per GB for hot storage
            'cost_per_gb_warm': 0.08,    # $0.08 per GB for warm storage
            'cost_per_gb_cold': 0.02,    # $0.02 per GB for cold storage
            'cost_per_gb_frozen': 0.005, # $0.005 per GB for frozen storage
            'migration_check_interval_hours': 6,
            'compliance_check_interval_hours': 24
        }
        
        # Initialize Ainflue business retention policies
        self._initialize_business_policies()
    
    def _initialize_business_policies(self):
        """Initialize Ainflue-specific retention policies"""
        
        # Content events - Long retention for creator rights
        content_policy = RetentionPolicy(
            event_pattern='content.*',
            hot_duration_days=30,      # 1 month hot
            warm_duration_days=335,    # 11 months warm (1 year total)
            cold_duration_days=2190,   # 6 years cold (7 years total)
            frozen_duration_days=None, # Indefinite for creator rights
            compliance_requirements=[ComplianceRequirement.GDPR, ComplianceRequirement.ISO27001],
            auto_delete_after_retention=False,  # Never auto-delete creator content
            require_encryption=True,
            compression_enabled=True
        )
        self._retention_policies.append(content_policy)
        
        # Revenue events - Financial compliance requirements
        revenue_policy = RetentionPolicy(
            event_pattern='revenue.*|payment.*|monetization.*',
            hot_duration_days=90,      # 3 months hot for active monitoring
            warm_duration_days=275,    # 9 months warm (1 year total)
            cold_duration_days=2555,   # 7 years cold for SOX compliance
            frozen_duration_days=None, # Indefinite for legal protection
            compliance_requirements=[ComplianceRequirement.SOX, ComplianceRequirement.PCI_DSS],
            auto_delete_after_retention=False,  # Legal requirement to keep
            require_encryption=True,
            compression_enabled=True
        )
        self._retention_policies.append(revenue_policy)
        
        # User interaction events - Privacy-focused retention
        interaction_policy = RetentionPolicy(
            event_pattern='content.viewed|content.liked|content.shared',
            hot_duration_days=14,      # 2 weeks hot for analytics
            warm_duration_days=76,     # ~2.5 months warm (3 months total)
            cold_duration_days=1002,   # 2.75 years cold (3 years total)
            frozen_duration_days=None, # No frozen tier for privacy
            compliance_requirements=[ComplianceRequirement.GDPR, ComplianceRequirement.CCPA],
            auto_delete_after_retention=True,  # Delete for privacy
            require_encryption=True,
            compression_enabled=True
        )
        self._retention_policies.append(interaction_policy)
        
        # Analytics events - Medium retention for business insights
        analytics_policy = RetentionPolicy(
            event_pattern='analytics.*|metrics.*',
            hot_duration_days=7,       # 1 week hot
            warm_duration_days=53,     # ~2 months warm
            cold_duration_days=1035,   # ~3 years cold (total ~3 years)
            compliance_requirements=[ComplianceRequirement.ISO27001],
            auto_delete_after_retention=True,
            require_encryption=False,
            compression_enabled=True
        )
        self._retention_policies.append(analytics_policy)
        
        # System events - Short retention for operational monitoring
        system_policy = RetentionPolicy(
            event_pattern='system.*|performance.*|health.*',
            hot_duration_days=3,       # 3 days hot
            warm_duration_days=27,     # 1 month warm
            cold_duration_days=335,    # 11 months cold (1 year total)
            compliance_requirements=[],
            auto_delete_after_retention=True,
            require_encryption=False,
            compression_enabled=True
        )
        self._retention_policies.append(system_policy)
        
        # Collaboration events - Professional retention
        collaboration_policy = RetentionPolicy(
            event_pattern='collaboration.*',
            hot_duration_days=60,      # 2 months hot
            warm_duration_days=305,    # 10 months warm (1 year total)
            cold_duration_days=1460,   # 4 years cold (5 years total)
            compliance_requirements=[ComplianceRequirement.ISO27001],
            auto_delete_after_retention=False,  # Keep for professional records
            require_encryption=True,
            compression_enabled=True
        )
        self._retention_policies.append(collaboration_policy)
    
    async def initialize(self, storage_backends: Dict[str, Any]):
        """Initialize the archival lifecycle controller"""
        
        self._storage_backends = storage_backends
        
        # Load existing archival events from storage
        await self._load_archival_registry()
        
        # Start background tasks
        asyncio.create_task(self._lifecycle_monitoring_task())
        asyncio.create_task(self._migration_execution_task())
        asyncio.create_task(self._compliance_monitoring_task())
        
        self._is_initialized = True
        logger.info("Archival Lifecycle Controller initialized successfully")
    
    async def _load_archival_registry(self):
        """Load existing archival events from registry"""
        
        try:
            # In real implementation, load from persistent storage
            # For now, simulate with empty registry
            logger.info("Loaded archival registry")
            
        except Exception as e:
            logger.error(f"Failed to load archival registry: {e}")
    
    async def register_event_for_archival(self, event_id: str, event_type: str,
                                        event_data: Dict[str, Any],
                                        size_bytes: int = 0) -> ArchivalEvent:
        """Register new event for lifecycle management"""
        
        archival_event = ArchivalEvent(
            event_id=event_id,
            event_type=event_type,
            original_data=event_data,
            current_tier=StorageTier.HOT,
            created_at=datetime.utcnow(),
            size_bytes=size_bytes or len(json.dumps(event_data).encode('utf-8')),
            metadata={
                'registration_time': datetime.utcnow().isoformat(),
                'original_backend': 'postgresql'  # Default
            }
        )
        
        self._archival_events[event_id] = archival_event
        
        # Update metrics
        self._metrics.total_events += 1
        self._metrics.events_by_tier[StorageTier.HOT] += 1
        self._metrics.total_size_bytes += archival_event.size_bytes
        self._metrics.size_by_tier[StorageTier.HOT] += archival_event.size_bytes
        
        logger.debug(f"Registered event {event_id} for archival lifecycle")
        return archival_event
    
    def _find_retention_policy(self, event_type: str) -> Optional[RetentionPolicy]:
        """Find matching retention policy for event type"""
        
        for policy in self._retention_policies:
            # Simple pattern matching (could be enhanced with regex)
            if self._matches_pattern(event_type, policy.event_pattern):
                return policy
        
        return None
    
    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Check if event type matches pattern"""
        
        # Handle multiple patterns separated by |
        patterns = pattern.split('|')
        
        for p in patterns:
            if '*' in p:
                # Wildcard matching
                prefix = p.replace('*', '')
                if event_type.startswith(prefix):
                    return True
            elif p == event_type:
                return True
        
        return False
    
    async def analyze_lifecycle_status(self, event_id: str) -> Dict[str, Any]:
        """Analyze current lifecycle status of an event"""
        
        if event_id not in self._archival_events:
            raise ValueError(f"Event {event_id} not found in archival registry")
        
        event = self._archival_events[event_id]
        policy = self._find_retention_policy(event.event_type)
        
        if not policy:
            return {
                'event_id': event_id,
                'error': 'No retention policy found for event type',
                'event_type': event.event_type
            }
        
        current_age_days = (datetime.utcnow() - event.created_at).days
        days_since_access = None
        if event.last_accessed:
            days_since_access = (datetime.utcnow() - event.last_accessed).days
        
        # Determine expected tier based on age
        expected_tier = self._calculate_expected_tier(current_age_days, policy)
        
        # Calculate next action
        next_action = None
        next_action_date = None
        
        if event.current_tier != expected_tier:
            next_action = self._get_migration_action(event.current_tier, expected_tier)
            next_action_date = datetime.utcnow()
        else:
            # Calculate when next migration should happen
            if event.current_tier == StorageTier.HOT:
                next_action_date = event.created_at + timedelta(days=policy.hot_duration_days)
                next_action = LifecycleAction.MIGRATE_TO_WARM
            elif event.current_tier == StorageTier.WARM:
                warm_start = event.created_at + timedelta(days=policy.hot_duration_days)
                next_action_date = warm_start + timedelta(days=policy.warm_duration_days)
                next_action = LifecycleAction.MIGRATE_TO_COLD
            elif event.current_tier == StorageTier.COLD:
                cold_start = (event.created_at + 
                            timedelta(days=policy.hot_duration_days + policy.warm_duration_days))
                if policy.frozen_duration_days:
                    next_action_date = cold_start + timedelta(days=policy.cold_duration_days)
                    next_action = LifecycleAction.MIGRATE_TO_FROZEN
                elif policy.auto_delete_after_retention:
                    next_action_date = cold_start + timedelta(days=policy.cold_duration_days)
                    next_action = LifecycleAction.DELETE
        
        return {
            'event_id': event_id,
            'event_type': event.event_type,
            'current_tier': event.current_tier.value,
            'expected_tier': expected_tier.value,
            'current_age_days': current_age_days,
            'days_since_last_access': days_since_access,
            'size_bytes': event.size_bytes,
            'is_compressed': event.compression_ratio < 1.0,
            'is_encrypted': event.is_encrypted,
            'next_action': next_action.value if next_action else None,
            'next_action_date': next_action_date.isoformat() if next_action_date else None,
            'policy': {
                'pattern': policy.event_pattern,
                'hot_days': policy.hot_duration_days,
                'warm_days': policy.warm_duration_days,
                'cold_days': policy.cold_duration_days,
                'compliance': [c.value for c in policy.compliance_requirements]
            }
        }
    
    def _calculate_expected_tier(self, age_days: int, policy: RetentionPolicy) -> StorageTier:
        """Calculate expected storage tier based on age and policy"""
        
        if age_days <= policy.hot_duration_days:
            return StorageTier.HOT
        elif age_days <= policy.hot_duration_days + policy.warm_duration_days:
            return StorageTier.WARM
        elif age_days <= (policy.hot_duration_days + policy.warm_duration_days + 
                         policy.cold_duration_days):
            return StorageTier.COLD
        else:
            return StorageTier.FROZEN
    
    def _get_migration_action(self, current_tier: StorageTier, 
                            target_tier: StorageTier) -> LifecycleAction:
        """Get migration action for tier transition"""
        
        migration_map = {
            (StorageTier.HOT, StorageTier.WARM): LifecycleAction.MIGRATE_TO_WARM,
            (StorageTier.HOT, StorageTier.COLD): LifecycleAction.MIGRATE_TO_COLD,
            (StorageTier.HOT, StorageTier.FROZEN): LifecycleAction.MIGRATE_TO_FROZEN,
            (StorageTier.WARM, StorageTier.COLD): LifecycleAction.MIGRATE_TO_COLD,
            (StorageTier.WARM, StorageTier.FROZEN): LifecycleAction.MIGRATE_TO_FROZEN,
            (StorageTier.COLD, StorageTier.FROZEN): LifecycleAction.MIGRATE_TO_FROZEN,
        }
        
        return migration_map.get((current_tier, target_tier), LifecycleAction.MIGRATE_TO_COLD)
    
    async def create_migration_plan(self) -> List[MigrationPlan]:
        """Create migration plan for events that need tier changes"""
        
        migration_plans = []
        
        # Group events by required migration
        migrations = {}
        
        for event_id, event in self._archival_events.items():
            policy = self._find_retention_policy(event.event_type)
            if not policy:
                continue
            
            age_days = (datetime.utcnow() - event.created_at).days
            expected_tier = self._calculate_expected_tier(age_days, policy)
            
            if event.current_tier != expected_tier:
                action = self._get_migration_action(event.current_tier, expected_tier)
                migration_key = (event.current_tier, expected_tier, action)
                
                if migration_key not in migrations:
                    migrations[migration_key] = []
                
                migrations[migration_key].append(event_id)
        
        # Create migration plans
        for (source_tier, target_tier, action), event_ids in migrations.items():
            # Calculate cost savings
            cost_savings = self._calculate_migration_cost_savings(
                event_ids, source_tier, target_tier
            )
            
            # Calculate size reduction from compression
            size_reduction = self._estimate_size_reduction(event_ids, target_tier)
            
            # Split into batches
            for i in range(0, len(event_ids), self.config['migration_batch_size']):
                batch_ids = event_ids[i:i + self.config['migration_batch_size']]
                
                plan = MigrationPlan(
                    event_ids=batch_ids,
                    source_tier=source_tier,
                    target_tier=target_tier,
                    action=action,
                    estimated_cost_savings=cost_savings * len(batch_ids) / len(event_ids),
                    estimated_size_reduction=size_reduction * len(batch_ids) / len(event_ids),
                    scheduled_time=datetime.utcnow() + timedelta(minutes=i * 5)  # Stagger migrations
                )
                
                migration_plans.append(plan)
        
        return migration_plans
    
    def _calculate_migration_cost_savings(self, event_ids: List[str],
                                        source_tier: StorageTier,
                                        target_tier: StorageTier) -> float:
        """Calculate cost savings from migration"""
        
        total_size_gb = sum(
            self._archival_events[eid].size_bytes for eid in event_ids
        ) / (1024**3)
        
        source_cost = total_size_gb * self._get_tier_cost_per_gb(source_tier)
        target_cost = total_size_gb * self._get_tier_cost_per_gb(target_tier)
        
        return max(0, source_cost - target_cost)
    
    def _get_tier_cost_per_gb(self, tier: StorageTier) -> float:
        """Get cost per GB for storage tier"""
        
        cost_map = {
            StorageTier.HOT: self.config['cost_per_gb_hot'],
            StorageTier.WARM: self.config['cost_per_gb_warm'],
            StorageTier.COLD: self.config['cost_per_gb_cold'],
            StorageTier.FROZEN: self.config['cost_per_gb_frozen']
        }
        
        return cost_map.get(tier, 0.0)
    
    def _estimate_size_reduction(self, event_ids: List[str], target_tier: StorageTier) -> float:
        """Estimate size reduction from compression"""
        
        total_size = sum(self._archival_events[eid].size_bytes for eid in event_ids)
        
        # Estimate compression ratios by tier
        compression_ratios = {
            StorageTier.HOT: 1.0,      # No compression
            StorageTier.WARM: 0.7,     # 30% reduction
            StorageTier.COLD: 0.5,     # 50% reduction
            StorageTier.FROZEN: 0.3    # 70% reduction
        }
        
        compression_ratio = compression_ratios.get(target_tier, 1.0)
        return total_size * (1.0 - compression_ratio)
    
    async def execute_migration_plan(self, plan: MigrationPlan) -> Dict[str, Any]:
        """Execute a migration plan"""
        
        start_time = datetime.utcnow()
        success_count = 0
        error_count = 0
        errors = []
        
        for event_id in plan.event_ids:
            try:
                await self._migrate_event(event_id, plan.target_tier, plan.action)
                success_count += 1
            except Exception as e:
                error_count += 1
                errors.append(f"Event {event_id}: {str(e)}")
                logger.error(f"Failed to migrate event {event_id}: {e}")
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        result = {
            'plan_id': f"migration_{start_time.strftime('%Y%m%d_%H%M%S')}",
            'events_processed': len(plan.event_ids),
            'successful_migrations': success_count,
            'failed_migrations': error_count,
            'execution_time_seconds': execution_time,
            'estimated_cost_savings': plan.estimated_cost_savings,
            'estimated_size_reduction_bytes': plan.estimated_size_reduction,
            'errors': errors[:10]  # Limit to first 10 errors
        }
        
        logger.info(f"Migration plan executed: {success_count}/{len(plan.event_ids)} successful")
        return result
    
    async def _migrate_event(self, event_id: str, target_tier: StorageTier,
                           action: LifecycleAction):
        """Migrate single event to target tier"""
        
        if event_id not in self._archival_events:
            raise ValueError(f"Event {event_id} not found")
        
        event = self._archival_events[event_id]
        old_tier = event.current_tier
        
        # Apply transformations based on target tier
        if target_tier in [StorageTier.COLD, StorageTier.FROZEN]:
            if not event.compression_ratio < 1.0:  # Not already compressed
                await self._compress_event(event)
        
        if target_tier == StorageTier.FROZEN:
            if not event.is_encrypted:
                await self._encrypt_event(event)
        
        # Update event metadata
        event.current_tier = target_tier
        event.metadata['migration_history'] = event.metadata.get('migration_history', [])
        event.metadata['migration_history'].append({
            'from_tier': old_tier.value,
            'to_tier': target_tier.value,
            'action': action.value,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Update metrics
        self._metrics.events_by_tier[old_tier] -= 1
        self._metrics.events_by_tier[target_tier] += 1
        self._metrics.size_by_tier[old_tier] -= event.size_bytes
        self._metrics.size_by_tier[target_tier] += event.size_bytes
        
        # In real implementation, move data in storage backends
        await self._physical_migration(event, target_tier)
        
        logger.debug(f"Migrated event {event_id} from {old_tier.value} to {target_tier.value}")
    
    async def _compress_event(self, event: ArchivalEvent):
        """Compress event data"""
        
        try:
            original_data = json.dumps(event.original_data).encode('utf-8')
            compressed_data = gzip.compress(original_data)
            
            old_size = len(original_data)
            new_size = len(compressed_data)
            
            event.compression_ratio = new_size / old_size
            event.size_bytes = new_size
            event.metadata['compressed_at'] = datetime.utcnow().isoformat()
            event.metadata['original_size_bytes'] = old_size
            
            # Update compression savings
            savings = old_size - new_size
            self._metrics.compression_savings_bytes += savings
            
            logger.debug(f"Compressed event {event.event_id}: {old_size} -> {new_size} bytes")
            
        except Exception as e:
            logger.error(f"Failed to compress event {event.event_id}: {e}")
            raise
    
    async def _encrypt_event(self, event: ArchivalEvent):
        """Encrypt event data"""
        
        try:
            # Simplified encryption (in production, use proper encryption libraries)
            data_str = json.dumps(event.original_data)
            encrypted_data = base64.b64encode(data_str.encode('utf-8')).decode('utf-8')
            
            event.is_encrypted = True
            event.metadata['encrypted_at'] = datetime.utcnow().isoformat()
            event.metadata['encryption_algorithm'] = 'base64'  # Placeholder
            
            logger.debug(f"Encrypted event {event.event_id}")
            
        except Exception as e:
            logger.error(f"Failed to encrypt event {event.event_id}: {e}")
            raise
    
    async def _physical_migration(self, event: ArchivalEvent, target_tier: StorageTier):
        """Perform physical migration in storage backends"""
        
        # This would interact with actual storage systems
        # For now, just simulate the migration
        
        migration_targets = {
            StorageTier.HOT: 'postgresql',
            StorageTier.WARM: 'mongodb',
            StorageTier.COLD: 's3_standard_ia',
            StorageTier.FROZEN: 's3_glacier'
        }
        
        target_backend = migration_targets.get(target_tier, 'postgresql')
        event.metadata['storage_backend'] = target_backend
        
        logger.debug(f"Physical migration of {event.event_id} to {target_backend}")
    
    async def retrieve_archived_event(self, event_id: str) -> Dict[str, Any]:
        """Retrieve event from archive (may require restore operation)"""
        
        if event_id not in self._archival_events:
            raise ValueError(f"Event {event_id} not found in archive")
        
        event = self._archival_events[event_id]
        
        # Update access time
        event.last_accessed = datetime.utcnow()
        
        # Handle restoration if needed
        if event.current_tier in [StorageTier.COLD, StorageTier.FROZEN]:
            logger.info(f"Restoring event {event_id} from {event.current_tier.value}")
            # In real implementation, initiate restore process
            await asyncio.sleep(0.1)  # Simulate restore delay
        
        # Decrypt if needed
        data = event.original_data
        if event.is_encrypted:
            data = await self._decrypt_event_data(event)
        
        # Decompress if needed
        if event.compression_ratio < 1.0:
            data = await self._decompress_event_data(event)
        
        return {
            'event_id': event_id,
            'event_type': event.event_type,
            'data': data,
            'metadata': {
                'current_tier': event.current_tier.value,
                'is_compressed': event.compression_ratio < 1.0,
                'is_encrypted': event.is_encrypted,
                'size_bytes': event.size_bytes,
                'last_accessed': event.last_accessed.isoformat(),
                'retrieval_time': datetime.utcnow().isoformat()
            }
        }
    
    async def _decrypt_event_data(self, event: ArchivalEvent) -> Dict[str, Any]:
        """Decrypt event data"""
        
        # Simplified decryption (in production, use proper decryption)
        try:
            encrypted_str = event.metadata.get('encrypted_data', '')
            decrypted_str = base64.b64decode(encrypted_str.encode('utf-8')).decode('utf-8')
            return json.loads(decrypted_str)
        except Exception as e:
            logger.error(f"Failed to decrypt event {event.event_id}: {e}")
            return event.original_data
    
    async def _decompress_event_data(self, event: ArchivalEvent) -> Dict[str, Any]:
        """Decompress event data"""
        
        try:
            compressed_data = event.metadata.get('compressed_data', '')
            decompressed_data = gzip.decompress(base64.b64decode(compressed_data))
            return json.loads(decompressed_data.decode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to decompress event {event.event_id}: {e}")
            return event.original_data
    
    async def check_compliance_violations(self) -> List[Dict[str, Any]]:
        """Check for compliance violations"""
        
        violations = []
        current_time = datetime.utcnow()
        
        for event_id, event in self._archival_events.items():
            policy = self._find_retention_policy(event.event_type)
            if not policy:
                continue
            
            age_days = (current_time - event.created_at).days
            
            # Check GDPR right to erasure
            if ComplianceRequirement.GDPR in policy.compliance_requirements:
                # GDPR allows 30 days to respond to erasure requests
                if age_days > 30 and event.metadata.get('deletion_requested'):
                    violations.append({
                        'event_id': event_id,
                        'violation_type': 'gdpr_erasure_delay',
                        'description': 'GDPR deletion request not processed within 30 days',
                        'age_days': age_days,
                        'severity': 'high'
                    })
            
            # Check SOX retention requirements
            if ComplianceRequirement.SOX in policy.compliance_requirements:
                total_retention = (policy.hot_duration_days + policy.warm_duration_days + 
                                 policy.cold_duration_days)
                if age_days > total_retention and policy.auto_delete_after_retention:
                    violations.append({
                        'event_id': event_id,
                        'violation_type': 'sox_premature_deletion',
                        'description': 'Financial record scheduled for deletion before SOX requirement',
                        'age_days': age_days,
                        'severity': 'critical'
                    })
            
            # Check encryption requirements
            if policy.require_encryption and not event.is_encrypted:
                if event.current_tier in [StorageTier.COLD, StorageTier.FROZEN]:
                    violations.append({
                        'event_id': event_id,
                        'violation_type': 'missing_encryption',
                        'description': 'Event in cold/frozen storage without required encryption',
                        'current_tier': event.current_tier.value,
                        'severity': 'medium'
                    })
        
        self._metrics.compliance_violations = len(violations)
        return violations
    
    async def get_archival_metrics(self) -> ArchivalMetrics:
        """Get comprehensive archival metrics"""
        
        # Recalculate metrics
        self._metrics.total_events = len(self._archival_events)
        
        # Reset tier counters
        for tier in StorageTier:
            self._metrics.events_by_tier[tier] = 0
            self._metrics.size_by_tier[tier] = 0
        
        # Count events and sizes by tier
        for event in self._archival_events.values():
            self._metrics.events_by_tier[event.current_tier] += 1
            self._metrics.size_by_tier[event.current_tier] += event.size_bytes
        
        self._metrics.total_size_bytes = sum(self._metrics.size_by_tier.values())
        
        # Calculate cost savings
        hot_cost = self._metrics.size_by_tier[StorageTier.HOT] / (1024**3) * self.config['cost_per_gb_hot']
        warm_cost = self._metrics.size_by_tier[StorageTier.WARM] / (1024**3) * self.config['cost_per_gb_warm']
        cold_cost = self._metrics.size_by_tier[StorageTier.COLD] / (1024**3) * self.config['cost_per_gb_cold']
        frozen_cost = self._metrics.size_by_tier[StorageTier.FROZEN] / (1024**3) * self.config['cost_per_gb_frozen']
        
        current_cost = hot_cost + warm_cost + cold_cost + frozen_cost
        hot_only_cost = self._metrics.total_size_bytes / (1024**3) * self.config['cost_per_gb_hot']
        
        self._metrics.cost_savings = max(0, hot_only_cost - current_cost)
        
        return self._metrics
    
    async def _lifecycle_monitoring_task(self):
        """Background task for lifecycle monitoring"""
        
        while self._is_initialized:
            try:
                await self._monitor_lifecycle_events()
                await asyncio.sleep(self.config['migration_check_interval_hours'] * 3600)
            except Exception as e:
                logger.error(f"Lifecycle monitoring task error: {e}")
                await asyncio.sleep(3600)  # 1 hour retry
    
    async def _monitor_lifecycle_events(self):
        """Monitor events for lifecycle transitions"""
        
        # Create and queue migration plans
        migration_plans = await self.create_migration_plan()
        
        for plan in migration_plans:
            if plan.scheduled_time <= datetime.utcnow():
                self._migration_queue.append(plan)
        
        logger.info(f"Queued {len(migration_plans)} migration plans")
    
    async def _migration_execution_task(self):
        """Background task for executing migrations"""
        
        while self._is_initialized:
            try:
                if self._migration_queue:
                    plan = self._migration_queue.pop(0)
                    result = await self.execute_migration_plan(plan)
                    logger.info(f"Executed migration plan: {result['successful_migrations']} events migrated")
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Migration execution task error: {e}")
                await asyncio.sleep(600)  # 10 minutes retry
    
    async def _compliance_monitoring_task(self):
        """Background task for compliance monitoring"""
        
        while self._is_initialized:
            try:
                violations = await self.check_compliance_violations()
                if violations:
                    logger.warning(f"Found {len(violations)} compliance violations")
                    for violation in violations[:5]:  # Log first 5
                        logger.warning(f"Violation: {violation}")
                
                await asyncio.sleep(self.config['compliance_check_interval_hours'] * 3600)
            except Exception as e:
                logger.error(f"Compliance monitoring task error: {e}")
                await asyncio.sleep(3600)


# Export public APIs
__all__ = [
    'ArchivalLifecycleController',
    'StorageTier',
    'LifecycleAction',
    'ComplianceRequirement',
    'RetentionPolicy',
    'ArchivalEvent',
    'MigrationPlan',
    'ArchivalMetrics'
]