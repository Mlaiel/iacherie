"""
Content Distribution Manager - IA Influencer Agent Platform
=========================================================

Advanced multi-platform content distribution system with automated publishing,
scheduling, and platform-specific optimization for maximum reach and engagement.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import aiohttp
from ...core.config import get_settings
from ...core.database import get_database
from ...core.exceptions import DistributionError
from ...core.logging import get_logger
from ...integrations.social_platforms import SocialPlatformManager
from ...models.distribution import DistributionJob, DistributionStatus
from ...utils.scheduler import TaskScheduler

logger = get_logger(__name__)
settings = get_settings()


class ContentDistributionManager:
    """Advanced multi-platform content distribution system."""
    
    def __init__(self):
        self.db = get_database()
        self.platform_manager = SocialPlatformManager()
        self.scheduler = TaskScheduler()
        
        # Platform configurations
        self.platform_configs = {
            'youtube': {
                'max_file_size': 128 * 1024 * 1024 * 1024,  # 128GB
                'supported_formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                'max_duration': 43200,  # 12 hours
                'api_limits': {'uploads_per_day': 100, 'requests_per_second': 10}
            },
            'instagram': {
                'max_file_size': 100 * 1024 * 1024,  # 100MB
                'supported_formats': ['mp4', 'mov', 'jpg', 'png'],
                'max_duration': 60,
                'aspect_ratios': ['1:1', '4:5', '9:16'],
                'api_limits': {'posts_per_hour': 25, 'requests_per_second': 5}
            },
            'tiktok': {
                'max_file_size': 4 * 1024 * 1024 * 1024,  # 4GB
                'supported_formats': ['mp4', 'mov', 'webm'],
                'max_duration': 180,
                'min_duration': 3,
                'aspect_ratio': '9:16',
                'api_limits': {'uploads_per_day': 20, 'requests_per_second': 2}
            },
            'twitter': {
                'max_file_size': 512 * 1024 * 1024,  # 512MB
                'supported_formats': ['mp4', 'mov', 'gif', 'jpg', 'png'],
                'max_duration': 140,
                'api_limits': {'tweets_per_hour': 300, 'requests_per_second': 15}
            },
            'facebook': {
                'max_file_size': 10 * 1024 * 1024 * 1024,  # 10GB
                'supported_formats': ['mp4', 'mov', 'avi', 'jpg', 'png'],
                'max_duration': 14400,  # 4 hours
                'api_limits': {'posts_per_hour': 25, 'requests_per_second': 10}
            },
            'linkedin': {
                'max_file_size': 200 * 1024 * 1024,  # 200MB
                'supported_formats': ['mp4', 'mov', 'jpg', 'png'],
                'max_duration': 600,
                'api_limits': {'posts_per_hour': 10, 'requests_per_second': 5}
            },
            'spotify': {
                'supported_formats': ['mp3', 'flac', 'wav'],
                'min_quality': '320kbps',
                'api_limits': {'uploads_per_day': 10, 'requests_per_second': 1}
            },
            'soundcloud': {
                'max_file_size': 2 * 1024 * 1024 * 1024,  # 2GB
                'supported_formats': ['mp3', 'wav', 'flac', 'aac', 'ogg', 'm4a'],
                'api_limits': {'uploads_per_day': 50, 'requests_per_second': 3}
            }
        }
        
        # Distribution strategies
        self.distribution_strategies = {
            'simultaneous': 'Upload to all platforms at the same time',
            'sequential': 'Upload to platforms one by one with delays',
            'priority_based': 'Upload to high-priority platforms first',
            'engagement_optimized': 'Upload based on optimal posting times',
            'viral_cascade': 'Start with smaller platforms, then scale up'
        }
    
    async def distribute_content(
        self,
        content_id: UUID,
        user_id: UUID,
        distribution_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Distribute content across multiple platforms.
        
        Args:
            content_id: ID of content to distribute
            user_id: Content creator's user ID
            distribution_plan: Distribution configuration
            
        Returns:
            Distribution results and tracking information
        """
        try:
            # Validate distribution plan
            await self._validate_distribution_plan(distribution_plan, user_id)
            
            # Get content information
            content_info = await self.db.content.get_by_id(content_id)
            if not content_info or content_info.user_id != user_id:
                raise DistributionError("Content not found or access denied")
            
            # Create distribution job
            distribution_job = await self._create_distribution_job(
                content_id, user_id, distribution_plan
            )
            
            # Prepare content for each platform
            platform_preparations = await self._prepare_content_for_platforms(
                content_info, distribution_plan
            )
            
            # Execute distribution based on strategy
            distribution_results = await self._execute_distribution_strategy(
                distribution_job.id, platform_preparations, distribution_plan
            )
            
            # Update distribution job with results
            await self._update_distribution_job(distribution_job.id, distribution_results)
            
            # Schedule follow-up actions
            await self._schedule_post_distribution_actions(
                distribution_job.id, distribution_plan
            )
            
            result = {
                'distribution_job_id': str(distribution_job.id),
                'status': 'initiated',
                'platforms': list(distribution_plan['platforms'].keys()),
                'strategy': distribution_plan.get('strategy', 'simultaneous'),
                'scheduled_time': distribution_plan.get('scheduled_time'),
                'platform_results': distribution_results,
                'estimated_completion': self._calculate_completion_time(distribution_plan),
                'tracking_urls': await self._generate_tracking_urls(distribution_results)
            }
            
            logger.info(f"Content distribution initiated: {distribution_job.id}")
            return result
            
        except Exception as e:
            logger.error(f"Content distribution failed: {str(e)}")
            raise DistributionError(f"Failed to distribute content: {str(e)}")
    
    async def _validate_distribution_plan(
        self, 
        distribution_plan: Dict[str, Any], 
        user_id: UUID
    ) -> None:
        """Validate distribution plan and user permissions."""
        required_fields = ['platforms']
        for field in required_fields:
            if field not in distribution_plan:
                raise DistributionError(f"Missing required field: {field}")
        
        # Validate platforms
        platforms = distribution_plan['platforms']
        if not isinstance(platforms, dict) or not platforms:
            raise DistributionError("Platforms must be a non-empty dictionary")
        
        # Check platform support
        unsupported_platforms = set(platforms.keys()) - set(self.platform_configs.keys())
        if unsupported_platforms:
            raise DistributionError(f"Unsupported platforms: {list(unsupported_platforms)}")
        
        # Verify user has platform credentials
        for platform in platforms.keys():
            has_credentials = await self.platform_manager.check_user_credentials(
                user_id, platform
            )
            if not has_credentials:
                raise DistributionError(f"Missing credentials for platform: {platform}")
    
    async def _create_distribution_job(
        self,
        content_id: UUID,
        user_id: UUID,
        distribution_plan: Dict[str, Any]
    ) -> DistributionJob:
        """Create distribution job record."""
        job_data = {
            'content_id': content_id,
            'user_id': user_id,
            'platforms': list(distribution_plan['platforms'].keys()),
            'strategy': distribution_plan.get('strategy', 'simultaneous'),
            'scheduled_time': distribution_plan.get('scheduled_time'),
            'status': DistributionStatus.PENDING,
            'configuration': distribution_plan,
            'created_at': datetime.utcnow()
        }
        
        return await self.db.distribution_jobs.create(job_data)
    
    async def _prepare_content_for_platforms(
        self,
        content_info: Any,
        distribution_plan: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """Prepare content variants for each platform."""
        platform_preparations = {}
        platforms_config = distribution_plan['platforms']
        
        for platform, platform_settings in platforms_config.items():
            try:
                platform_config = self.platform_configs[platform]
                
                # Check content compliance
                compliance_result = await self._check_platform_compliance(
                    content_info, platform, platform_config
                )
                
                if not compliance_result['compliant']:
                    # Apply platform-specific optimizations
                    optimized_content = await self._optimize_content_for_platform(
                        content_info, platform, platform_config
                    )
                    content_to_use = optimized_content
                else:
                    content_to_use = content_info
                
                # Prepare metadata and settings
                platform_preparations[platform] = {
                    'content': content_to_use,
                    'metadata': self._prepare_platform_metadata(
                        platform_settings, platform_config
                    ),
                    'settings': platform_settings,
                    'compliance': compliance_result,
                    'posting_time': self._calculate_optimal_posting_time(
                        platform, platform_settings
                    )
                }
                
            except Exception as e:
                logger.error(f"Failed to prepare content for {platform}: {str(e)}")
                platform_preparations[platform] = {
                    'error': str(e),
                    'status': 'preparation_failed'
                }
        
        return platform_preparations
    
    async def _check_platform_compliance(
        self,
        content_info: Any,
        platform: str,
        platform_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if content complies with platform requirements."""
        compliance = {
            'compliant': True,
            'issues': [],
            'required_changes': []
        }
        
        # Check file size
        max_size = platform_config.get('max_file_size')
        if max_size and content_info.file_size > max_size:
            compliance['compliant'] = False
            compliance['issues'].append(f"File size exceeds {max_size} bytes")
            compliance['required_changes'].append('file_size_reduction')
        
        # Check format support
        supported_formats = platform_config.get('supported_formats', [])
        file_extension = Path(content_info.filename).suffix.lower().lstrip('.')
        if supported_formats and file_extension not in supported_formats:
            compliance['compliant'] = False
            compliance['issues'].append(f"Format {file_extension} not supported")
            compliance['required_changes'].append('format_conversion')
        
        # Check duration for video/audio
        if content_info.content_type in ['video', 'audio']:
            max_duration = platform_config.get('max_duration')
            min_duration = platform_config.get('min_duration')
            
            content_duration = content_info.metadata.get('duration', 0)
            
            if max_duration and content_duration > max_duration:
                compliance['compliant'] = False
                compliance['issues'].append(f"Duration {content_duration}s exceeds limit")
                compliance['required_changes'].append('duration_trim')
            
            if min_duration and content_duration < min_duration:
                compliance['compliant'] = False
                compliance['issues'].append(f"Duration {content_duration}s below minimum")
                compliance['required_changes'].append('duration_extend')
        
        # Check aspect ratio for images/videos
        if content_info.content_type in ['image', 'video']:
            required_ratios = platform_config.get('aspect_ratios')
            if required_ratios:
                current_ratio = content_info.metadata.get('aspect_ratio', '1:1')
                if current_ratio not in required_ratios:
                    compliance['compliant'] = False
                    compliance['issues'].append(f"Aspect ratio {current_ratio} not supported")
                    compliance['required_changes'].append('aspect_ratio_adjustment')
        
        return compliance
    
    async def _optimize_content_for_platform(
        self,
        content_info: Any,
        platform: str,
        platform_config: Dict[str, Any]
    ) -> Any:
        """Optimize content for specific platform requirements."""
        # This would interface with the MultiFormatHandler
        from .format_handler import MultiFormatHandler
        
        format_handler = MultiFormatHandler()
        
        # Determine optimization parameters
        optimization_params = {}
        
        if platform == 'instagram':
            if content_info.content_type == 'video':
                optimization_params = {
                    'max_duration': 60,
                    'aspect_ratio': '1:1',
                    'resolution': '1080x1080'
                }
        elif platform == 'tiktok':
            optimization_params = {
                'aspect_ratio': '9:16',
                'resolution': '1080x1920',
                'max_duration': 180
            }
        elif platform == 'youtube':
            optimization_params = {
                'quality': 'high',
                'resolution': '1920x1080'
            }
        
        # Apply optimizations
        optimization_result = await format_handler.handle_format(
            Path(content_info.file_path),
            content_info.content_type,
            platform_optimization=platform
        )
        
        # Return optimized content info
        optimized_files = optimization_result.get('output_files', [])
        if optimized_files:
            # Use the first optimized file
            optimized_file = optimized_files[0]
            content_info.file_path = optimized_file['file_path']
            content_info.file_size = optimized_file['size']
        
        return content_info
    
    def _prepare_platform_metadata(
        self,
        platform_settings: Dict[str, Any],
        platform_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare metadata for specific platform."""
        metadata = {}
        
        # Common metadata
        if 'title' in platform_settings:
            metadata['title'] = platform_settings['title']
        if 'description' in platform_settings:
            metadata['description'] = platform_settings['description']
        if 'tags' in platform_settings:
            metadata['tags'] = platform_settings['tags']
        
        # Platform-specific metadata
        if 'privacy' in platform_settings:
            metadata['privacy'] = platform_settings['privacy']
        if 'category' in platform_settings:
            metadata['category'] = platform_settings['category']
        if 'thumbnail' in platform_settings:
            metadata['thumbnail'] = platform_settings['thumbnail']
        
        return metadata
    
    def _calculate_optimal_posting_time(
        self,
        platform: str,
        platform_settings: Dict[str, Any]
    ) -> datetime:
        """Calculate optimal posting time for platform."""
        # If specific time is provided, use it
        if 'scheduled_time' in platform_settings:
            return datetime.fromisoformat(platform_settings['scheduled_time'])
        
        # Use platform-specific optimal times
        optimal_times = {
            'instagram': {'hour': 11, 'minute': 0},  # 11 AM
            'tiktok': {'hour': 18, 'minute': 0},     # 6 PM
            'youtube': {'hour': 14, 'minute': 0},    # 2 PM
            'twitter': {'hour': 12, 'minute': 0},    # 12 PM
            'facebook': {'hour': 15, 'minute': 0},   # 3 PM
            'linkedin': {'hour': 8, 'minute': 0},    # 8 AM
        }
        
        now = datetime.utcnow()
        optimal_time = optimal_times.get(platform, {'hour': 12, 'minute': 0})
        
        # Calculate next optimal time
        next_optimal = now.replace(
            hour=optimal_time['hour'],
            minute=optimal_time['minute'],
            second=0,
            microsecond=0
        )
        
        if next_optimal <= now:
            next_optimal += timedelta(days=1)
        
        return next_optimal
    
    async def _execute_distribution_strategy(
        self,
        distribution_job_id: UUID,
        platform_preparations: Dict[str, Dict[str, Any]],
        distribution_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute distribution based on chosen strategy."""
        strategy = distribution_plan.get('strategy', 'simultaneous')
        
        if strategy == 'simultaneous':
            return await self._execute_simultaneous_distribution(
                distribution_job_id, platform_preparations
            )
        elif strategy == 'sequential':
            return await self._execute_sequential_distribution(
                distribution_job_id, platform_preparations, distribution_plan
            )
        elif strategy == 'priority_based':
            return await self._execute_priority_based_distribution(
                distribution_job_id, platform_preparations, distribution_plan
            )
        elif strategy == 'engagement_optimized':
            return await self._execute_engagement_optimized_distribution(
                distribution_job_id, platform_preparations
            )
        else:
            raise DistributionError(f"Unknown distribution strategy: {strategy}")
    
    async def _execute_simultaneous_distribution(
        self,
        distribution_job_id: UUID,
        platform_preparations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute simultaneous distribution to all platforms."""
        results = {}
        
        # Create tasks for all platforms
        tasks = []
        for platform, preparation in platform_preparations.items():
            if 'error' not in preparation:
                task = self._upload_to_platform(platform, preparation)
                tasks.append((platform, task))
        
        # Execute all uploads concurrently
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = result
            except Exception as e:
                logger.error(f"Upload to {platform} failed: {str(e)}")
                results[platform] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _execute_sequential_distribution(
        self,
        distribution_job_id: UUID,
        platform_preparations: Dict[str, Dict[str, Any]],
        distribution_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute sequential distribution with delays."""
        results = {}
        delay_between_uploads = distribution_plan.get('sequential_delay', 300)  # 5 minutes
        
        for i, (platform, preparation) in enumerate(platform_preparations.items()):
            if 'error' not in preparation:
                # Add delay between uploads (except for first one)
                if i > 0:
                    await asyncio.sleep(delay_between_uploads)
                
                try:
                    result = await self._upload_to_platform(platform, preparation)
                    results[platform] = result
                except Exception as e:
                    logger.error(f"Upload to {platform} failed: {str(e)}")
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
        
        return results
    
    async def _execute_priority_based_distribution(
        self,
        distribution_job_id: UUID,
        platform_preparations: Dict[str, Dict[str, Any]],
        distribution_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute distribution based on platform priorities."""
        results = {}
        
        # Get platform priorities
        platform_priorities = distribution_plan.get('platform_priorities', {})
        
        # Sort platforms by priority
        sorted_platforms = sorted(
            platform_preparations.items(),
            key=lambda x: platform_priorities.get(x[0], 5),  # Default priority 5
            reverse=True
        )
        
        # Execute high priority platforms first, then batch lower priority
        high_priority_tasks = []
        medium_priority_tasks = []
        low_priority_tasks = []
        
        for platform, preparation in sorted_platforms:
            if 'error' not in preparation:
                priority = platform_priorities.get(platform, 5)
                task = self._upload_to_platform(platform, preparation)
                
                if priority >= 8:
                    high_priority_tasks.append((platform, task))
                elif priority >= 5:
                    medium_priority_tasks.append((platform, task))
                else:
                    low_priority_tasks.append((platform, task))
        
        # Execute in batches
        for batch_name, tasks in [
            ('high_priority', high_priority_tasks),
            ('medium_priority', medium_priority_tasks),
            ('low_priority', low_priority_tasks)
        ]:
            for platform, task in tasks:
                try:
                    result = await task
                    results[platform] = result
                except Exception as e:
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            
            # Small delay between priority batches
            if tasks and batch_name != 'low_priority':
                await asyncio.sleep(60)  # 1 minute delay
        
        return results
    
    async def _execute_engagement_optimized_distribution(
        self,
        distribution_job_id: UUID,
        platform_preparations: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute distribution at optimal engagement times."""
        results = {}
        
        # Schedule uploads at optimal times
        scheduled_uploads = []
        
        for platform, preparation in platform_preparations.items():
            if 'error' not in preparation:
                optimal_time = preparation['posting_time']
                scheduled_uploads.append((optimal_time, platform, preparation))
        
        # Sort by posting time
        scheduled_uploads.sort(key=lambda x: x[0])
        
        # Schedule or execute uploads
        for posting_time, platform, preparation in scheduled_uploads:
            current_time = datetime.utcnow()
            
            if posting_time <= current_time:
                # Execute immediately
                try:
                    result = await self._upload_to_platform(platform, preparation)
                    results[platform] = result
                except Exception as e:
                    results[platform] = {
                        'status': 'failed',
                        'error': str(e),
                        'timestamp': datetime.utcnow().isoformat()
                    }
            else:
                # Schedule for later
                await self.scheduler.schedule_task(
                    task_name=f"upload_{distribution_job_id}_{platform}",
                    scheduled_time=posting_time,
                    task_data={
                        'platform': platform,
                        'preparation': preparation,
                        'distribution_job_id': str(distribution_job_id)
                    }
                )
                results[platform] = {
                    'status': 'scheduled',
                    'scheduled_time': posting_time.isoformat(),
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        return results
    
    async def _upload_to_platform(
        self,
        platform: str,
        preparation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload content to specific platform."""
        try:
            # Respect API rate limits
            await self._check_rate_limits(platform)
            
            # Execute platform-specific upload
            if platform == 'youtube':
                result = await self._upload_to_youtube(preparation)
            elif platform == 'instagram':
                result = await self._upload_to_instagram(preparation)
            elif platform == 'tiktok':
                result = await self._upload_to_tiktok(preparation)
            elif platform == 'twitter':
                result = await self._upload_to_twitter(preparation)
            elif platform == 'facebook':
                result = await self._upload_to_facebook(preparation)
            elif platform == 'linkedin':
                result = await self._upload_to_linkedin(preparation)
            elif platform == 'spotify':
                result = await self._upload_to_spotify(preparation)
            elif platform == 'soundcloud':
                result = await self._upload_to_soundcloud(preparation)
            else:
                raise DistributionError(f"Upload handler not implemented for {platform}")
            
            # Update rate limit tracking
            await self._update_rate_limit_tracking(platform)
            
            return {
                'status': 'success',
                'platform_response': result,
                'timestamp': datetime.utcnow().isoformat(),
                'content_url': result.get('url'),
                'platform_id': result.get('id')
            }
            
        except Exception as e:
            logger.error(f"Upload to {platform} failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def _check_rate_limits(self, platform: str) -> None:
        """Check and enforce API rate limits."""
        platform_config = self.platform_configs.get(platform, {})
        api_limits = platform_config.get('api_limits', {})
        
        # This would check against rate limit tracking in database
        # For now, we'll add a small delay
        await asyncio.sleep(1)
    
    async def _update_rate_limit_tracking(self, platform: str) -> None:
        """Update rate limit tracking after API call."""
        # This would update rate limit counters in database
        pass
    
    # Platform-specific upload methods
    async def _upload_to_youtube(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to YouTube."""
        # This would use YouTube Data API
        return await self.platform_manager.upload_to_youtube(preparation)
    
    async def _upload_to_instagram(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to Instagram."""
        # This would use Instagram Basic Display API
        return await self.platform_manager.upload_to_instagram(preparation)
    
    async def _upload_to_tiktok(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to TikTok."""
        # This would use TikTok API
        return await self.platform_manager.upload_to_tiktok(preparation)
    
    async def _upload_to_twitter(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to Twitter."""
        # This would use Twitter API v2
        return await self.platform_manager.upload_to_twitter(preparation)
    
    async def _upload_to_facebook(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to Facebook."""
        # This would use Facebook Graph API
        return await self.platform_manager.upload_to_facebook(preparation)
    
    async def _upload_to_linkedin(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to LinkedIn."""
        # This would use LinkedIn API
        return await self.platform_manager.upload_to_linkedin(preparation)
    
    async def _upload_to_spotify(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to Spotify."""
        # This would use Spotify Web API
        return await self.platform_manager.upload_to_spotify(preparation)
    
    async def _upload_to_soundcloud(self, preparation: Dict[str, Any]) -> Dict[str, Any]:
        """Upload content to SoundCloud."""
        # This would use SoundCloud API
        return await self.platform_manager.upload_to_soundcloud(preparation)
    
    async def _update_distribution_job(
        self,
        distribution_job_id: UUID,
        distribution_results: Dict[str, Any]
    ) -> None:
        """Update distribution job with results."""
        # Calculate overall status
        successful_uploads = sum(1 for result in distribution_results.values() 
                               if result.get('status') == 'success')
        total_uploads = len(distribution_results)
        
        if successful_uploads == total_uploads:
            status = DistributionStatus.COMPLETED
        elif successful_uploads > 0:
            status = DistributionStatus.PARTIAL
        else:
            status = DistributionStatus.FAILED
        
        update_data = {
            'status': status,
            'results': distribution_results,
            'completed_at': datetime.utcnow(),
            'success_rate': successful_uploads / total_uploads if total_uploads > 0 else 0
        }
        
        await self.db.distribution_jobs.update(distribution_job_id, update_data)
    
    async def _schedule_post_distribution_actions(
        self,
        distribution_job_id: UUID,
        distribution_plan: Dict[str, Any]
    ) -> None:
        """Schedule follow-up actions after distribution."""
        post_actions = distribution_plan.get('post_distribution_actions', {})
        
        # Schedule analytics collection
        if post_actions.get('collect_analytics', True):
            analytics_delay = post_actions.get('analytics_delay_hours', 24)
            analytics_time = datetime.utcnow() + timedelta(hours=analytics_delay)
            
            await self.scheduler.schedule_task(
                task_name=f"collect_analytics_{distribution_job_id}",
                scheduled_time=analytics_time,
                task_data={
                    'distribution_job_id': str(distribution_job_id),
                    'action': 'collect_analytics'
                }
            )
        
        # Schedule engagement monitoring
        if post_actions.get('monitor_engagement', True):
            monitoring_intervals = [1, 6, 24, 48, 168]  # Hours
            for interval in monitoring_intervals:
                monitoring_time = datetime.utcnow() + timedelta(hours=interval)
                
                await self.scheduler.schedule_task(
                    task_name=f"monitor_engagement_{distribution_job_id}_{interval}h",
                    scheduled_time=monitoring_time,
                    task_data={
                        'distribution_job_id': str(distribution_job_id),
                        'action': 'monitor_engagement',
                        'interval_hours': interval
                    }
                )
    
    def _calculate_completion_time(self, distribution_plan: Dict[str, Any]) -> datetime:
        """Calculate estimated completion time."""
        strategy = distribution_plan.get('strategy', 'simultaneous')
        platform_count = len(distribution_plan['platforms'])
        
        if strategy == 'simultaneous':
            # Assume 5 minutes max for simultaneous uploads
            completion_time = datetime.utcnow() + timedelta(minutes=5)
        elif strategy == 'sequential':
            delay_between = distribution_plan.get('sequential_delay', 300)  # seconds
            total_time = platform_count * delay_between + 300  # Add 5 min buffer
            completion_time = datetime.utcnow() + timedelta(seconds=total_time)
        else:
            # Default to 30 minutes for other strategies
            completion_time = datetime.utcnow() + timedelta(minutes=30)
        
        return completion_time
    
    async def _generate_tracking_urls(
        self, 
        distribution_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate tracking URLs for uploaded content."""
        tracking_urls = {}
        
        for platform, result in distribution_results.items():
            if result.get('status') == 'success':
                platform_response = result.get('platform_response', {})
                content_url = platform_response.get('url')
                if content_url:
                    tracking_urls[platform] = content_url
        
        return tracking_urls
    
    async def get_distribution_status(
        self, 
        distribution_job_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get distribution job status."""
        job = await self.db.distribution_jobs.get_by_id(distribution_job_id)
        if not job or job.user_id != user_id:
            raise DistributionError("Distribution job not found or access denied")
        
        return {
            'job_id': str(distribution_job_id),
            'status': job.status.value,
            'platforms': job.platforms,
            'strategy': job.strategy,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'success_rate': job.success_rate,
            'results': job.results or {},
            'progress': self._calculate_progress(job)
        }
    
    def _calculate_progress(self, job: DistributionJob) -> int:
        """Calculate distribution progress percentage."""
        if job.status == DistributionStatus.PENDING:
            return 0
        elif job.status == DistributionStatus.IN_PROGRESS:
            return 50
        elif job.status in [DistributionStatus.COMPLETED, DistributionStatus.PARTIAL, DistributionStatus.FAILED]:
            return 100
        else:
            return 25
    
    async def cancel_distribution(
        self, 
        distribution_job_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """Cancel pending distribution job."""
        job = await self.db.distribution_jobs.get_by_id(distribution_job_id)
        if not job or job.user_id != user_id:
            raise DistributionError("Distribution job not found or access denied")
        
        if job.status not in [DistributionStatus.PENDING, DistributionStatus.IN_PROGRESS]:
            raise DistributionError("Cannot cancel completed distribution")
        
        # Cancel scheduled tasks
        await self.scheduler.cancel_tasks_by_prefix(f"upload_{distribution_job_id}")
        
        # Update job status
        await self.db.distribution_jobs.update(distribution_job_id, {
            'status': DistributionStatus.CANCELLED,
            'cancelled_at': datetime.utcnow()
        })
        
        return {
            'job_id': str(distribution_job_id),
            'status': 'cancelled',
            'message': 'Distribution job cancelled successfully'
        }
    
    async def get_platform_analytics(
        self, 
        distribution_job_id: UUID, 
        user_id: UUID
    ) -> Dict[str, Any]:
        """Get analytics for distributed content."""
        job = await self.db.distribution_jobs.get_by_id(distribution_job_id)
        if not job or job.user_id != user_id:
            raise DistributionError("Distribution job not found or access denied")
        
        analytics = {}
        
        for platform in job.platforms:
            try:
                platform_analytics = await self.platform_manager.get_content_analytics(
                    platform, job.results.get(platform, {}).get('platform_id')
                )
                analytics[platform] = platform_analytics
            except Exception as e:
                logger.error(f"Failed to get analytics for {platform}: {str(e)}")
                analytics[platform] = {'error': str(e)}
        
        return {
            'distribution_job_id': str(distribution_job_id),
            'analytics_timestamp': datetime.utcnow().isoformat(),
            'platform_analytics': analytics,
            'summary': self._generate_analytics_summary(analytics)
        }
    
    def _generate_analytics_summary(
        self, 
        platform_analytics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate analytics summary across platforms."""
        total_views = 0
        total_engagement = 0
        total_shares = 0
        successful_platforms = 0
        
        for platform, analytics in platform_analytics.items():
            if 'error' not in analytics:
                total_views += analytics.get('views', 0)
                total_engagement += analytics.get('engagement', 0)
                total_shares += analytics.get('shares', 0)
                successful_platforms += 1
        
        return {
            'total_views': total_views,
            'total_engagement': total_engagement,
            'total_shares': total_shares,
            'platforms_count': successful_platforms,
            'average_views_per_platform': total_views / successful_platforms if successful_platforms > 0 else 0,
            'engagement_rate': total_engagement / total_views if total_views > 0 else 0
        }
    
    async def get_supported_platforms(self) -> Dict[str, Any]:
        """Get list of supported platforms and their configurations."""
        return {
            platform: {
                'name': platform.title(),
                'supported_formats': config.get('supported_formats', []),
                'max_file_size': config.get('max_file_size'),
                'max_duration': config.get('max_duration'),
                'features': self._get_platform_features(platform)
            }
            for platform, config in self.platform_configs.items()
        }
    
    def _get_platform_features(self, platform: str) -> List[str]:
        """Get list of features supported by platform."""
        features_map = {
            'youtube': ['video', 'audio', 'live_streaming', 'shorts', 'monetization'],
            'instagram': ['image', 'video', 'stories', 'reels', 'shopping'],
            'tiktok': ['video', 'effects', 'duets', 'sounds'],
            'twitter': ['text', 'image', 'video', 'threads', 'spaces'],
            'facebook': ['text', 'image', 'video', 'live', 'events'],
            'linkedin': ['text', 'image', 'video', 'articles', 'professional'],
            'spotify': ['audio', 'podcasts', 'playlists'],
            'soundcloud': ['audio', 'waveform', 'comments', 'reposts']
        }
        
        return features_map.get(platform, ['basic_upload'])
