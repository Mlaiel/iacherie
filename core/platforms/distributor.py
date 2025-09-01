"""Platform Distributor Module

Handles automated content distribution across multiple platforms with intelligent routing.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, copying, or distribution 
of this code without explicit written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import logging
from enum import Enum
from dataclasses import dataclass

from .base import (
    PlatformBase, PlatformManager, ContentType, ContentMetadata, 
    UploadResult, PlatformType
)

logger = logging.getLogger(__name__)


class DistributionStrategy(Enum):
    """
Distribution strategy enumeration"""

    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    PRIORITY_FIRST = "priority_first"
    SCHEDULED = "scheduled"
    SMART_ROUTING = "smart_routing"


class ContentFormat(Enum):
    """Content format enumeration"""

    ORIGINAL = "original"
    OPTIMIZED = "optimized"
    PLATFORM_SPECIFIC = "platform_specific"


@dataclass
class PlatformTarget:
    """Platform target configuration"""
    platform_id: str
    priority: int = 1
    format: ContentFormat = ContentFormat.ORIGINAL
    custom_metadata: Optional[ContentMetadata] = None
    scheduled_time: Optional[datetime] = None
    retry_count: int = 3
    success_threshold: float = 0.8


@dataclass
class DistributionRule:
    """
Distribution rule configuration"""
    content_types: List[ContentType]
    platform_types: List[PlatformType]
    min_quality_score: float = 0.7
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_formats: List[str] = None
    geo_restrictions: List[str] = None
    time_restrictions: Dict[str, Any] = None


@dataclass
class DistributionTask:
    """
Distribution task definition"""
    task_id: str
    content_path: str
    metadata: ContentMetadata
    targets: List[PlatformTarget]
    strategy: DistributionStrategy
    rules: List[DistributionRule]
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    retry_limit: int = 3
    timeout: int = 300


@dataclass
class DistributionResult:
    """
Distribution result summary"""
    task_id: str
    success_count: int
    failure_count: int
    total_platforms: int
    results: Dict[str, UploadResult]
    execution_time: float
    errors: List[str]
    warnings: List[str]
    completed_at: datetime


class PlatformDistributor:
    """
Intelligent platform distribution manager"""
    
    def __init__(self, platform_manager: PlatformManager):
        """
Initialize distributor with platform manager"""
        self.platform_manager = platform_manager
        self.active_tasks: Dict[str, DistributionTask] = {}
        self.completed_tasks: Dict[str, DistributionResult] = {}
        self.distribution_rules: List[DistributionRule] = []
        self.default_strategy = DistributionStrategy.SMART_ROUTING
        
    def add_distribution_rule(self, rule: DistributionRule):
        """
Add distribution rule"""
        self.distribution_rules.append(rule)
        logger.info(f"Added distribution rule for content types: {rule.content_types}")
    
    def remove_distribution_rule(self, index: int):
        """Remove distribution rule by index"""
        if 0 <= index < len(self.distribution_rules):
            removed_rule = self.distribution_rules.pop(index)
            logger.info(f"Removed distribution rule for content types: {removed_rule.content_types}")
    
    async def distribute_content(
        self,
        task_id: str,
        content_path: str,
        metadata: ContentMetadata,
        platform_targets: List[PlatformTarget],
        strategy: DistributionStrategy = None
    ) -> DistributionResult:
        """Distribute content to multiple platforms"""
        start_time = datetime.utcnow()
        strategy = strategy or self.default_strategy
        
        # Create distribution task
        task = DistributionTask(
            task_id=task_id,
            content_path=content_path,
            metadata=metadata,
            targets=platform_targets,
            strategy=strategy,
            rules=self._get_applicable_rules(metadata),
            created_at=start_time
        )
        
        self.active_tasks[task_id] = task
        
        try:
            # Validate content and targets
            validation_errors = await self._validate_distribution(task)
            if validation_errors:
                return self._create_failed_result(task_id, validation_errors, start_time)
            
            # Filter and prepare targets
            valid_targets = await self._prepare_targets(task)
            if not valid_targets:
                return self._create_failed_result(task_id, ["No valid targets available"], start_time)
            
            # Execute distribution based on strategy
            results = await self._execute_distribution(task, valid_targets)
            
            # Create result summary
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            
            success_count = sum(1 for r in results.values() if r.success)
            failure_count = len(results) - success_count
            
            errors = [r.error for r in results.values() if r.error]
            warnings = self._generate_warnings(task, results)
            
            result = DistributionResult(
                task_id=task_id,
                success_count=success_count,
                failure_count=failure_count,
                total_platforms=len(results),
                results=results,
                execution_time=execution_time,
                errors=errors,
                warnings=warnings,
                completed_at=end_time
            )
            
            self.completed_tasks[task_id] = result
            return result
            
        except Exception as e:
            logger.error(f"Distribution task {task_id} failed: {e}")
            return self._create_failed_result(task_id, [str(e)], start_time)
        
        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
    
    async def _validate_distribution(self, task: DistributionTask) -> List[str]:
        """Validate distribution task"""
        errors = []
        
        # Check if content file exists
        import os
        if not os.path.exists(task.content_path):
            errors.append(f"Content file not found: {task.content_path}")
            return errors
        
        # Check file size
        file_size = os.path.getsize(task.content_path)
        for rule in task.rules:
            if file_size > rule.max_file_size:
                errors.append(f"File size {file_size} exceeds limit {rule.max_file_size}")
        
        # Check content type compatibility
        content_type = self._detect_content_type(task.content_path)
        if not self._is_content_type_allowed(content_type, task.rules):
            errors.append(f"Content type {content_type} not allowed by rules")
        
        # Validate platforms
        for target in task.targets:
            platform = self.platform_manager.get_platform(target.platform_id)
            if not platform:
                errors.append(f"Platform {target.platform_id} not found")
            elif not platform.is_active:
                errors.append(f"Platform {target.platform_id} is not active")
        
        return errors
    
    async def _prepare_targets(self, task: DistributionTask) -> List[PlatformTarget]:
        """Prepare and filter valid targets"""
        valid_targets = []
        
        for target in task.targets:
            platform = self.platform_manager.get_platform(target.platform_id)
            if platform and platform.is_active:
                # Check platform compatibility
                if self._is_platform_compatible(platform, task):
                    valid_targets.append(target)
                else:
                    logger.warning(f"Platform {target.platform_id} not compatible with content")
        
        # Sort by priority
        valid_targets.sort(key=lambda t: t.priority, reverse=True)
        return valid_targets
    
    async def _execute_distribution(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """Execute distribution based on strategy"""
        if task.strategy == DistributionStrategy.SIMULTANEOUS:
            return await self._distribute_simultaneous(task, targets)
        elif task.strategy == DistributionStrategy.SEQUENTIAL:
            return await self._distribute_sequential(task, targets)
        elif task.strategy == DistributionStrategy.PRIORITY_FIRST:
            return await self._distribute_priority_first(task, targets)
        elif task.strategy == DistributionStrategy.SCHEDULED:
            return await self._distribute_scheduled(task, targets)
        elif task.strategy == DistributionStrategy.SMART_ROUTING:
            return await self._distribute_smart_routing(task, targets)
        else:
            raise ValueError(f"Unknown distribution strategy: {task.strategy}")
    
    async def _distribute_simultaneous(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """Distribute to all platforms simultaneously"""
        tasks = []
        for target in targets:
            platform = self.platform_manager.get_platform(target.platform_id)
            metadata = target.custom_metadata or task.metadata
            tasks.append(self._upload_with_retry(platform, task.content_path, metadata, target))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        result_dict = {}
        for i, result in enumerate(results):
            target = targets[i]
            if isinstance(result, Exception):
                result_dict[target.platform_id] = UploadResult(
                    success=False,
                    platform_id=target.platform_id,
                    error=str(result)
                )
            else:
                result_dict[target.platform_id] = result
        
        return result_dict
    
    async def _distribute_sequential(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """
Distribute to platforms sequentially"""
        results = {}
        
        for target in targets:
            platform = self.platform_manager.get_platform(target.platform_id)
            metadata = target.custom_metadata or task.metadata
            
            result = await self._upload_with_retry(platform, task.content_path, metadata, target)
            results[target.platform_id] = result
            
            # Add delay between uploads to avoid rate limiting
            await asyncio.sleep(1)
        
        return results
    
    async def _distribute_priority_first(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """
Distribute to highest priority platforms first"""
        results = {}
        
        # Group by priority
        priority_groups = {}
        for target in targets:
            priority = target.priority
            if priority not in priority_groups:
                priority_groups[priority] = []
            priority_groups[priority].append(target)
        
        # Process in priority order
        for priority in sorted(priority_groups.keys(), reverse=True):
            group_targets = priority_groups[priority]
            
            # Process group simultaneously
            group_results = await self._distribute_simultaneous(task, group_targets)
            results.update(group_results)
            
            # Check if we have enough successes to stop
            success_count = sum(1 for r in results.values() if r.success)
            if success_count >= len(targets) * 0.8:  # 80% success threshold
                break
        
        return results
    
    async def _distribute_scheduled(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """
Distribute based on scheduled times"""
        results = {}
        now = datetime.utcnow()
        
        # Separate immediate and scheduled targets
        immediate_targets = []
        scheduled_targets = []
        
        for target in targets:
            if target.scheduled_time and target.scheduled_time > now:
                scheduled_targets.append(target)
            else:
                immediate_targets.append(target)
        
        # Process immediate targets
        if immediate_targets:
            immediate_results = await self._distribute_simultaneous(task, immediate_targets)
            results.update(immediate_results)
        
        # Schedule future targets (simplified - in production, use a proper scheduler)
        for target in scheduled_targets:
            delay = (target.scheduled_time - now).total_seconds()
            if delay > 0:
                await asyncio.sleep(min(delay, 300))  # Max 5 minute wait for demo
            
            platform = self.platform_manager.get_platform(target.platform_id)
            metadata = target.custom_metadata or task.metadata
            result = await self._upload_with_retry(platform, task.content_path, metadata, target)
            results[target.platform_id] = result
        
        return results
    
    async def _distribute_smart_routing(
        self, 
        task: DistributionTask, 
        targets: List[PlatformTarget]
    ) -> Dict[str, UploadResult]:
        """
Intelligent distribution based on platform characteristics"""
        results = {}
        
        # Analyze content and platforms
        content_type = self._detect_content_type(task.content_path)
        
        # Group platforms by type and characteristics
        music_platforms = []
        video_platforms = []
        social_platforms = []
        
        for target in targets:
            platform = self.platform_manager.get_platform(target.platform_id)
            if platform.platform_type == PlatformType.MUSIC:
                music_platforms.append(target)
            elif platform.platform_type == PlatformType.VIDEO:
                video_platforms.append(target)
            elif platform.platform_type == PlatformType.SOCIAL:
                social_platforms.append(target)
        
        # Route based on content type
        if content_type == ContentType.AUDIO:
            # Music platforms first, then social
            primary_targets = music_platforms + social_platforms
            secondary_targets = video_platforms
        elif content_type == ContentType.VIDEO:
            # Video platforms first, then social
            primary_targets = video_platforms + social_platforms
            secondary_targets = music_platforms
        else:
            # Social platforms for other content
            primary_targets = social_platforms
            secondary_targets = music_platforms + video_platforms
        
        # Distribute to primary targets first
        if primary_targets:
            primary_results = await self._distribute_simultaneous(task, primary_targets)
            results.update(primary_results)
        
        # If primary distribution is successful enough, skip secondary
        primary_success_rate = sum(1 for r in results.values() if r.success) / max(len(results), 1)
        
        if primary_success_rate < 0.7 and secondary_targets:
            secondary_results = await self._distribute_simultaneous(task, secondary_targets)
            results.update(secondary_results)
        
        return results
    
    async def _upload_with_retry(
        self, 
        platform: PlatformBase, 
        content_path: str, 
        metadata: ContentMetadata, 
        target: PlatformTarget
    ) -> UploadResult:
        """
Upload with retry logic"""
        last_error = None
        
        for attempt in range(target.retry_count):
            try:
                result = await platform.upload_content(content_path, metadata)
                if result.success:
                    return result
                else:
                    last_error = result.error
                    logger.warning(f"Upload attempt {attempt + 1} failed for {platform.platform_id}: {last_error}")
            
            except Exception as e:
                last_error = str(e)
                logger.error(f"Upload attempt {attempt + 1} error for {platform.platform_id}: {e}")
            
            # Wait before retry
            if attempt < target.retry_count - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return UploadResult(
            success=False,
            platform_id=platform.platform_id,
            error=f"Upload failed after {target.retry_count} attempts: {last_error}"
        )
    
    def _detect_content_type(self, file_path: str) -> ContentType:
        """Detect content type from file"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type:
            if mime_type.startswith('audio/'):
                return ContentType.AUDIO
            elif mime_type.startswith('video/'):
                return ContentType.VIDEO
            elif mime_type.startswith('image/'):
                return ContentType.IMAGE
        
        return ContentType.TEXT
    
    def _is_content_type_allowed(self, content_type: ContentType, rules: List[DistributionRule]) -> bool:
        """
Check if content type is allowed by rules"""
        if not rules:
            return True
        
        for rule in rules:
            if content_type in rule.content_types:
                return True
        
        return False
    
    def _is_platform_compatible(self, platform: PlatformBase, task: DistributionTask) -> bool:
        """
Check if platform is compatible with content"""
        content_type = self._detect_content_type(task.content_path)
        
        # Check if platform supports the content type
        if content_type not in platform.config.content_types:
            return False
        
        # Check distribution rules
        for rule in task.rules:
            if platform.platform_type in rule.platform_types:
                return True
        
        return len(task.rules) == 0  # If no rules, allow all platforms
    
    def _get_applicable_rules(self, metadata: ContentMetadata) -> List[DistributionRule]:
        """
Get applicable distribution rules for content"""
        # For now, return all rules. In practice, you'd filter based on content characteristics
        return self.distribution_rules
    
    def _generate_warnings(self, task: DistributionTask, results: Dict[str, UploadResult]) -> List[str]:
        """
Generate warnings based on distribution results"""
        warnings = []
        
        success_rate = sum(1 for r in results.values() if r.success) / max(len(results), 1)
        if success_rate < 0.5:
            warnings.append(f"Low success rate: {success_rate:.1%}")
        
        failed_platforms = [pid for pid, result in results.items() if not result.success]
        if failed_platforms:
            warnings.append(f"Failed platforms: {', '.join(failed_platforms)}")
        
        return warnings
    
    def _create_failed_result(self, task_id: str, errors: List[str], start_time: datetime) -> DistributionResult:
        """Create failed distribution result"""
        return DistributionResult(
            task_id=task_id,
            success_count=0,
            failure_count=0,
            total_platforms=0,
            results={},
            execution_time=(datetime.utcnow() - start_time).total_seconds(),
            errors=errors,
            warnings=[],
            completed_at=datetime.utcnow()
        )
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
Get status of a distribution task"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                'status': 'active',
                'task': task,
                'started_at': task.created_at
            }
        elif task_id in self.completed_tasks:
            result = self.completed_tasks[task_id]
            return {
                'status': 'completed',
                'result': result
            }
        else:
            return None
    
    def get_distribution_stats(self) -> Dict[str, Any]:
        """
Get distribution statistics"""
        total_tasks = len(self.completed_tasks)
        successful_tasks = sum(1 for r in self.completed_tasks.values() if r.success_count > 0)
        
        platform_stats = {}
        for result in self.completed_tasks.values():
            for platform_id, upload_result in result.results.items():
                if platform_id not in platform_stats:
                    platform_stats[platform_id] = {'success': 0, 'failure': 0}
                
                if upload_result.success:
                    platform_stats[platform_id]['success'] += 1
                else:
                    platform_stats[platform_id]['failure'] += 1
        
        return {
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'active_tasks': len(self.active_tasks),
            'success_rate': successful_tasks / max(total_tasks, 1),
            'platform_stats': platform_stats,
            'distribution_rules': len(self.distribution_rules)
        }
