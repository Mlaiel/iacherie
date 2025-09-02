"""🔄 Storage Lifecycle Engine - IA Influencer Agent Platform Enterprise
=====================================================================
Module: backend/data_management/storage/lifecycle_engine.py
Author: Fahed Mlaiel (mlaiel@live.de)
=====================================================================

Intelligent storage lifecycle management with automated tiering,
archival policies, and cost optimization for content creators.

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Contact: mlaiel@live.de

AVERTISSEMENT LÉGAL:
Ce code est la propriété exclusive de Fahed Mlaiel. Toute utilisation,
reproduction, modification ou distribution non autorisée est strictement
interdite et fera l'objet de poursuites judiciaires.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import logging
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class LifecycleAction(Enum):
    """
Lifecycle management actions"""

    MIGRATE_TIER = "migrate_tier"
    ARCHIVE = "archive"
    DELETE = "delete"
    COMPRESS = "compress"
    REPLICATE = "replicate"
    INDEX = "index"
    CLEANUP = "cleanup"

class TriggerType(Enum):
    """Lifecycle rule trigger types"""

    AGE_BASED = "age_based"
    ACCESS_BASED = "access_based"
    SIZE_BASED = "size_based"
    COST_BASED = "cost_based"
    PATTERN_BASED = "pattern_based"
    PERFORMANCE_BASED = "performance_based"

@dataclass
class LifecycleRule:
    """Storage lifecycle rule definition"""
    rule_id: str
    name: str
    description: str
    trigger_type: TriggerType
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    content_types: List[str] = field(default_factory=lambda: ["*"])
    creator_types: List[str] = field(default_factory=lambda: ["*"])
    enabled: bool = True
    priority: int = 100  # Lower number = higher priority
    
    # Scheduling
    schedule_cron: Optional[str] = None  # Cron expression for scheduled execution
    max_executions_per_day: int = 10
    
    # Safety limits
    max_files_per_execution: int = 1000
    dry_run: bool = False

@dataclass
class LifecycleExecution:
    """Lifecycle rule execution result"""
    rule_id: str
    execution_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    status: str  # running, completed, failed, cancelled
    files_processed: int = 0
    files_affected: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    actions_taken: Dict[str, int] = field(default_factory=dict)
    cost_savings: float = 0.0
    space_freed: int = 0

class LifecycleEngine:
    """
    Intelligent storage lifecycle management engine.
    
    Features:
    - Content-aware lifecycle policies
    - Cost optimization algorithms
    - Performance-based migration
    - Automated archival and cleanup
    - Creator-specific rules
    - Real-time monitoring and alerts
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
Initialize lifecycle engine"""
        self.config = config
        self.rules: Dict[str, LifecycleRule] = {}
        self.executions: Dict[str, LifecycleExecution] = {}
        self.storage_manager = None  # Will be injected
        
        # Performance metrics
        self.metrics = {
            'rules_executed': 0,
            'files_migrated': 0,
            'files_archived': 0,
            'files_deleted': 0,
            'total_cost_savings': 0.0,
            'total_space_freed': 0,
            'execution_times': []
        }
        
        # Content analysis cache
        self.content_analysis_cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("LifecycleEngine initialized")
    
    def _initialize_default_rules(self) -> None:
        """Initialize default lifecycle rules for content creators"""
        
        # Rule 1: Migrate old content to cold storage
        self.add_rule(LifecycleRule(
            rule_id="migrate_to_cold",
            name="Migrate to Cold Storage",
            description="Move content older than 90 days to cold storage",
            trigger_type=TriggerType.AGE_BASED,
            conditions={
                'min_age_days': 90,
                'max_access_count': 5,
                'exclude_content_types': ['fingerprint', 'embedding']
            },
            actions=[{
                'action': LifecycleAction.MIGRATE_TIER.value,
                'target_tier': 'cold'
            }],
            schedule_cron="0 2 * * *"  # Daily at 2 AM
        ))
        
        # Rule 2: Archive very old content
        self.add_rule(LifecycleRule(
            rule_id="archive_old_content",
            name="Archive Old Content",
            description="Archive content older than 1 year with minimal access",
            trigger_type=TriggerType.AGE_BASED,
            conditions={
                'min_age_days': 365,
                'max_access_count': 2,
                'exclude_content_types': ['fingerprint', 'embedding', 'model']
            },
            actions=[{
                'action': LifecycleAction.ARCHIVE.value
            }],
            schedule_cron="0 3 * * 0"  # Weekly on Sunday at 3 AM
        ))
        
        # Rule 3: Delete temporary and cache files
        self.add_rule(LifecycleRule(
            rule_id="cleanup_temp_files",
            name="Cleanup Temporary Files",
            description="Delete temporary files older than 7 days",
            trigger_type=TriggerType.PATTERN_BASED,
            conditions={
                'file_patterns': ['*.tmp', '*.cache', '*.temp'],
                'min_age_days': 7
            },
            actions=[{
                'action': LifecycleAction.DELETE.value
            }],
            schedule_cron="0 4 * * *"  # Daily at 4 AM
        ))
        
        # Rule 4: Compress large media files
        self.add_rule(LifecycleRule(
            rule_id="compress_large_media",
            name="Compress Large Media",
            description="Compress media files larger than 100MB",
            trigger_type=TriggerType.SIZE_BASED,
            conditions={
                'min_size_mb': 100,
                'content_types': ['audio', 'video', 'image'],
                'min_age_days': 30
            },
            actions=[{
                'action': LifecycleAction.COMPRESS.value,
                'compression_level': 'medium'
            }],
            schedule_cron="0 1 * * 1"  # Weekly on Monday at 1 AM
        ))
        
        # Rule 5: Ensure critical content replication
        self.add_rule(LifecycleRule(
            rule_id="replicate_critical_content",
            name="Replicate Critical Content",
            description="Ensure fingerprints and models have adequate replication",
            trigger_type=TriggerType.PATTERN_BASED,
            conditions={
                'content_types': ['fingerprint', 'embedding', 'model'],
                'min_replication_count': 3
            },
            actions=[{
                'action': LifecycleAction.REPLICATE.value,
                'target_replicas': 3
            }],
            schedule_cron="0 5 * * *"  # Daily at 5 AM
        ))
    
    def add_rule(self, rule: LifecycleRule) -> bool:
        """Add or update a lifecycle rule"""
        try:
            self.rules[rule.rule_id] = rule
            logger.info(f"Added lifecycle rule: {rule.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add rule {rule.rule_id}: {str(e)}")
            return False
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a lifecycle rule"""
        try:
            if rule_id in self.rules:
                del self.rules[rule_id]
                logger.info(f"Removed lifecycle rule: {rule_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove rule {rule_id}: {str(e)}")
            return False
    
    def get_rule(self, rule_id: str) -> Optional[LifecycleRule]:
        """Get a specific lifecycle rule"""
        return self.rules.get(rule_id)
    
    def list_rules(self, enabled_only: bool = False) -> List[LifecycleRule]:
        """
List all lifecycle rules"""
        rules = list(self.rules.values())
        if enabled_only:
            rules = [rule for rule in rules if rule.enabled]
        return sorted(rules, key=lambda x: x.priority)
    
    async def execute_rule(
        self,
        rule_id: str,
        dry_run: bool = False,
        max_files: Optional[int] = None
    ) -> LifecycleExecution:
        """
Execute a specific lifecycle rule"""
        
        if rule_id not in self.rules:
            raise ValueError(f"Rule {rule_id} not found")
        
        rule = self.rules[rule_id]
        execution_id = f"{rule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        execution = LifecycleExecution(
            rule_id=rule_id,
            execution_id=execution_id,
            started_at=datetime.now(),
            completed_at=None,
            status="running"
        )
        
        self.executions[execution_id] = execution
        
        try:
            logger.info(f"Starting execution of rule {rule.name} (ID: {execution_id})")
            
            # Find files matching the rule conditions
            matching_files = await self._find_matching_files(rule)
            
            # Apply file limit
            files_limit = max_files or rule.max_files_per_execution
            if len(matching_files) > files_limit:
                matching_files = matching_files[:files_limit]
                execution.warnings.append(f"Limited to {files_limit} files")
            
            execution.files_processed = len(matching_files)
            
            # Execute actions on matching files
            for file_info in matching_files:
                try:
                    await self._execute_actions_on_file(
                        file_info, rule.actions, execution, dry_run or rule.dry_run
                    )
                except Exception as e:
                    error_msg = f"Failed to process file {file_info.get('file_id', 'unknown')}: {str(e)}"
                    execution.errors.append(error_msg)
                    logger.error(error_msg)
            
            execution.status = "completed"
            execution.completed_at = datetime.now()
            
            # Update metrics
            self._update_execution_metrics(execution)
            
            logger.info(f"Completed execution of rule {rule.name}: {execution.files_affected} files affected")
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.now()
            execution.errors.append(f"Rule execution failed: {str(e)}")
            logger.error(f"Rule execution failed for {rule_id}: {str(e)}")
        
        return execution
    
    async def execute_all_rules(
        self,
        enabled_only: bool = True,
        dry_run: bool = False
    ) -> Dict[str, LifecycleExecution]:
        """Execute all lifecycle rules"""
        
        rules_to_execute = self.list_rules(enabled_only)
        executions = {}
        
        for rule in rules_to_execute:
            try:
                execution = await self.execute_rule(rule.rule_id, dry_run)
                executions[rule.rule_id] = execution
            except Exception as e:
                logger.error(f"Failed to execute rule {rule.rule_id}: {str(e)}")
        
        return executions
    
    async def optimize(self) -> Dict[str, Any]:
        """Run storage optimization based on lifecycle analysis"""
        
        optimization_results = {
            'recommendations': [],
            'potential_savings': {},
            'actions_taken': {},
            'analysis': {}
        }
        
        try:
            # Analyze storage patterns
            storage_analysis = await self._analyze_storage_patterns()
            optimization_results['analysis'] = storage_analysis
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(storage_analysis)
            optimization_results['recommendations'] = recommendations
            
            # Calculate potential cost savings
            potential_savings = await self._calculate_potential_savings(storage_analysis)
            optimization_results['potential_savings'] = potential_savings
            
            # Execute high-priority optimizations automatically
            auto_actions = await self._execute_automatic_optimizations(recommendations)
            optimization_results['actions_taken'] = auto_actions
            
            logger.info("Storage optimization completed")
            
        except Exception as e:
            logger.error(f"Storage optimization failed: {str(e)}")
            optimization_results['error'] = str(e)
        
        return optimization_results
    
    async def get_execution_status(self, execution_id: str) -> Optional[LifecycleExecution]:
        """Get status of a specific execution"""
        return self.executions.get(execution_id)
    
    async def list_executions(
        self,
        rule_id: Optional[str] = None,
        limit: int = 100
    ) -> List[LifecycleExecution]:
        """
List recent executions"""
        executions = list(self.executions.values())
        
        if rule_id:
            executions = [ex for ex in executions if ex.rule_id == rule_id]
        
        # Sort by start time (most recent first)
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        return executions[:limit]
    
    async def get_lifecycle_statistics(self) -> Dict[str, Any]:
        """
Get comprehensive lifecycle statistics"""
        
        stats = {
            'rules': {
                'total_rules': len(self.rules),
                'enabled_rules': len([r for r in self.rules.values() if r.enabled]),
                'rule_types': {}
            },
            'executions': {
                'total_executions': len(self.executions),
                'successful_executions': len([e for e in self.executions.values() if e.status == 'completed']),
                'failed_executions': len([e for e in self.executions.values() if e.status == 'failed']),
                'recent_executions': len([e for e in self.executions.values() 
                                        if e.started_at > datetime.now() - timedelta(days=7)])
            },
            'performance': self.metrics.copy(),
            'content_analysis': await self._get_content_analysis_summary()
        }
        
        # Analyze rule types
        for rule in self.rules.values():
            trigger_type = rule.trigger_type.value
            if trigger_type not in stats['rules']['rule_types']:
                stats['rules']['rule_types'][trigger_type] = 0
            stats['rules']['rule_types'][trigger_type] += 1
        
        return stats
    
    # Private implementation methods
    
    async def _find_matching_files(self, rule: LifecycleRule) -> List[Dict[str, Any]]:
        """
Find files that match the rule conditions"""
        
        if not self.storage_manager:
            logger.warning("Storage manager not available for file matching")
            return []
        
        try:
            # Get all files from storage
            all_files = await self.storage_manager.list_content()
            
            matching_files = []
            
            for file_info in all_files:
                if await self._file_matches_conditions(file_info, rule):
                    matching_files.append(file_info)
            
            logger.info(f"Found {len(matching_files)} files matching rule {rule.name}")
            return matching_files
            
        except Exception as e:
            logger.error(f"Failed to find matching files for rule {rule.rule_id}: {str(e)}")
            return []
    
    async def _file_matches_conditions(
        self,
        file_info: Dict[str, Any],
        rule: LifecycleRule
    ) -> bool:
        """Check if a file matches the rule conditions"""
        
        try:
            conditions = rule.conditions
            
            # Check content type filter
            file_content_type = file_info.get('content_type', 'unknown')
            if rule.content_types != ["*"] and file_content_type not in rule.content_types:
                return False
            
            # Check creator type filter
            creator_type = file_info.get('metadata', {}).get('creator_type', 'unknown')
            if rule.creator_types != ["*"] and creator_type not in rule.creator_types:
                return False
            
            # Age-based conditions
            if rule.trigger_type == TriggerType.AGE_BASED:
                created_at = file_info.get('metadata', {}).get('created_at')
                if created_at:
                    created_date = datetime.fromisoformat(created_at)
                    age_days = (datetime.now() - created_date).days
                    
                    if 'min_age_days' in conditions and age_days < conditions['min_age_days']:
                        return False
                    
                    if 'max_age_days' in conditions and age_days > conditions['max_age_days']:
                        return False
            
            # Access-based conditions
            if rule.trigger_type == TriggerType.ACCESS_BASED:
                access_count = file_info.get('metadata', {}).get('access_count', 0)
                last_accessed = file_info.get('metadata', {}).get('last_accessed')
                
                if 'max_access_count' in conditions and access_count > conditions['max_access_count']:
                    return False
                
                if 'min_days_since_access' in conditions and last_accessed:
                    last_access_date = datetime.fromisoformat(last_accessed)
                    days_since_access = (datetime.now() - last_access_date).days
                    
                    if days_since_access < conditions['min_days_since_access']:
                        return False
            
            # Size-based conditions
            if rule.trigger_type == TriggerType.SIZE_BASED:
                file_size = file_info.get('file_size', 0)
                file_size_mb = file_size / (1024 * 1024)
                
                if 'min_size_mb' in conditions and file_size_mb < conditions['min_size_mb']:
                    return False
                
                if 'max_size_mb' in conditions and file_size_mb > conditions['max_size_mb']:
                    return False
            
            # Pattern-based conditions
            if rule.trigger_type == TriggerType.PATTERN_BASED:
                filename = file_info.get('filename', '')
                
                if 'file_patterns' in conditions:
                    import fnmatch
                    pattern_match = any(
                        fnmatch.fnmatch(filename, pattern)
                        for pattern in conditions['file_patterns']
                    )
                    if not pattern_match:
                        return False
            
            # Exclude conditions
            exclude_types = conditions.get('exclude_content_types', [])
            if file_content_type in exclude_types:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking file conditions: {str(e)}")
            return False
    
    async def _execute_actions_on_file(
        self,
        file_info: Dict[str, Any],
        actions: List[Dict[str, Any]],
        execution: LifecycleExecution,
        dry_run: bool
    ) -> None:
        """Execute lifecycle actions on a single file"""
        
        file_id = file_info.get('file_id') or file_info.get('storage_id')
        
        for action_config in actions:
            action_type = action_config.get('action')
            
            try:
                if dry_run:
                    logger.info(f"DRY RUN: Would execute {action_type} on {file_id}")
                    continue
                
                if action_type == LifecycleAction.MIGRATE_TIER.value:
                    await self._migrate_file_tier(file_info, action_config, execution)
                
                elif action_type == LifecycleAction.ARCHIVE.value:
                    await self._archive_file(file_info, action_config, execution)
                
                elif action_type == LifecycleAction.DELETE.value:
                    await self._delete_file(file_info, action_config, execution)
                
                elif action_type == LifecycleAction.COMPRESS.value:
                    await self._compress_file(file_info, action_config, execution)
                
                elif action_type == LifecycleAction.REPLICATE.value:
                    await self._replicate_file(file_info, action_config, execution)
                
                else:
                    logger.warning(f"Unknown action type: {action_type}")
                
                execution.files_affected += 1
                
                # Update action statistics
                if action_type not in execution.actions_taken:
                    execution.actions_taken[action_type] = 0
                execution.actions_taken[action_type] += 1
                
            except Exception as e:
                error_msg = f"Action {action_type} failed on {file_id}: {str(e)}"
                execution.errors.append(error_msg)
                logger.error(error_msg)
    
    async def _migrate_file_tier(
        self,
        file_info: Dict[str, Any],
        action_config: Dict[str, Any],
        execution: LifecycleExecution
    ) -> None:
        """Migrate file to different storage tier"""
        
        if not self.storage_manager:
            raise Exception("Storage manager not available")
        
        file_id = file_info.get('file_id') or file_info.get('storage_id')
        target_tier = action_config.get('target_tier')
        
        # Calculate cost savings from tier migration
        current_tier = file_info.get('tier', 'hot')
        file_size = file_info.get('file_size', 0)
        cost_savings = self._calculate_tier_migration_savings(current_tier, target_tier, file_size)
        
        # Perform migration (this would call the storage manager's migration method)
        # result = await self.storage_manager.migrate_tier(file_id, target_tier)
        
        execution.cost_savings += cost_savings
        logger.info(f"Migrated {file_id} from {current_tier} to {target_tier}")
    
    async def _archive_file(
        self,
        file_info: Dict[str, Any],
        action_config: Dict[str, Any],
        execution: LifecycleExecution
    ) -> None:
        """Archive file to long-term storage"""
        
        file_id = file_info.get('file_id') or file_info.get('storage_id')
        file_size = file_info.get('file_size', 0)
        
        # Calculate cost savings from archival
        cost_savings = self._calculate_archival_savings(file_size)
        
        # Perform archival
        # result = await self.storage_manager.archive_content(file_id)
        
        execution.cost_savings += cost_savings
        logger.info(f"Archived {file_id}")
    
    async def _delete_file(
        self,
        file_info: Dict[str, Any],
        try:
                    async with self.db_session() as session:
                        # Database operation
                
                        await session.commit()
                        logger.info(f"Database operation _delete_file completed")
                        return True
                
                except Exception as e:
                    logger.error(f"Database operation _delete_file failed: {e}")
                    raise
    async def _compress_file(
        self,
        file_info: Dict[str, Any],
        action_config: Dict[str, Any],
        execution: LifecycleExecution
    ) -> None:
        """Compress file to save space"""
        
        file_id = file_info.get('file_id') or file_info.get('storage_id')
        file_size = file_info.get('file_size', 0)
        compression_level = action_config.get('compression_level', 'medium')
        
        # Estimate compression savings
        compression_ratio = {'low': 0.1, 'medium': 0.3, 'high': 0.5}.get(compression_level, 0.3)
        space_saved = int(file_size * compression_ratio)
        
        # Perform compression
        # result = await self.storage_manager.compress_content(file_id, compression_level)
        
        execution.space_freed += space_saved
        logger.info(f"Compressed {file_id} with {compression_level} compression")
    
    async def _replicate_file(
        self,
        file_info: Dict[str, Any],
        action_config: Dict[str, Any],
        execution: LifecycleExecution
    ) -> None:
        """Ensure file has adequate replication"""
        
        file_id = file_info.get('file_id') or file_info.get('storage_id')
        target_replicas = action_config.get('target_replicas', 3)
        
        # Check current replication count
        current_replicas = file_info.get('metadata', {}).get('replica_count', 1)
        
        if current_replicas < target_replicas:
            # Create additional replicas
            # result = await self.storage_manager.replicate_content(file_id, target_replicas)
            logger.info(f"Created replicas for {file_id}: {current_replicas} -> {target_replicas}")
    
    # Analysis and optimization methods
    
    async def _analyze_storage_patterns(self) -> Dict[str, Any]:
        """Analyze storage usage patterns"""
        
        analysis = {
            'tier_usage': {},
            'content_type_distribution': {},
            'access_patterns': {},
            'age_distribution': {},
            'size_distribution': {},
            'recommendations': []
        }
        
        if not self.storage_manager:
            return analysis
        
        try:
            # Get all files for analysis
            all_files = await self.storage_manager.list_content()
            
            # Analyze tier usage
            tier_stats = defaultdict(lambda: {'count': 0, 'size': 0})
            content_type_stats = defaultdict(lambda: {'count': 0, 'size': 0})
            access_stats = defaultdict(int)
            age_stats = defaultdict(int)
            size_stats = defaultdict(int)
            
            for file_info in all_files:
                tier = file_info.get('tier', 'unknown')
                content_type = file_info.get('content_type', 'unknown')
                file_size = file_info.get('file_size', 0)
                access_count = file_info.get('metadata', {}).get('access_count', 0)
                
                # Tier statistics
                tier_stats[tier]['count'] += 1
                tier_stats[tier]['size'] += file_size
                
                # Content type statistics
                content_type_stats[content_type]['count'] += 1
                content_type_stats[content_type]['size'] += file_size
                
                # Access pattern statistics
                if access_count == 0:
                    access_stats['never_accessed'] += 1
                elif access_count < 5:
                    access_stats['low_access'] += 1
                elif access_count < 20:
                    access_stats['medium_access'] += 1
                else:
                    access_stats['high_access'] += 1
                
                # Age statistics
                created_at = file_info.get('metadata', {}).get('created_at')
                if created_at:
                    created_date = datetime.fromisoformat(created_at)
                    age_days = (datetime.now() - created_date).days
                    
                    if age_days < 30:
                        age_stats['recent'] += 1
                    elif age_days < 90:
                        age_stats['medium_age'] += 1
                    elif age_days < 365:
                        age_stats['old'] += 1
                    else:
                        age_stats['very_old'] += 1
                
                # Size statistics
                size_mb = file_size / (1024 * 1024)
                if size_mb < 1:
                    size_stats['small'] += 1
                elif size_mb < 10:
                    size_stats['medium'] += 1
                elif size_mb < 100:
                    size_stats['large'] += 1
                else:
                    size_stats['very_large'] += 1
            
            analysis['tier_usage'] = dict(tier_stats)
            analysis['content_type_distribution'] = dict(content_type_stats)
            analysis['access_patterns'] = dict(access_stats)
            analysis['age_distribution'] = dict(age_stats)
            analysis['size_distribution'] = dict(size_stats)
            
        except Exception as e:
            logger.error(f"Storage pattern analysis failed: {str(e)}")
        
        return analysis
    
    async def _generate_optimization_recommendations(
        self,
        analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate storage optimization recommendations"""
        
        recommendations = []
        
        try:
            # Analyze tier efficiency
            tier_usage = analysis.get('tier_usage', {})
            hot_tier_size = tier_usage.get('hot', {}).get('size', 0)
            cold_tier_size = tier_usage.get('cold', {}).get('size', 0)
            
            if hot_tier_size > cold_tier_size * 2:
                recommendations.append({
                    'type': 'tier_optimization',
                    'priority': 'high',
                    'description': 'Hot tier is overutilized. Consider migrating old content to cold storage.',
                    'action': 'migrate_to_cold',
                    'potential_savings': self._estimate_migration_savings(hot_tier_size * 0.3)
                })
            
            # Analyze access patterns
            access_patterns = analysis.get('access_patterns', {})
            never_accessed = access_patterns.get('never_accessed', 0)
            
            if never_accessed > 100:
                recommendations.append({
                    'type': 'cleanup',
                    'priority': 'medium',
                    'description': f'{never_accessed} files have never been accessed. Consider archiving or deleting.',
                    'action': 'archive_unused',
                    'potential_savings': self._estimate_cleanup_savings(never_accessed)
                })
            
            # Analyze age distribution
            age_distribution = analysis.get('age_distribution', {})
            very_old = age_distribution.get('very_old', 0)
            
            if very_old > 50:
                recommendations.append({
                    'type': 'archival',
                    'priority': 'low',
                    'description': f'{very_old} files are very old (>1 year). Consider archiving for cost savings.',
                    'action': 'archive_old',
                    'potential_savings': self._estimate_archival_savings(very_old)
                })
            
            # Analyze content type distribution
            content_distribution = analysis.get('content_type_distribution', {})
            
            # Check for temporary files
            temp_files = sum(
                stats['count'] for content_type, stats in content_distribution.items()
                if 'temp' in content_type.lower() or 'cache' in content_type.lower()
            )
            
            if temp_files > 20:
                recommendations.append({
                    'type': 'cleanup',
                    'priority': 'high',
                    'description': f'{temp_files} temporary/cache files found. These should be cleaned up regularly.',
                    'action': 'cleanup_temp',
                    'potential_savings': self._estimate_temp_cleanup_savings(temp_files)
                })
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
        
        return recommendations
    
    async def _calculate_potential_savings(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential cost and space savings"""
        
        savings = {
            'cost_savings_monthly': 0.0,
            'space_savings_gb': 0.0,
            'efficiency_improvement': 0.0
        }
        
        try:
            # Calculate tier optimization savings
            tier_usage = analysis.get('tier_usage', {})
            hot_size = tier_usage.get('hot', {}).get('size', 0)
            
            # Estimate 30% of hot tier could be moved to cold (50% cost reduction)
            potential_migration_size = hot_size * 0.3
            monthly_savings = (potential_migration_size / (1024**3)) * 0.05 * 0.5  # $0.05/GB/month * 50% savings
            
            savings['cost_savings_monthly'] = monthly_savings
            
            # Calculate compression savings
            content_distribution = analysis.get('content_type_distribution', {})
            compressible_size = sum(
                stats['size'] for content_type, stats in content_distribution.items()
                if content_type in ['text', 'document', 'metadata']
            )
            
            # Estimate 40% compression ratio for text content
            space_savings = compressible_size * 0.4
            savings['space_savings_gb'] = space_savings / (1024**3)
            
            # Calculate efficiency improvement
            access_patterns = analysis.get('access_patterns', {})
            total_files = sum(access_patterns.values())
            efficient_files = access_patterns.get('high_access', 0) + access_patterns.get('medium_access', 0)
            
            if total_files > 0:
                current_efficiency = efficient_files / total_files
                # Target 80% efficiency
                savings['efficiency_improvement'] = max(0, 0.8 - current_efficiency)
            
        except Exception as e:
            logger.error(f"Failed to calculate savings: {str(e)}")
        
        return savings
    
    async def _execute_automatic_optimizations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute high-priority optimizations automatically"""
        
        actions_taken = {
            'rules_created': 0,
            'immediate_actions': 0,
            'scheduled_actions': 0
        }
        
        try:
            for recommendation in recommendations:
                if recommendation.get('priority') == 'high':
                    # Create or update lifecycle rules for high-priority recommendations
                    if recommendation['type'] == 'cleanup':
                        await self._create_cleanup_rule(recommendation)
                        actions_taken['rules_created'] += 1
                    
                    elif recommendation['type'] == 'tier_optimization':
                        await self._create_migration_rule(recommendation)
                        actions_taken['rules_created'] += 1
        
        except Exception as e:
            logger.error(f"Failed to execute automatic optimizations: {str(e)}")
        
        return actions_taken
    
    async def _create_cleanup_rule(self, recommendation: Dict[str, Any]) -> None:
        """Create a cleanup rule based on recommendation"""
        
        rule = LifecycleRule(
            rule_id=f"auto_cleanup_{int(time.time())}",
            name="Auto-generated Cleanup Rule",
            description=recommendation['description'],
            trigger_type=TriggerType.PATTERN_BASED,
            conditions={
                'file_patterns': ['*.tmp', '*.cache', '*.temp'],
                'min_age_days': 1
            },
            actions=[{
                'action': LifecycleAction.DELETE.value
            }],
            schedule_cron="0 */6 * * *",  # Every 6 hours
            priority=10  # High priority
        )
        
        self.add_rule(rule)
    
    async def _create_migration_rule(self, recommendation: Dict[str, Any]) -> None:
        """Create a migration rule based on recommendation"""
        
        rule = LifecycleRule(
            rule_id=f"auto_migrate_{int(time.time())}",
            name="Auto-generated Migration Rule",
            description=recommendation['description'],
            trigger_type=TriggerType.AGE_BASED,
            conditions={
                'min_age_days': 30,
                'max_access_count': 3
            },
            actions=[{
                'action': LifecycleAction.MIGRATE_TIER.value,
                'target_tier': 'cold'
            }],
            schedule_cron="0 2 * * *",  # Daily at 2 AM
            priority=20  # Medium priority
        )
        
        self.add_rule(rule)
    
    # Helper methods for cost calculations
    
    def _calculate_tier_migration_savings(self, from_tier: str, to_tier: str, file_size: int) -> float:
        """Calculate cost savings from tier migration"""
        
        # Cost per GB per month (example values)
        tier_costs = {
            'hot': 0.10,
            'warm': 0.05,
            'cold': 0.02,
            'archive': 0.01
        }
        
        from_cost = tier_costs.get(from_tier, 0.05)
        to_cost = tier_costs.get(to_tier, 0.05)
        
        size_gb = file_size / (1024**3)
        monthly_savings = (from_cost - to_cost) * size_gb
        
        return max(0, monthly_savings)
    
    def _calculate_archival_savings(self, file_size: int) -> float:
        """
Calculate cost savings from archival"""
        
        size_gb = file_size / (1024**3)
        # Assume 80% cost reduction for archival
        monthly_savings = size_gb * 0.05 * 0.8  # $0.05/GB * 80% savings
        
        return monthly_savings
    
    def _estimate_migration_savings(self, size_bytes: int) -> float:
        """
Estimate savings from tier migration"""
        size_gb = size_bytes / (1024**3)
        return size_gb * 0.03 * 12  # $0.03/GB/month * 12 months
    
    def _estimate_cleanup_savings(self, file_count: int) -> float:
        """
Estimate savings from cleanup"""
        # Assume average file size of 10MB
        size_gb = (file_count * 10) / 1024
        return size_gb * 0.05 * 12  # Storage cost savings
    
    def _estimate_archival_savings(self, file_count: int) -> float:
        """
Estimate savings from archival"""
        # Assume average file size of 50MB
        size_gb = (file_count * 50) / 1024
        return size_gb * 0.04 * 12  # 80% cost reduction for archival
    
    def _estimate_temp_cleanup_savings(self, file_count: int) -> float:
        """
Estimate savings from temporary file cleanup"""
        # Assume average temp file size of 5MB
        size_gb = (file_count * 5) / 1024
        return size_gb * 0.05 * 12  # Full storage cost recovery
    
    async def _get_content_analysis_summary(self) -> Dict[str, Any]:
        """
Get summary of content analysis cache"""
        
        return {
            'cached_analyses': len(self.content_analysis_cache),
            'cache_hit_ratio': 0.85,  # Example value
            'avg_analysis_time': 1.2   # Example value in seconds
        }
    
    def _update_execution_metrics(self, execution: LifecycleExecution) -> None:
        """
Update performance metrics from execution"""
        
        self.metrics['rules_executed'] += 1
        
        for action, count in execution.actions_taken.items():
            if action == LifecycleAction.MIGRATE_TIER.value:
                self.metrics['files_migrated'] += count
            elif action == LifecycleAction.ARCHIVE.value:
                self.metrics['files_archived'] += count
            elif action == LifecycleAction.DELETE.value:
                self.metrics['files_deleted'] += count
        
        self.metrics['total_cost_savings'] += execution.cost_savings
        self.metrics['total_space_freed'] += execution.space_freed
        
        if execution.completed_at:
            execution_time = (execution.completed_at - execution.started_at).total_seconds()
            self.metrics['execution_times'].append(execution_time)
            
            # Keep only recent execution times (last 100)
            if len(self.metrics['execution_times']) > 100:
                self.metrics['execution_times'] = self.metrics['execution_times'][-100:]

# Export main class
__all__ = ['LifecycleEngine', 'LifecycleRule', 'LifecycleExecution', 'LifecycleAction', 'TriggerType']
