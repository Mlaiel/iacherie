"""Retention Engine - Enterprise Content Retention Management

Provides comprehensive retention policy management, automated
lifecycle enforcement, and compliance-driven content lifecycle
management for legal and business requirements.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL / LEGAL WARNING ⚠️
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
This code is the exclusive intellectual property of Fahed Mlaiel.
Toute utilisation non autorisée est strictement interdite.
Any unauthorized use is strictly prohibited.
"""import asyncio
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
import schedule
from pathlib import Path

from .models import ArchiveEntry
from ..exceptions import RetentionPolicyViolationError


class RetentionAction(Enum):
    """Retention action enumeration"""    KEEP = "keep"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    MIGRATE = "migrate"
    DELETE = "delete"
    LEGAL_HOLD = "legal_hold"
    REVIEW_REQUIRED = "review_required"


@dataclass
class RetentionPolicy:
    """Comprehensive retention policy definition"""    policy_id: str
    name: str
    description: str
    
    # Content scope
    content_types: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    creator_ids: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    
    # Time-based rules
    minimum_retention_days: int = 0
    maximum_retention_days: Optional[int] = None
    legal_hold_days: Optional[int] = None
    
    # Action schedules
    action_schedule: Dict[int, RetentionAction] = field(default_factory=dict)  # days -> action
    
    # Compliance settings
    regulatory_framework: Optional[str] = None  # GDPR, CCPA, SOX, etc.
    compliance_requirements: Set[str] = field(default_factory=set)
    audit_required: bool = False
    
    # Business rules
    business_value_threshold: float = 0.0  # 0-1 scale
    access_frequency_threshold: int = 0  # accesses per period
    storage_cost_limit: float = 0.0  # cost per GB per month
    
    # Advanced conditions
    conditions: Dict[str, Any] = field(default_factory=dict)
    exceptions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    created_by: str = ""
    priority: int = 5  # 1-10, higher = more important
    enabled: bool = True


@dataclass
class RetentionSchedule:
    """Retention schedule for content"""    content_id: str
    archive_id: str
    policy_id: str
    
    scheduled_actions: Dict[datetime, RetentionAction] = field(default_factory=dict)
    completed_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    next_action_date: Optional[datetime] = None
    next_action: Optional[RetentionAction] = None
    
    legal_hold_until: Optional[datetime] = None
    deletion_eligible_date: Optional[datetime] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class RetentionScheduler:
    """Automated retention action scheduler"""    
    def __init__(self, retention_engine):
        self.retention_engine = retention_engine
        self.logger = logging.getLogger("retention.scheduler")
        self.running = False
        self.schedule_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the retention scheduler"""        if self.running:
            return
        
        self.running = True
        self.schedule_task = asyncio.create_task(self._scheduler_loop())
        self.logger.info("Retention scheduler started")
    
    async def stop(self):
        """Stop the retention scheduler"""        if not self.running:
            return
        
        self.running = False
        if self.schedule_task:
            self.schedule_task.cancel()
            try:
                await self.schedule_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Retention scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""        while self.running:
            try:
                await self._process_scheduled_actions()
                await asyncio.sleep(3600)  # Check every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _process_scheduled_actions(self):
        """Process all scheduled retention actions"""        current_time = datetime.utcnow()
        due_actions = await self.retention_engine.get_due_actions(current_time)
        
        for action in due_actions:
            try:
                await self.retention_engine.execute_retention_action(
                    action["content_id"],
                    action["action"],
                    action["policy_id"]
                )
            except Exception as e:
                self.logger.error(f"Failed to execute retention action: {e}")


class RetentionEngine:
    """    Enterprise retention engine with policy-driven content lifecycle
    management, compliance enforcement, and automated retention actions
    """    
    def __init__(self, database_path: Optional[str] = None):
        self.database_path = database_path or "/var/data/retention/retention.db"
        self.logger = logging.getLogger("retention.engine")
        
        # Policy storage
        self.policies: Dict[str, RetentionPolicy] = {}
        self.content_schedules: Dict[str, RetentionSchedule] = {}
        
        # Action callbacks
        self.action_handlers: Dict[RetentionAction, Callable] = {}
        
        # Statistics
        self.stats = {
            "policies_registered": 0,
            "content_registered": 0,
            "actions_executed": 0,
            "violations_detected": 0,
            "legal_holds_active": 0
        }
        
        # Initialize database
        self._init_database()
        
        # Initialize scheduler
        self.scheduler = RetentionScheduler(self)
        
        # Load default policies
        self._initialize_default_policies()
    
    def _init_database(self):
        """Initialize retention database"""        Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""                CREATE TABLE IF NOT EXISTS retention_policies (
                    policy_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    content_types TEXT DEFAULT '[]',
                    content_categories TEXT DEFAULT '[]',
                    creator_ids TEXT DEFAULT '[]',
                    tags TEXT DEFAULT '[]',
                    minimum_retention_days INTEGER DEFAULT 0,
                    maximum_retention_days INTEGER,
                    legal_hold_days INTEGER,
                    action_schedule TEXT DEFAULT '{}',
                    regulatory_framework TEXT,
                    compliance_requirements TEXT DEFAULT '[]',
                    audit_required BOOLEAN DEFAULT FALSE,
                    business_value_threshold REAL DEFAULT 0.0,
                    access_frequency_threshold INTEGER DEFAULT 0,
                    storage_cost_limit REAL DEFAULT 0.0,
                    conditions TEXT DEFAULT '{}',
                    exceptions TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    created_by TEXT DEFAULT '',
                    priority INTEGER DEFAULT 5,
                    enabled BOOLEAN DEFAULT TRUE
                )
            """)
            
            conn.execute("""                CREATE TABLE IF NOT EXISTS content_schedules (
                    content_id TEXT PRIMARY KEY,
                    archive_id TEXT NOT NULL,
                    policy_id TEXT NOT NULL,
                    scheduled_actions TEXT DEFAULT '{}',
                    completed_actions TEXT DEFAULT '[]',
                    next_action_date TEXT,
                    next_action TEXT,
                    legal_hold_until TEXT,
                    deletion_eligible_date TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT,
                    FOREIGN KEY (policy_id) REFERENCES retention_policies (policy_id)
                )
            """)
            
            conn.execute("""                CREATE TABLE IF NOT EXISTS retention_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    policy_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT DEFAULT '{}',
                    executed_at TEXT NOT NULL,
                    executed_by TEXT DEFAULT 'system'
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_schedules_policy ON content_schedules(policy_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_schedules_next_action ON content_schedules(next_action_date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_content ON retention_audit_log(content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_executed ON retention_audit_log(executed_at)")
            
            conn.commit()
    
    def _initialize_default_policies(self):
        """Initialize default retention policies"""        
        # GDPR compliance policy
        gdpr_policy = RetentionPolicy(
            policy_id="gdpr_standard",
            name="GDPR Standard Retention",
            description="Standard GDPR compliance retention policy",
            content_types=["all"],
            minimum_retention_days=30,
            maximum_retention_days=2555,  # 7 years
            action_schedule={
                0: RetentionAction.KEEP,
                30: RetentionAction.ARCHIVE,
                365: RetentionAction.MIGRATE,
                2555: RetentionAction.DELETE
            },
            regulatory_framework="GDPR",
            compliance_requirements={"data_protection", "right_to_erasure"},
            audit_required=True,
            priority=9
        )
        
        # Financial records policy (SOX compliance)
        financial_policy = RetentionPolicy(
            policy_id="financial_sox",
            name="Financial Records (SOX)",
            description="Financial records retention for SOX compliance",
            content_categories=["financial", "revenue", "transaction"],
            minimum_retention_days=2555,  # 7 years
            maximum_retention_days=3650,  # 10 years
            action_schedule={
                0: RetentionAction.LEGAL_HOLD,
                30: RetentionAction.ARCHIVE,
                90: RetentionAction.MIGRATE,
                3650: RetentionAction.REVIEW_REQUIRED
            },
            regulatory_framework="SOX",
            compliance_requirements={"financial_records", "audit_trail"},
            audit_required=True,
            priority=10
        )
        
        # Content protection policy (Critical for fingerprints)
        protection_policy = RetentionPolicy(
            policy_id="content_protection_critical",
            name="Content Protection Critical",
            description="Critical retention for content protection data",
            content_categories=["fingerprint", "protection", "copyright"],
            tags={"fingerprint", "protection", "critical"},
            minimum_retention_days=3650,  # 10 years
            legal_hold_days=3650,
            action_schedule={
                0: RetentionAction.LEGAL_HOLD,
                1: RetentionAction.ARCHIVE,
                30: RetentionAction.MIGRATE,
                # Never delete - permanent retention for legal purposes
            },
            regulatory_framework="COPYRIGHT",
            compliance_requirements={"copyright_protection", "legal_evidence"},
            audit_required=True,
            business_value_threshold=1.0,
            priority=10
        )
        
        # Media content policy
        media_policy = RetentionPolicy(
            policy_id="media_content_standard",
            name="Media Content Standard",
            description="Standard retention for media content",
            content_types=["audio/*", "video/*", "image/*"],
            content_categories=["music", "video", "image", "media"],
            minimum_retention_days=365,
            maximum_retention_days=2555,
            action_schedule={
                0: RetentionAction.KEEP,
                7: RetentionAction.COMPRESS,
                30: RetentionAction.ARCHIVE,
                365: RetentionAction.MIGRATE,
                2555: RetentionAction.DELETE
            },
            business_value_threshold=0.3,
            access_frequency_threshold=5,
            priority=7
        )
        
        # Temporary content policy
        temp_policy = RetentionPolicy(
            policy_id="temporary_content",
            name="Temporary Content",
            description="Short-term retention for temporary content",
            content_categories=["temp", "cache", "processing"],
            tags={"temporary"},
            minimum_retention_days=1,
            maximum_retention_days=30,
            action_schedule={
                0: RetentionAction.KEEP,
                7: RetentionAction.COMPRESS,
                30: RetentionAction.DELETE
            },
            priority=3
        )
        
        # Register all policies
        policies = [gdpr_policy, financial_policy, protection_policy, media_policy, temp_policy]
        for policy in policies:
            self.register_policy(policy)
    
    def register_policy(self, policy: RetentionPolicy):
        """Register a retention policy"""        self.policies[policy.policy_id] = policy
        
        # Store in database
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""                INSERT OR REPLACE INTO retention_policies (
                    policy_id, name, description, content_types, content_categories,
                    creator_ids, tags, minimum_retention_days, maximum_retention_days,
                    legal_hold_days, action_schedule, regulatory_framework,
                    compliance_requirements, audit_required, business_value_threshold,
                    access_frequency_threshold, storage_cost_limit, conditions,
                    exceptions, created_at, updated_at, created_by, priority, enabled
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                policy.policy_id, policy.name, policy.description,
                json.dumps(policy.content_types), json.dumps(policy.content_categories),
                json.dumps(policy.creator_ids), json.dumps(list(policy.tags)),
                policy.minimum_retention_days, policy.maximum_retention_days,
                policy.legal_hold_days,
                json.dumps({str(k): v.value for k, v in policy.action_schedule.items()}),
                policy.regulatory_framework, json.dumps(list(policy.compliance_requirements)),
                policy.audit_required, policy.business_value_threshold,
                policy.access_frequency_threshold, policy.storage_cost_limit,
                json.dumps(policy.conditions), json.dumps(policy.exceptions),
                policy.created_at.isoformat(), 
                policy.updated_at.isoformat() if policy.updated_at else None,
                policy.created_by, policy.priority, policy.enabled
            ))
            conn.commit()
        
        self.stats["policies_registered"] += 1
        self.logger.info(f"Registered retention policy: {policy.policy_id}")
    
    def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get retention policy by ID"""        return self.policies.get(policy_id)
    
    def find_applicable_policy(
        self,
        content_type: str,
        content_category: str = None,
        creator_id: str = None,
        tags: Set[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[RetentionPolicy]:
        """Find the most applicable retention policy"""        
        matching_policies = []
        tags = tags or set()
        metadata = metadata or {}
        
        for policy in self.policies.values():
            if not policy.enabled:
                continue
            
            score = 0
            
            # Content type matching
            if policy.content_types:
                if "all" in policy.content_types or any(
                    content_type.startswith(ct.rstrip('*')) for ct in policy.content_types
                ):
                    score += 10
            
            # Content category matching
            if policy.content_categories and content_category:
                if content_category in policy.content_categories:
                    score += 8
            
            # Creator ID matching
            if policy.creator_ids and creator_id:
                if creator_id in policy.creator_ids:
                    score += 6
            
            # Tags matching
            if policy.tags and tags:
                tag_overlap = len(policy.tags.intersection(tags))
                if tag_overlap > 0:
                    score += tag_overlap * 4
            
            # Business conditions
            if policy.conditions:
                if self._evaluate_conditions(policy.conditions, metadata):
                    score += 5
            
            if score > 0:
                matching_policies.append((policy, score))
        
        if matching_policies:
            # Sort by score (descending) and priority (descending)
            matching_policies.sort(key=lambda x: (x[1], x[0].priority), reverse=True)
            return matching_policies[0][0]
        
        return None
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Evaluate policy conditions against content metadata"""        # Simplified condition evaluation
        # In a real implementation, this would support complex boolean logic
        for key, expected_value in conditions.items():
            if key in metadata:
                if metadata[key] != expected_value:
                    return False
        return True
    
    async def register_content(
        self,
        archive_entry: ArchiveEntry,
        policy: Optional[RetentionPolicy] = None
    ):
        """Register content with retention engine"""        
        if not policy:
            # Find applicable policy
            policy = self.find_applicable_policy(
                content_type=archive_entry.content_type,
                content_category=archive_entry.metadata.get("content_category"),
                creator_id=archive_entry.metadata.get("creator_id"),
                tags=set(archive_entry.metadata.get("tags", [])),
                metadata=archive_entry.metadata
            )
        
        if not policy:
            self.logger.warning(f"No applicable retention policy for content {archive_entry.content_id}")
            return
        
        # Create retention schedule
        schedule = self._create_retention_schedule(archive_entry, policy)
        self.content_schedules[archive_entry.content_id] = schedule
        
        # Store in database
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""                INSERT OR REPLACE INTO content_schedules (
                    content_id, archive_id, policy_id, scheduled_actions,
                    completed_actions, next_action_date, next_action,
                    legal_hold_until, deletion_eligible_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                schedule.content_id, schedule.archive_id, schedule.policy_id,
                json.dumps({k.isoformat(): v.value for k, v in schedule.scheduled_actions.items()}),
                json.dumps(schedule.completed_actions),
                schedule.next_action_date.isoformat() if schedule.next_action_date else None,
                schedule.next_action.value if schedule.next_action else None,
                schedule.legal_hold_until.isoformat() if schedule.legal_hold_until else None,
                schedule.deletion_eligible_date.isoformat() if schedule.deletion_eligible_date else None,
                schedule.created_at.isoformat(),
                schedule.updated_at.isoformat() if schedule.updated_at else None
            ))
            conn.commit()
        
        self.stats["content_registered"] += 1
        self.logger.info(f"Registered content {archive_entry.content_id} with policy {policy.policy_id}")
    
    def _create_retention_schedule(
        self,
        archive_entry: ArchiveEntry,
        policy: RetentionPolicy
    ) -> RetentionSchedule:
        """Create retention schedule for content"""        
        schedule = RetentionSchedule(
            content_id=archive_entry.content_id,
            archive_id=archive_entry.archive_id,
            policy_id=policy.policy_id
        )
        
        base_date = archive_entry.created_at
        
        # Schedule actions based on policy
        for days_offset, action in policy.action_schedule.items():
            action_date = base_date + timedelta(days=days_offset)
            schedule.scheduled_actions[action_date] = action
        
        # Set legal hold if required
        if policy.legal_hold_days:
            schedule.legal_hold_until = base_date + timedelta(days=policy.legal_hold_days)
        
        # Set deletion eligibility
        if policy.maximum_retention_days:
            schedule.deletion_eligible_date = base_date + timedelta(days=policy.maximum_retention_days)
        
        # Find next action
        current_time = datetime.utcnow()
        future_actions = {
            date: action for date, action in schedule.scheduled_actions.items()
            if date > current_time
        }
        
        if future_actions:
            next_date = min(future_actions.keys())
            schedule.next_action_date = next_date
            schedule.next_action = future_actions[next_date]
        
        return schedule
    
    async def can_delete_content(self, content_id: str) -> bool:
        """Check if content can be deleted according to retention policy"""        
        schedule = self.content_schedules.get(content_id)
        if not schedule:
            return True  # No retention policy, can delete
        
        current_time = datetime.utcnow()
        
        # Check legal hold
        if schedule.legal_hold_until and current_time < schedule.legal_hold_until:
            return False
        
        # Check minimum retention
        policy = self.get_policy(schedule.policy_id)
        if policy:
            min_retention_date = datetime.fromisoformat(
                schedule.created_at.isoformat()
            ) + timedelta(days=policy.minimum_retention_days)
            
            if current_time < min_retention_date:
                return False
        
        # Check if deletion is explicitly allowed
        if schedule.deletion_eligible_date:
            return current_time >= schedule.deletion_eligible_date
        
        return True
    
    async def get_due_actions(self, current_time: datetime) -> List[Dict[str, Any]]:
        """Get retention actions that are due for execution"""        
        due_actions = []
        
        for schedule in self.content_schedules.values():
            if schedule.next_action_date and schedule.next_action_date <= current_time:
                due_actions.append({
                    "content_id": schedule.content_id,
                    "archive_id": schedule.archive_id,
                    "action": schedule.next_action,
                    "policy_id": schedule.policy_id,
                    "scheduled_date": schedule.next_action_date
                })
        
        return due_actions
    
    async def execute_retention_action(
        self,
        content_id: str,
        action: RetentionAction,
        policy_id: str,
        executed_by: str = "system"
    ) -> bool:
        """Execute a retention action"""        
        try:
            self.logger.info(f"Executing retention action {action.value} for content {content_id}")
            
            # Check if action handler is registered
            if action in self.action_handlers:
                success = await self.action_handlers[action](content_id, policy_id)
            else:
                # Default action handling
                success = await self._default_action_handler(content_id, action, policy_id)
            
            # Log action execution
            await self._log_retention_action(
                content_id, policy_id, action, 
                "success" if success else "failed",
                executed_by
            )
            
            # Update schedule
            if success:
                await self._update_content_schedule(content_id, action)
            
            self.stats["actions_executed"] += 1
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to execute retention action {action.value} for {content_id}: {e}")
            await self._log_retention_action(
                content_id, policy_id, action, "error", executed_by, {"error": str(e)}
            )
            return False
    
    async def _default_action_handler(
        self,
        content_id: str,
        action: RetentionAction,
        policy_id: str
    ) -> bool:
        """Default retention action handler"""        
        # This is a placeholder implementation
        # In a real system, these would integrate with actual storage/archival systems
        
        if action == RetentionAction.KEEP:
            return True  # No action needed
        elif action == RetentionAction.ARCHIVE:
            self.logger.info(f"Archiving content {content_id}")
            return True
        elif action == RetentionAction.COMPRESS:
            self.logger.info(f"Compressing content {content_id}")
            return True
        elif action == RetentionAction.MIGRATE:
            self.logger.info(f"Migrating content {content_id}")
            return True
        elif action == RetentionAction.DELETE:
            self.logger.info(f"Deleting content {content_id}")
            return True
        elif action == RetentionAction.LEGAL_HOLD:
            self.logger.info(f"Applying legal hold to content {content_id}")
            self.stats["legal_holds_active"] += 1
            return True
        elif action == RetentionAction.REVIEW_REQUIRED:
            self.logger.info(f"Marking content {content_id} for review")
            return True
        
        return False
    
    def register_action_handler(self, action: RetentionAction, handler: Callable):
        """Register custom action handler"""        self.action_handlers[action] = handler
        self.logger.info(f"Registered custom handler for action {action.value}")
    
    async def _log_retention_action(
        self,
        content_id: str,
        policy_id: str,
        action: RetentionAction,
        status: str,
        executed_by: str,
        details: Dict[str, Any] = None
    ):
        """Log retention action execution"""        
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""                INSERT INTO retention_audit_log (
                    content_id, policy_id, action, status, details, executed_at, executed_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id, policy_id, action.value, status,
                json.dumps(details or {}), datetime.utcnow().isoformat(), executed_by
            ))
            conn.commit()
    
    async def _update_content_schedule(self, content_id: str, completed_action: RetentionAction):
        """Update content schedule after action completion"""        
        schedule = self.content_schedules.get(content_id)
        if not schedule:
            return
        
        # Record completed action
        schedule.completed_actions.append({
            "action": completed_action.value,
            "completed_at": datetime.utcnow().isoformat()
        })
        
        # Find next action
        current_time = datetime.utcnow()
        future_actions = {
            date: action for date, action in schedule.scheduled_actions.items()
            if date > current_time and action != completed_action
        }
        
        if future_actions:
            next_date = min(future_actions.keys())
            schedule.next_action_date = next_date
            schedule.next_action = future_actions[next_date]
        else:
            schedule.next_action_date = None
            schedule.next_action = None
        
        schedule.updated_at = current_time
        
        # Update database
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("""                UPDATE content_schedules SET
                    completed_actions = ?, next_action_date = ?, next_action = ?, updated_at = ?
                WHERE content_id = ?
            """, (
                json.dumps(schedule.completed_actions),
                schedule.next_action_date.isoformat() if schedule.next_action_date else None,
                schedule.next_action.value if schedule.next_action else None,
                schedule.updated_at.isoformat(),
                content_id
            ))
            conn.commit()
    
    async def find_expired_content(self) -> List[str]:
        """Find content that has expired according to retention policies"""        
        expired_content = []
        current_time = datetime.utcnow()
        
        for content_id, schedule in self.content_schedules.items():
            # Check if deletion is due
            if (schedule.deletion_eligible_date and 
                current_time >= schedule.deletion_eligible_date and
                await self.can_delete_content(content_id)):
                expired_content.append(content_id)
        
        return expired_content
    
    async def unregister_content(self, content_id: str):
        """Unregister content from retention management"""        
        if content_id in self.content_schedules:
            del self.content_schedules[content_id]
        
        # Remove from database
        with sqlite3.connect(self.database_path) as conn:
            conn.execute("DELETE FROM content_schedules WHERE content_id = ?", (content_id,))
            conn.commit()
        
        self.logger.info(f"Unregistered content {content_id} from retention management")
    
    async def get_retention_statistics(self) -> Dict[str, Any]:
        """Get comprehensive retention statistics"""        
        stats = self.stats.copy()
        
        # Add database statistics
        with sqlite3.connect(self.database_path) as conn:
            # Count by policy
            cursor = conn.execute("""                SELECT policy_id, COUNT(*) 
                FROM content_schedules 
                GROUP BY policy_id
            """)
            stats["content_by_policy"] = dict(cursor.fetchall())
            
            # Count by next action
            cursor = conn.execute("""                SELECT next_action, COUNT(*) 
                FROM content_schedules 
                WHERE next_action IS NOT NULL
                GROUP BY next_action
            """)
            stats["pending_actions"] = dict(cursor.fetchall())
            
            # Count legal holds
            cursor = conn.execute("""                SELECT COUNT(*) 
                FROM content_schedules 
                WHERE legal_hold_until > ?
            """, (datetime.utcnow().isoformat(),))
            stats["active_legal_holds"] = cursor.fetchone()[0]
        
        stats["timestamp"] = datetime.utcnow().isoformat()
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform retention engine health check"""        
        health = {
            "status": "healthy",
            "checks": {},
            "issues": []
        }
        
        try:
            # Check database connectivity
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM retention_policies")
                policy_count = cursor.fetchone()[0]
                health["checks"]["database_accessible"] = True
                health["checks"]["policies_loaded"] = policy_count > 0
            
            # Check scheduler status
            health["checks"]["scheduler_running"] = self.scheduler.running
            
            # Check for overdue actions
            current_time = datetime.utcnow()
            overdue_actions = await self.get_due_actions(current_time - timedelta(hours=1))
            if overdue_actions:
                health["issues"].append(f"{len(overdue_actions)} overdue retention actions")
                health["checks"]["no_overdue_actions"] = False
            else:
                health["checks"]["no_overdue_actions"] = True
            
            # Determine overall status
            if health["issues"]:
                health["status"] = "degraded" if len(health["issues"]) <= 2 else "critical"
            
        except Exception as e:
            health["status"] = "critical"
            health["issues"].append(f"Health check failed: {str(e)}")
        
        return health
    
    async def start_scheduler(self):
        """Start the retention scheduler"""        await self.scheduler.start()
    
    async def stop_scheduler(self):
        """Stop the retention scheduler"""        await self.scheduler.stop()
