"""Cross-Platform Sync - Advanced Cross-Platform Content Synchronization Engine
Intelligent content adaptation, unified publishing, and cross-platform analytics consolidation

Created by: Fahed Mlaiel <mlaiel@live.de>
Project: IA Influencer Agent - Ultra-Industrial Content Protection & Monetization Platform

⚠️ STRICT COPYRIGHT WARNING ⚠️
This code and concept are the intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit written permission 
from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited and will result in legal action.

Development Team Specialties:
- Lead AI Developer & ML Engineer
- Backend Senior Architect
- Database Administrator (DBA) 
- Security & Microservices Expert
- Audio Processing Specialist
- DevOps & Infrastructure Engineer
- AI Prompt Engineering Expert
"""
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import hashlib
from collections import defaultdict, deque
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class SyncStatus(Enum):
    """Cross-platform synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    CANCELLED = "cancelled"

class ConflictResolution(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    PLATFORM_PRIORITY = "platform_priority"
    MANUAL_REVIEW = "manual_review"
    MERGE_CONTENT = "merge_content"
    KEEP_BOTH = "keep_both"

class SyncDirection(Enum):
    """Synchronization direction"""
    BIDIRECTIONAL = "bidirectional"
    ONE_WAY_TO = "one_way_to"
    ONE_WAY_FROM = "one_way_from"
    BROADCAST = "broadcast"

@dataclass
class PlatformContent:
    """Content representation for a specific platform"""
    platform: str
    content_id: str
    title: str
    description: str
    media_urls: List[str]
    hashtags: List[str]
    mentions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    checksum: str = ""
    
    def __post_init__(self):
        if not self.checksum:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calculate content checksum for change detection"""
        content_str = f"{self.title}{self.description}{','.join(self.hashtags)}{','.join(self.media_urls)}"
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def has_changed(self, other: 'PlatformContent') -> bool:
        """Check if content has changed compared to another version"""
        return self.checksum != other.checksum
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class SyncRule:
    """Cross-platform synchronization rule"""
    id: str
    name: str
    source_platforms: List[str]
    target_platforms: List[str]
    sync_direction: SyncDirection
    content_filters: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: Dict[str, Any] = field(default_factory=dict)
    conflict_resolution: ConflictResolution = ConflictResolution.LATEST_WINS
    auto_sync: bool = True
    sync_interval: Optional[int] = None  # minutes
    priority: int = 1  # 1=high, 5=low
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class SyncOperation:
    """Synchronization operation tracking"""
    id: str
    rule_id: str
    source_platform: str
    target_platforms: List[str]
    content_id: str
    status: SyncStatus = SyncStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    sync_results: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    
@dataclass
class ConflictItem:
    """Content conflict requiring resolution"""
    id: str
    content_id: str
    platforms: List[str]
    conflict_type: str
    source_content: PlatformContent
    target_content: PlatformContent
    suggested_resolution: ConflictResolution
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution: Optional[str] = None

class ContentTransformer(ABC):
    """Abstract base class for content transformation"""
    
    @abstractmethod
    async def transform(self, content: PlatformContent, target_platform: str) -> PlatformContent:
        """Transform content for target platform"""
        pass
    
    @abstractmethod
    def can_transform(self, source_platform: str, target_platform: str) -> bool:
        """Check if transformation is supported"""
        pass

class StandardContentTransformer(ContentTransformer):
    """Standard content transformer with platform-specific adaptations"""
    
    PLATFORM_LIMITS = {
        'twitter': {'text_limit': 280, 'hashtag_limit': 10, 'media_limit': 4},
        'instagram': {'text_limit': 2200, 'hashtag_limit': 30, 'media_limit': 10},
        'facebook': {'text_limit': 63206, 'hashtag_limit': 50, 'media_limit': 100},
        'linkedin': {'text_limit': 3000, 'hashtag_limit': 20, 'media_limit': 9},
        'tiktok': {'text_limit': 150, 'hashtag_limit': 20, 'media_limit': 1},
        'youtube': {'title_limit': 100, 'description_limit': 5000, 'hashtag_limit': 15}
    }
    
    def can_transform(self, source_platform: str, target_platform: str) -> bool:
        """Check if transformation is supported"""
        return target_platform.lower() in self.PLATFORM_LIMITS
    
    async def transform(self, content: PlatformContent, target_platform: str) -> PlatformContent:
        """Transform content for target platform"""
        if not self.can_transform(content.platform, target_platform):
            raise ValueError(f"Transformation from {content.platform} to {target_platform} not supported")
        
        limits = self.PLATFORM_LIMITS.get(target_platform.lower(), {})
        
        # Create transformed content
        transformed = PlatformContent(
            platform=target_platform,
            content_id=f"{content.content_id}_{target_platform}",
            title=content.title,
            description=content.description,
            media_urls=content.media_urls.copy(),
            hashtags=content.hashtags.copy(),
            mentions=content.mentions.copy(),
            metadata=content.metadata.copy()
        )
        
        # Apply platform-specific transformations
        await self._apply_text_limits(transformed, limits)
        await self._apply_hashtag_limits(transformed, limits)
        await self._apply_media_limits(transformed, limits)
        await self._apply_platform_specific_rules(transformed, target_platform)
        
        return transformed
    
    async def _apply_text_limits(self, content: PlatformContent, limits: Dict[str, Any]):
        """Apply text length limits"""
        text_limit = limits.get('text_limit')
        if text_limit and len(content.description) > text_limit:
            # Smart truncation preserving important content
            content.description = self._smart_truncate(content.description, text_limit)
    
    async def _apply_hashtag_limits(self, content: PlatformContent, limits: Dict[str, Any]):
        """Apply hashtag limits"""
        hashtag_limit = limits.get('hashtag_limit')
        if hashtag_limit and len(content.hashtags) > hashtag_limit:
            # Keep most important hashtags
            content.hashtags = content.hashtags[:hashtag_limit]
    
    async def _apply_media_limits(self, content: PlatformContent, limits: Dict[str, Any]):
        """Apply media limits"""
        media_limit = limits.get('media_limit')
        if media_limit and len(content.media_urls) > media_limit:
            content.media_urls = content.media_urls[:media_limit]
    
    async def _apply_platform_specific_rules(self, content: PlatformContent, platform: str):
        """Apply platform-specific formatting rules"""
        platform_lower = platform.lower()
        
        if platform_lower == 'twitter':
            # Twitter-specific formatting
            content.description = self._format_for_twitter(content.description)
        elif platform_lower == 'linkedin':
            # LinkedIn professional formatting
            content.description = self._format_for_linkedin(content.description)
        elif platform_lower == 'instagram':
            # Instagram visual-first formatting
            content.description = self._format_for_instagram(content.description)
    
    def _smart_truncate(self, text: str, limit: int) -> str:
        """Intelligently truncate text preserving meaning"""
        if len(text) <= limit:
            return text
        
        # Try to break at sentence boundaries
        sentences = text.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') <= limit - 3:
                truncated += sentence + '. '
            else:
                break
        
        if truncated:
            return truncated.rstrip() + "..."
        
        # Fallback to word boundaries
        words = text.split()
        truncated_words = []
        
        for word in words:
            if len(' '.join(truncated_words + [word])) <= limit - 3:
                truncated_words.append(word)
            else:
                break
        
        return ' '.join(truncated_words) + "..." if truncated_words else text[:limit-3] + "..."
    
    def _format_for_twitter(self, text: str) -> str:
        """Format text for Twitter"""
        # Ensure proper spacing for hashtags and mentions
        text = re.sub(r'(\S)#', r'\1 #', text)
        text = re.sub(r'(\S)@', r'\1 @', text)
        return text
    
    def _format_for_linkedin(self, text: str) -> str:
        """Format text for LinkedIn professional style"""
        # Add line breaks for better readability
        sentences = text.split('. ')
        if len(sentences) > 2:
            formatted = '. '.join(sentences[:2]) + '.\n\n' + '. '.join(sentences[2:])
            return formatted
        return text
    
    def _format_for_instagram(self, text: str) -> str:
        """Format text for Instagram visual-first approach"""
        # Move hashtags to the end for cleaner appearance
        lines = text.split('\n')
        content_lines = []
        hashtag_lines = []
        
        for line in lines:
            if line.strip().startswith('#'):
                hashtag_lines.append(line)
            else:
                content_lines.append(line)
        
        formatted = '\n'.join(content_lines)
        if hashtag_lines:
            formatted += '\n\n' + '\n'.join(hashtag_lines)
        
        return formatted

class ConflictResolver:
    """Handles content conflicts between platforms"""
    
    def __init__(self):
        self.pending_conflicts: List[ConflictItem] = []
        self.resolution_strategies: Dict[ConflictResolution, callable] = {
            ConflictResolution.LATEST_WINS: self._resolve_latest_wins,
            ConflictResolution.PLATFORM_PRIORITY: self._resolve_platform_priority,
            ConflictResolution.MERGE_CONTENT: self._resolve_merge_content,
            ConflictResolution.KEEP_BOTH: self._resolve_keep_both
        }
        self.platform_priorities: Dict[str, int] = {
            'instagram': 1,
            'twitter': 2,
            'youtube': 3,
            'facebook': 4,
            'linkedin': 5,
            'tiktok': 6
        }
    
    async def detect_conflicts(self, content_versions: List[PlatformContent]) -> List[ConflictItem]:
        """Detect conflicts between content versions"""
        conflicts = []
        
        # Group by content ID (base ID without platform suffix)
        content_groups = defaultdict(list)
        for content in content_versions:
            base_id = content.content_id.split('_')[0]
            content_groups[base_id].append(content)
        
        # Check for conflicts within each group
        for base_id, versions in content_groups.items():
            if len(versions) > 1:
                conflicts.extend(await self._check_version_conflicts(base_id, versions))
        
        return conflicts
    
    async def _check_version_conflicts(self, content_id: str, versions: List[PlatformContent]) -> List[ConflictItem]:
        """Check for conflicts between content versions"""
        conflicts = []
        
        # Compare all pairs of versions
        for i in range(len(versions)):
            for j in range(i + 1, len(versions)):
                version_a, version_b = versions[i], versions[j]
                
                if version_a.has_changed(version_b):
                    conflict_type = self._determine_conflict_type(version_a, version_b)
                    
                    conflict = ConflictItem(
                        id=str(uuid.uuid4()),
                        content_id=content_id,
                        platforms=[version_a.platform, version_b.platform],
                        conflict_type=conflict_type,
                        source_content=version_a,
                        target_content=version_b,
                        suggested_resolution=self._suggest_resolution(version_a, version_b, conflict_type)
                    )
                    
                    conflicts.append(conflict)
        
        return conflicts
    
    def _determine_conflict_type(self, content_a: PlatformContent, content_b: PlatformContent) -> str:
        """Determine the type of conflict between two content versions"""
        if content_a.title != content_b.title:
            return "title_mismatch"
        elif content_a.description != content_b.description:
            return "description_mismatch"
        elif set(content_a.hashtags) != set(content_b.hashtags):
            return "hashtag_mismatch"
        elif set(content_a.media_urls) != set(content_b.media_urls):
            return "media_mismatch"
        else:
            return "metadata_mismatch"
    
    def _suggest_resolution(self, content_a: PlatformContent, content_b: PlatformContent, 
                          conflict_type: str) -> ConflictResolution:
        """Suggest resolution strategy based on conflict type"""
        if conflict_type == "title_mismatch":
            return ConflictResolution.PLATFORM_PRIORITY
        elif conflict_type == "description_mismatch":
            return ConflictResolution.MERGE_CONTENT
        elif conflict_type in ["hashtag_mismatch", "media_mismatch"]:
            return ConflictResolution.LATEST_WINS
        else:
            return ConflictResolution.MANUAL_REVIEW
    
    async def resolve_conflict(self, conflict: ConflictItem) -> Optional[PlatformContent]:
        """Resolve a content conflict"""
        if conflict.resolved:
            return None
        
        resolution_strategy = self.resolution_strategies.get(conflict.suggested_resolution)
        if not resolution_strategy:
            logger.error(f"No resolution strategy for {conflict.suggested_resolution}")
            return None
        
        try:
            resolved_content = await resolution_strategy(conflict)
            conflict.resolved = True
            conflict.resolution = f"Resolved using {conflict.suggested_resolution.value}"
            return resolved_content
        except Exception as e:
            logger.error(f"Failed to resolve conflict {conflict.id}: {str(e)}")
            return None
    
    async def _resolve_latest_wins(self, conflict: ConflictItem) -> PlatformContent:
        """Resolve by using the most recently updated content"""
        if conflict.source_content.updated_at > conflict.target_content.updated_at:
            return conflict.source_content
        return conflict.target_content
    
    async def _resolve_platform_priority(self, conflict: ConflictItem) -> PlatformContent:
        """Resolve by platform priority"""
        source_priority = self.platform_priorities.get(conflict.source_content.platform, 10)
        target_priority = self.platform_priorities.get(conflict.target_content.platform, 10)
        
        if source_priority < target_priority:
            return conflict.source_content
        return conflict.target_content
    
    async def _resolve_merge_content(self, conflict: ConflictItem) -> PlatformContent:
        """Resolve by merging content from both versions"""
        source = conflict.source_content
        target = conflict.target_content
        
        # Create merged content
        merged = PlatformContent(
            platform="merged",
            content_id=source.content_id,
            title=source.title if len(source.title) > len(target.title) else target.title,
            description=self._merge_descriptions(source.description, target.description),
            media_urls=list(set(source.media_urls + target.media_urls)),
            hashtags=list(set(source.hashtags + target.hashtags)),
            mentions=list(set(source.mentions + target.mentions)),
            metadata={**target.metadata, **source.metadata}  # Source overwrites target
        )
        
        return merged
    
    def _merge_descriptions(self, desc_a: str, desc_b: str) -> str:
        """Merge two descriptions intelligently"""
        if not desc_a:
            return desc_b
        if not desc_b:
            return desc_a
        
        # Use longer description as base and append unique content
        if len(desc_a) > len(desc_b):
            base, additional = desc_a, desc_b
        else:
            base, additional = desc_b, desc_a
        
        # Extract unique sentences from additional content
        base_sentences = set(base.split('. '))
        additional_sentences = [s for s in additional.split('. ') if s not in base_sentences]
        
        if additional_sentences:
            return base + '\n\n' + '. '.join(additional_sentences)
        
        return base
    
    async def _resolve_keep_both(self, conflict: ConflictItem) -> List[PlatformContent]:
        """Resolve by keeping both versions as separate content"""
        source = conflict.source_content
        target = conflict.target_content
        
        # Modify IDs to indicate they're separate versions
        source.content_id += "_v1"
        target.content_id += "_v2"
        
        return [source, target]

class CrossPlatformSync:
    """
    Advanced Cross-Platform Content Synchronization Engine
    Handles intelligent content sync, conflict resolution, and unified content management
    """
    
    def __init__(self):
        self.sync_rules: Dict[str, SyncRule] = {}
        self.active_operations: Dict[str, SyncOperation] = {}
        self.content_cache: Dict[str, PlatformContent] = {}
        self.sync_history: deque = deque(maxlen=1000)
        self.content_transformer = StandardContentTransformer()
        self.conflict_resolver = ConflictResolver()
        self.sync_queue: asyncio.Queue = asyncio.Queue()
        self.worker_tasks: List[asyncio.Task] = []
        self.running = False
        
    async def start_sync_engine(self, num_workers: int = 3):
        """Start the synchronization engine with worker tasks"""
        if self.running:
            return
        
        self.running = True
        
        # Start worker tasks
        for i in range(num_workers):
            task = asyncio.create_task(self._sync_worker(f"worker_{i}"))
            self.worker_tasks.append(task)
        
        # Start periodic sync task
        periodic_task = asyncio.create_task(self._periodic_sync())
        self.worker_tasks.append(periodic_task)
        
        logger.info(f"Cross-platform sync engine started with {num_workers} workers")
    
    async def stop_sync_engine(self):
        """Stop the synchronization engine"""
        self.running = False
        
        # Cancel all worker tasks
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        self.worker_tasks.clear()
        
        logger.info("Cross-platform sync engine stopped")
    
    async def _sync_worker(self, worker_id: str):
        """Worker task for processing sync operations"""
        logger.info(f"Sync worker {worker_id} started")
        
        while self.running:
            try:
                # Get operation from queue with timeout
                operation = await asyncio.wait_for(self.sync_queue.get(), timeout=5.0)
                await self._process_sync_operation(operation)
                self.sync_queue.task_done()
                
            except asyncio.TimeoutError:
                continue  # Normal timeout, continue loop
            except Exception as e:
                logger.error(f"Sync worker {worker_id} error: {str(e)}")
                await asyncio.sleep(1)
        
        logger.info(f"Sync worker {worker_id} stopped")
    
    async def _periodic_sync(self):
        """Periodic synchronization based on rules"""
        while self.running:
            try:
                await self._check_scheduled_syncs()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Periodic sync error: {str(e)}")
                await asyncio.sleep(60)
    
    async def _check_scheduled_syncs(self):
        """Check for rules that need periodic synchronization"""
        now = datetime.utcnow()
        
        for rule in self.sync_rules.values():
            if not rule.active or not rule.auto_sync or not rule.sync_interval:
                continue
            
            # Check if it's time for sync
            last_sync = self._get_last_sync_time(rule.id)
            if not last_sync or (now - last_sync).total_seconds() >= rule.sync_interval * 60:
                await self._trigger_rule_sync(rule)
    
    def _get_last_sync_time(self, rule_id: str) -> Optional[datetime]:
        """Get last sync time for a rule"""
        for entry in reversed(self.sync_history):
            if entry.get('rule_id') == rule_id:
                return entry.get('completed_at')
        return None
    
    async def _trigger_rule_sync(self, rule: SyncRule):
        """Trigger synchronization for a rule"""
        logger.info(f"Triggering periodic sync for rule: {rule.name}")
        
        # Create sync operations for all content matching the rule
        for source_platform in rule.source_platforms:
            content_items = await self._get_platform_content(source_platform, rule.content_filters)
            
            for content in content_items:
                operation = SyncOperation(
                    id=str(uuid.uuid4()),
                    rule_id=rule.id,
                    source_platform=source_platform,
                    target_platforms=rule.target_platforms,
                    content_id=content.content_id
                )
                
                await self.sync_queue.put(operation)
    
    def add_sync_rule(self, rule: SyncRule):
        """Add a new synchronization rule"""
        self.sync_rules[rule.id] = rule
        logger.info(f"Added sync rule: {rule.name}")
    
    def remove_sync_rule(self, rule_id: str) -> bool:
        """Remove a synchronization rule"""
        if rule_id in self.sync_rules:
            del self.sync_rules[rule_id]
            logger.info(f"Removed sync rule: {rule_id}")
            return True
        return False
    
    async def sync_content(self, content: PlatformContent, target_platforms: List[str],
                          rule_id: Optional[str] = None) -> str:
        """Sync content to target platforms"""
        operation = SyncOperation(
            id=str(uuid.uuid4()),
            rule_id=rule_id or "manual",
            source_platform=content.platform,
            target_platforms=target_platforms,
            content_id=content.content_id
        )
        
        # Cache source content
        self.content_cache[content.content_id] = content
        
        # Queue operation
        await self.sync_queue.put(operation)
        self.active_operations[operation.id] = operation
        
        logger.info(f"Queued sync operation {operation.id} for content {content.content_id}")
        return operation.id
    
    async def _process_sync_operation(self, operation: SyncOperation):
        """Process a sync operation"""
        operation.status = SyncStatus.IN_PROGRESS
        operation.started_at = datetime.utcnow()
        
        try:
            # Get source content
            source_content = self.content_cache.get(operation.content_id)
            if not source_content:
                source_content = await self._fetch_content(operation.source_platform, operation.content_id)
            
            if not source_content:
                raise ValueError(f"Source content not found: {operation.content_id}")
            
            sync_results = {}
            
            # Sync to each target platform
            for target_platform in operation.target_platforms:
                try:
                    result = await self._sync_to_platform(source_content, target_platform, operation.rule_id)
                    sync_results[target_platform] = result
                    
                except Exception as e:
                    logger.error(f"Failed to sync to {target_platform}: {str(e)}")
                    sync_results[target_platform] = {'success': False, 'error': str(e)}
            
            # Determine overall status
            successful_syncs = sum(1 for result in sync_results.values() if result.get('success'))
            total_syncs = len(sync_results)
            
            if successful_syncs == total_syncs:
                operation.status = SyncStatus.COMPLETED
            elif successful_syncs > 0:
                operation.status = SyncStatus.PARTIAL
            else:
                operation.status = SyncStatus.FAILED
            
            operation.sync_results = sync_results
            operation.completed_at = datetime.utcnow()
            
            # Add to history
            self.sync_history.append({
                'operation_id': operation.id,
                'rule_id': operation.rule_id,
                'source_platform': operation.source_platform,
                'target_platforms': operation.target_platforms,
                'status': operation.status.value,
                'completed_at': operation.completed_at
            })
            
            logger.info(f"Sync operation {operation.id} completed with status: {operation.status.value}")
            
        except Exception as e:
            operation.status = SyncStatus.FAILED
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
            logger.error(f"Sync operation {operation.id} failed: {str(e)}")
        
        finally:
            # Remove from active operations
            if operation.id in self.active_operations:
                del self.active_operations[operation.id]
    
    async def _sync_to_platform(self, source_content: PlatformContent, target_platform: str,
                               rule_id: Optional[str]) -> Dict[str, Any]:
        """Sync content to a specific platform"""
        # Get sync rule if specified
        rule = self.sync_rules.get(rule_id) if rule_id else None
        
        # Transform content for target platform
        if source_content.platform != target_platform:
            transformed_content = await self.content_transformer.transform(source_content, target_platform)
        else:
            transformed_content = source_content
        
        # Apply rule transformations if applicable
        if rule and rule.transformation_rules:
            transformed_content = await self._apply_transformation_rules(transformed_content, rule.transformation_rules)
        
        # Check for existing content and conflicts
        existing_content = await self._fetch_content(target_platform, transformed_content.content_id)
        
        if existing_content:
            # Check for conflicts
            conflicts = await self.conflict_resolver.detect_conflicts([transformed_content, existing_content])
            
            if conflicts:
                # Resolve conflicts based on rule
                resolution_strategy = rule.conflict_resolution if rule else ConflictResolution.LATEST_WINS
                
                if resolution_strategy == ConflictResolution.MANUAL_REVIEW:
                    # Queue for manual review
                    self.conflict_resolver.pending_conflicts.extend(conflicts)
                    return {'success': False, 'reason': 'conflict_requires_manual_review'}
                else:
                    # Auto-resolve conflict
                    for conflict in conflicts:
                        conflict.suggested_resolution = resolution_strategy
                        resolved_content = await self.conflict_resolver.resolve_conflict(conflict)
                        if resolved_content:
                            transformed_content = resolved_content
        
        # Publish to target platform
        result = await self._publish_to_platform(transformed_content, target_platform)
        
        # Cache the content
        self.content_cache[transformed_content.content_id] = transformed_content
        
        return result
    
    async def _apply_transformation_rules(self, content: PlatformContent, 
                                        transformation_rules: Dict[str, Any]) -> PlatformContent:
        """Apply transformation rules to content"""
        # Apply hashtag transformations
        if 'hashtag_mappings' in transformation_rules:
            mappings = transformation_rules['hashtag_mappings']
            content.hashtags = [mappings.get(tag, tag) for tag in content.hashtags]
        
        # Apply content filters
        if 'content_filters' in transformation_rules:
            filters = transformation_rules['content_filters']
            
            if 'remove_words' in filters:
                for word in filters['remove_words']:
                    content.description = content.description.replace(word, '')
            
            if 'replace_words' in filters:
                for old_word, new_word in filters['replace_words'].items():
                    content.description = content.description.replace(old_word, new_word)
        
        # Apply metadata transformations
        if 'metadata_rules' in transformation_rules:
            metadata_rules = transformation_rules['metadata_rules']
            content.metadata.update(metadata_rules)
        
        return content
    
    async def _get_platform_content(self, platform: str, filters: Dict[str, Any]) -> List[PlatformContent]:
        """Get content from platform with filters"""
        # This would typically connect to platform APIs
        # For now, return cached content
        platform_content = [
            content for content in self.content_cache.values()
            if content.platform == platform
        ]
        
        # Apply filters
        if 'created_after' in filters:
            after_date = datetime.fromisoformat(filters['created_after'])
            platform_content = [c for c in platform_content if c.created_at > after_date]
        
        if 'hashtags_include' in filters:
            required_tags = set(filters['hashtags_include'])
            platform_content = [c for c in platform_content 
                              if required_tags.intersection(set(c.hashtags))]
        
        return platform_content
    
    async def _fetch_content(self, platform: str, content_id: str) -> Optional[PlatformContent]:
        """Fetch content from platform"""
        # Check cache first
        cache_key = f"{platform}_{content_id}"
        if cache_key in self.content_cache:
            return self.content_cache[cache_key]
        
        # This would typically make API calls to fetch content
        # For now, return None (content not found)
        return None
    
    async def _publish_to_platform(self, content: PlatformContent, platform: str) -> Dict[str, Any]:
        """Publish content to platform"""
        # This would typically use platform APIs to publish content
        # For now, simulate successful publication
        
        try:
            # Simulate API call delay
            await asyncio.sleep(0.1)
            
            # Update content metadata
            content.updated_at = datetime.utcnow()
            content.version += 1
            
            return {
                'success': True,
                'platform': platform,
                'content_id': content.content_id,
                'published_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'platform': platform,
                'error': str(e)
            }
    
    def get_sync_status(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a sync operation"""
        operation = self.active_operations.get(operation_id)
        if operation:
            return {
                'id': operation.id,
                'status': operation.status.value,
                'source_platform': operation.source_platform,
                'target_platforms': operation.target_platforms,
                'started_at': operation.started_at.isoformat() if operation.started_at else None,
                'completed_at': operation.completed_at.isoformat() if operation.completed_at else None,
                'error_message': operation.error_message,
                'sync_results': operation.sync_results
            }
        
        # Check history
        for entry in self.sync_history:
            if entry.get('operation_id') == operation_id:
                return entry
        
        return None
    
    def get_sync_analytics(self, days_back: int = 7) -> Dict[str, Any]:
        """Get synchronization analytics"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        recent_operations = [
            entry for entry in self.sync_history
            if entry.get('completed_at') and 
            datetime.fromisoformat(entry['completed_at']) > cutoff_date
        ]
        
        analytics = {
            'total_operations': len(recent_operations),
            'by_status': defaultdict(int),
            'by_source_platform': defaultdict(int),
            'by_target_platform': defaultdict(int),
            'success_rate': 0.0,
            'active_operations': len(self.active_operations),
            'pending_conflicts': len(self.conflict_resolver.pending_conflicts)
        }
        
        for operation in recent_operations:
            status = operation.get('status', 'unknown')
            analytics['by_status'][status] += 1
            
            source = operation.get('source_platform')
            if source:
                analytics['by_source_platform'][source] += 1
            
            for target in operation.get('target_platforms', []):
                analytics['by_target_platform'][target] += 1
        
        # Calculate success rate
        if recent_operations:
            successful = analytics['by_status']['completed']
            analytics['success_rate'] = successful / len(recent_operations)
        
        return dict(analytics)
    
    def get_pending_conflicts(self) -> List[Dict[str, Any]]:
        """Get pending conflicts requiring resolution"""
        return [
            {
                'id': conflict.id,
                'content_id': conflict.content_id,
                'platforms': conflict.platforms,
                'conflict_type': conflict.conflict_type,
                'suggested_resolution': conflict.suggested_resolution.value,
                'created_at': conflict.created_at.isoformat()
            }
            for conflict in self.conflict_resolver.pending_conflicts
            if not conflict.resolved
        ]
    
    async def resolve_manual_conflict(self, conflict_id: str, resolution: ConflictResolution) -> bool:
        """Manually resolve a conflict"""
        for conflict in self.conflict_resolver.pending_conflicts:
            if conflict.id == conflict_id and not conflict.resolved:
                conflict.suggested_resolution = resolution
                resolved_content = await self.conflict_resolver.resolve_conflict(conflict)
                
                if resolved_content:
                    # Update content cache
                    self.content_cache[resolved_content.content_id] = resolved_content
                    logger.info(f"Manually resolved conflict {conflict_id}")
                    return True
        
        return False
