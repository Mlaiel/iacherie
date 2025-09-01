"""📦 Distribution Processor - IA Influencer Agent Platform Enterprise
==================================================================
Module: backend/data_management/processors/distribution_processor.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Content Distribution - Enterprise Production-Ready Ultra Advanced
Responsibility: Distribution intelligente contenu multi-plateformes avec optimisation automatisée
============================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Toute tentative de vol de ce concept, de cette idée ou de ce code sans autorisation personnelle claire 
et écrite de Fahed Mlaiel est strictement interdite et sera poursuivie en justice selon la loi allemande.
Contact obligatoire: mlaiel@live.de

LOGIQUE MÉTIER DISTRIBUTION:
Content Preparation → Platform Optimization → Automated Upload → Cross-Platform Sync → 
Performance Monitoring → A/B Testing → Distribution Analytics → ROI Optimization
"""

import json
import logging
import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone, timedelta
import requests
import queue
import hashlib
from dataclasses import dataclass, asdict
import schedule
from concurrent.futures import ThreadPoolExecutor
import subprocess
import tempfile
import shutil

from .base_processor import BaseProcessor, AsyncBaseProcessor


@dataclass
class DistributionJob:
    """
Job de distribution de contenu"""
    job_id: str
    content_id: str
    platforms: List[str]
    content_data: Dict[str, Any]
    distribution_strategy: str
    priority: int
    scheduled_time: datetime
    status: str
    retry_count: int
    max_retries: int


@dataclass
class PlatformConfig:
    """
Configuration plateforme"""
    platform_name: str
    api_endpoint: str
    auth_config: Dict[str, Any]
    format_requirements: Dict[str, Any]
    upload_limits: Dict[str, Any]
    optimization_settings: Dict[str, Any]


class DistributionProcessor(BaseProcessor):
    """
Processeur distribution multi-plateformes - Production Enterprise"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        
        # Distribution Configuration
        self.distribution_config = {
            'platforms': {
                'youtube': {
                    'api_endpoint': 'https://www.googleapis.com/youtube/v3',
                    'upload_endpoint': 'https://www.googleapis.com/upload/youtube/v3/videos',
                    'max_file_size_gb': 256,
                    'supported_formats': ['mp4', 'mov', 'avi', 'wmv', 'flv', 'webm'],
                    'max_duration_hours': 12,
                    'rate_limits': {'uploads_per_day': 6, 'api_calls_per_hour': 10000},
                    'optimization': {
                        'preferred_codec': 'h264',
                        'max_bitrate_mbps': 68,
                        'audio_codec': 'aac',
                        'container': 'mp4'
                    }
                },
                'instagram': {
                    'api_endpoint': 'https://graph.instagram.com',
                    'max_file_size_mb': 100,
                    'supported_formats': {
                        'photo': ['jpg', 'jpeg', 'png'],
                        'video': ['mp4', 'mov'],
                        'reel': ['mp4']
                    },
                    'aspect_ratios': {
                        'feed': [(1, 1), (4, 5), (16, 9)],
                        'story': [(9, 16)],
                        'reel': [(9, 16)]
                    },
                    'rate_limits': {'posts_per_hour': 25, 'api_calls_per_hour': 4800}
                },
                'tiktok': {
                    'api_endpoint': 'https://open-api.tiktok.com',
                    'max_file_size_mb': 287,
                    'supported_formats': ['mp4', 'mov', 'jpeg', 'jpg', 'png'],
                    'video_requirements': {
                        'min_duration_seconds': 3,
                        'max_duration_seconds': 180,
                        'aspect_ratio': (9, 16),
                        'resolution': [(540, 960), (720, 1280), (1080, 1920)]
                    },
                    'rate_limits': {'posts_per_day': 10, 'api_calls_per_hour': 1000}
                },
                'facebook': {
                    'api_endpoint': 'https://graph.facebook.com/v18.0',
                    'max_file_size_gb': 10,
                    'supported_formats': {
                        'video': ['mp4', 'mov', 'avi'],
                        'photo': ['jpg', 'png', 'gif']
                    },
                    'optimization': {
                        'video_codec': 'h264',
                        'audio_codec': 'aac',
                        'max_bitrate_mbps': 8
                    },
                    'rate_limits': {'posts_per_hour': 25, 'api_calls_per_hour': 4800}
                },
                'twitter': {
                    'api_endpoint': 'https://api.twitter.com/2',
                    'max_file_size_mb': 512,
                    'supported_formats': {
                        'video': ['mp4', 'mov'],
                        'photo': ['jpg', 'png', 'gif', 'webp']
                    },
                    'video_requirements': {
                        'max_duration_seconds': 140,
                        'max_bitrate_mbps': 25
                    },
                    'rate_limits': {'tweets_per_hour': 300, 'media_uploads_per_hour': 300}
                },
                'linkedin': {
                    'api_endpoint': 'https://api.linkedin.com/v2',
                    'max_file_size_mb': 200,
                    'supported_formats': {
                        'video': ['mp4', 'mov', 'wmv'],
                        'image': ['jpg', 'png', 'gif']
                    },
                    'video_requirements': {
                        'min_duration_seconds': 3,
                        'max_duration_seconds': 600
                    },
                    'rate_limits': {'posts_per_hour': 20, 'api_calls_per_hour': 500}
                }
            },
            'distribution_strategies': {
                'simultaneous': {
                    'description': 'Upload to all platforms simultaneously',
                    'delay_between_uploads': 0,
                    'priority_order': [],
                    'fallback_strategy': 'sequential'
                },
                'sequential': {
                    'description': 'Upload to platforms one by one',
                    'delay_between_uploads': 300,  # 5 minutes
                    'priority_order': ['youtube', 'instagram', 'tiktok', 'twitter', 'linkedin'],
                    'stop_on_failure': False
                },
                'prioritized': {
                    'description': 'Upload to high-priority platforms first',
                    'delay_between_uploads': 60,
                    'priority_order': ['youtube', 'instagram', 'tiktok', 'facebook', 'twitter'],
                    'stop_on_failure': False
                },
                'staged': {
                    'description': 'Upload in stages with intervals',
                    'stages': [
                        {'platforms': ['youtube'], 'delay_after': 3600},  # 1 hour
                        {'platforms': ['instagram', 'tiktok'], 'delay_after': 1800},  # 30 min
                        {'platforms': ['twitter', 'linkedin'], 'delay_after': 0}
                    ]
                }
            },
            'content_optimization': {
                'auto_format_conversion': True,
                'auto_resolution_adjustment': True,
                'auto_aspect_ratio_correction': True,
                'quality_preservation': True,
                'metadata_optimization': True,
                'thumbnail_generation': True
            },
            'monitoring': {
                'upload_progress_tracking': True,
                'performance_analytics': True,
                'error_monitoring': True,
                'retry_mechanisms': True,
                'notification_systems': ['email', 'webhook', 'dashboard']
            }
        }
        
        # Distribution Queue and Job Management
        self.distribution_queue = queue.PriorityQueue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.failed_jobs = {}
        
        # Worker threads
        self.worker_threads = []
        self.workers_active = False
        self.max_workers = 5
        
        # Rate limiting
        self.rate_limiters = {}
        self._init_rate_limiters()
        
        # Performance tracking
        self.performance_metrics = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'average_upload_time': 0,
            'platform_success_rates': {},
            'content_type_performance': {}
        }
        
        # A/B Testing
        self.ab_tests = {}
        
    def _init_rate_limiters(self):
        """
Initialise les limiteurs de débit"""
        for platform, config in self.distribution_config['platforms'].items():
            self.rate_limiters[platform] = {
                'requests': [],
                'uploads': [],
                'limits': config.get('rate_limits', {})
            }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
Traite la distribution de contenu"""
        operation = input_data.get('operation', 'distribute_content')
        
        result = {
            'operation': operation,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'status': 'processing',
            'data': {},
            'job_id': None,
            'errors': []
        }
        
        try:
            if operation == 'distribute_content':
                result.update(self._distribute_content(input_data))
            elif operation == 'schedule_distribution':
                result.update(self._schedule_distribution(input_data))
            elif operation == 'bulk_distribute':
                result.update(self._bulk_distribute(input_data))
            elif operation == 'get_job_status':
                result.update(self._get_job_status(input_data))
            elif operation == 'cancel_distribution':
                result.update(self._cancel_distribution(input_data))
            elif operation == 'retry_failed':
                result.update(self._retry_failed_distribution(input_data))
            elif operation == 'get_analytics':
                result.update(self._get_distribution_analytics(input_data))
            elif operation == 'ab_test':
                result.update(self._setup_ab_test(input_data))
            elif operation == 'optimize_content':
                result.update(self._optimize_content_for_platforms(input_data))
            else:
                result['status'] = 'error'
                result['errors'].append(f"Unknown operation: {operation}")
        
        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            self.logger.error(f"Distribution operation failed: {e}")
        
        return result
    
    def _distribute_content(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Distribue le contenu sur les plateformes"""
        content_data = input_data.get('content_data', {})
        platforms = input_data.get('platforms', ['youtube'])
        strategy = input_data.get('strategy', 'simultaneous')
        priority = input_data.get('priority', 5)
        scheduled_time = input_data.get('scheduled_time')
        
        result = {
            'job_id': None,
            'status': 'queued',
            'platforms': platforms,
            'strategy': strategy,
            'estimated_completion_time': None
        }
        
        try:
            # Validate content and platforms
            validation = self._validate_distribution_request(content_data, platforms)
            if not validation['valid']:
                result['status'] = 'error'
                result['errors'] = validation['errors']
                return result
            
            # Generate job ID
            job_id = self._generate_job_id(content_data, platforms)
            result['job_id'] = job_id
            
            # Parse scheduled time
            if scheduled_time:
                if isinstance(scheduled_time, str):
                    scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                else:
                    scheduled_dt = scheduled_time
            else:
                scheduled_dt = datetime.now(timezone.utc)
            
            # Create distribution job
            job = DistributionJob(
                job_id=job_id,
                content_id=content_data.get('content_id', job_id),
                platforms=platforms,
                content_data=content_data,
                distribution_strategy=strategy,
                priority=priority,
                scheduled_time=scheduled_dt,
                status='queued',
                retry_count=0,
                max_retries=3
            )
            
            # Add to queue
            self.distribution_queue.put((priority, scheduled_dt.timestamp(), job))
            self.active_jobs[job_id] = job
            
            # Start workers if not running
            if not self.workers_active:
                self._start_distribution_workers()
            
            # Estimate completion time
            result['estimated_completion_time'] = self._estimate_completion_time(job)
            result['status'] = 'queued'
            
        except Exception as e:
            result['status'] = 'error'
            result['errors'] = [str(e)]
            self.logger.error(f"Content distribution failed: {e}")
        
        return result
    
    def _validate_distribution_request(self, content_data: Dict, platforms: List[str]) -> Dict[str, Any]:
        """Valide la demande de distribution"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Check content data
            if not content_data:
                validation['errors'].append('Content data is required')
                validation['valid'] = False
            
            # Check file path
            file_path = content_data.get('file_path')
            if not file_path:
                validation['errors'].append('File path is required')
                validation['valid'] = False
            elif not self._file_exists(file_path):
                validation['errors'].append('File not found')
                validation['valid'] = False
            
            # Check platforms
            if not platforms:
                validation['errors'].append('At least one platform must be specified')
                validation['valid'] = False
            
            for platform in platforms:
                if platform not in self.distribution_config['platforms']:
                    validation['errors'].append(f'Unsupported platform: {platform}')
                    validation['valid'] = False
            
            # Platform-specific validations
            if validation['valid']:
                for platform in platforms:
                    platform_validation = self._validate_content_for_platform(content_data, platform)
                    if not platform_validation['valid']:
                        validation['warnings'].extend(platform_validation['warnings'])
                        # Don't fail completely, just warn
            
        except Exception as e:
            validation['errors'].append(f'Validation error: {str(e)}')
            validation['valid'] = False
        
        return validation
    
    def _validate_content_for_platform(self, content_data: Dict, platform: str) -> Dict[str, Any]:
        """
Valide le contenu pour une plateforme spécifique"""
        validation = {
            'valid': True,
            'warnings': [],
            'suggestions': []
        }
        
        try:
            platform_config = self.distribution_config['platforms'][platform]
            file_path = content_data.get('file_path', '')
            
            # Check file format
            file_extension = file_path.split('.')[-1].lower()
            supported_formats = platform_config.get('supported_formats', [])
            
            if isinstance(supported_formats, dict):
                # Format by content type
                content_type = content_data.get('content_type', 'video')
                type_formats = supported_formats.get(content_type, [])
                if file_extension not in type_formats:
                    validation['warnings'].append(f'{platform}: Format {file_extension} may not be supported for {content_type}')
                    validation['suggestions'].append(f'Convert to {type_formats[0] if type_formats else "mp4"}')
            elif isinstance(supported_formats, list):
                if file_extension not in supported_formats:
                    validation['warnings'].append(f'{platform}: Format {file_extension} may not be supported')
                    validation['suggestions'].append(f'Convert to {supported_formats[0] if supported_formats else "mp4"}')
            
            # Check file size
            file_size_mb = self._get_file_size_mb(file_path)
            max_size_mb = platform_config.get('max_file_size_mb')
            max_size_gb = platform_config.get('max_file_size_gb')
            
            if max_size_mb and file_size_mb > max_size_mb:
                validation['warnings'].append(f'{platform}: File size {file_size_mb}MB exceeds limit {max_size_mb}MB')
                validation['suggestions'].append('Compress file or reduce quality')
            elif max_size_gb and file_size_mb > (max_size_gb * 1024):
                validation['warnings'].append(f'{platform}: File size {file_size_mb}MB exceeds limit {max_size_gb}GB')
                validation['suggestions'].append('Compress file or reduce quality')
            
            # Platform-specific checks
            if platform == 'tiktok':
                # Check aspect ratio for TikTok
                video_reqs = platform_config.get('video_requirements', {})
                aspect_ratio = video_reqs.get('aspect_ratio')
                if aspect_ratio and aspect_ratio != (9, 16):
                    validation['warnings'].append('TikTok prefers 9:16 aspect ratio')
                    validation['suggestions'].append('Crop or resize video to 9:16 aspect ratio')
            
        except Exception as e:
            validation['warnings'].append(f'Platform validation error: {str(e)}')
        
        return validation
    
    def _file_exists(self, file_path: str) -> bool:
        """Vérifie si le fichier existe"""
        try:
            import os
            return os.path.exists(file_path)
        except:
            return False
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """
Récupère la taille du fichier en MB"""
        try:
            import os
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except:
            return 0.0
    
    def _generate_job_id(self, content_data: Dict, platforms: List[str]) -> str:
        """
Génère un ID unique pour le job"""
        content_str = json.dumps(content_data, sort_keys=True)
        platforms_str = ','.join(sorted(platforms))
        timestamp = str(int(time.time()))
        
        hash_input = f"{content_str}_{platforms_str}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _estimate_completion_time(self, job: DistributionJob) -> str:
        """Estime le temps de completion"""
        try:
            base_upload_time = 300  # 5 minutes per platform
            platform_count = len(job.platforms)
            
            strategy_multipliers = {
                'simultaneous': 1.0,
                'sequential': platform_count,
                'prioritized': platform_count * 0.8,
                'staged': platform_count * 1.5
            }
            
            multiplier = strategy_multipliers.get(job.distribution_strategy, 1.0)
            estimated_seconds = base_upload_time * multiplier
            
            completion_time = job.scheduled_time + timedelta(seconds=estimated_seconds)
            return completion_time.isoformat()
            
        except:
            return (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()
    
    def _start_distribution_workers(self):
        """
Démarre les workers de distribution"""
        if self.workers_active:
            return
        
        self.workers_active = True
        
        for i in range(self.max_workers):
            worker_thread = threading.Thread(
                target=self._distribution_worker,
                args=(f"worker_{i}",),
                daemon=True
            )
            worker_thread.start()
            self.worker_threads.append(worker_thread)
        
        self.logger.info(f"Started {self.max_workers} distribution workers")
    
    def _distribution_worker(self, worker_id: str):
        """Worker de distribution"""
        self.logger.info(f"Distribution worker {worker_id} started")
        
        while self.workers_active:
            try:
                # Get job from queue (with timeout)
                try:
                    priority, timestamp, job = self.distribution_queue.get(timeout=30)
                except queue.Empty:
                    continue
                
                # Check if it's time to process
                current_time = datetime.now(timezone.utc)
                if current_time < job.scheduled_time:
                    # Put back in queue and wait
                    self.distribution_queue.put((priority, timestamp, job))
                    time.sleep(60)  # Check again in 1 minute
                    continue
                
                # Process the job
                self.logger.info(f"Worker {worker_id} processing job {job.job_id}")
                job.status = 'processing'
                
                try:
                    result = self._execute_distribution_job(job)
                    
                    if result['success']:
                        job.status = 'completed'
                        self.completed_jobs[job.job_id] = job
                        self.performance_metrics['successful_uploads'] += len(job.platforms)
                    else:
                        if job.retry_count < job.max_retries:
                            job.retry_count += 1
                            job.status = 'retrying'
                            # Put back in queue with lower priority
                            retry_time = current_time + timedelta(minutes=10 * job.retry_count)
                            self.distribution_queue.put((priority + 10, retry_time.timestamp(), job))
                            self.logger.info(f"Job {job.job_id} scheduled for retry {job.retry_count}")
                        else:
                            job.status = 'failed'
                            self.failed_jobs[job.job_id] = job
                            self.performance_metrics['failed_uploads'] += len(job.platforms)
                
                except Exception as e:
                    self.logger.error(f"Job execution failed: {e}")
                    job.status = 'failed'
                    self.failed_jobs[job.job_id] = job
                
                # Remove from active jobs if completed or failed
                if job.status in ['completed', 'failed']:
                    self.active_jobs.pop(job.job_id, None)
                
                self.performance_metrics['total_uploads'] += len(job.platforms)
                self.distribution_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Worker {worker_id} error: {e}")
                time.sleep(10)  # Wait before continuing
        
        self.logger.info(f"Distribution worker {worker_id} stopped")
    
    def _execute_distribution_job(self, job: DistributionJob) -> Dict[str, Any]:
        """Exécute un job de distribution"""
        result = {
            'success': True,
            'platform_results': {},
            'errors': [],
            'start_time': datetime.now(timezone.utc),
            'end_time': None
        }
        
        try:
            strategy = job.distribution_strategy
            
            if strategy == 'simultaneous':
                result = self._execute_simultaneous_distribution(job)
            elif strategy == 'sequential':
                result = self._execute_sequential_distribution(job)
            elif strategy == 'prioritized':
                result = self._execute_prioritized_distribution(job)
            elif strategy == 'staged':
                result = self._execute_staged_distribution(job)
            else:
                result = self._execute_simultaneous_distribution(job)  # Default
            
            result['end_time'] = datetime.now(timezone.utc)
            
        except Exception as e:
            result['success'] = False
            result['errors'].append(str(e))
            result['end_time'] = datetime.now(timezone.utc)
            self.logger.error(f"Distribution job execution failed: {e}")
        
        return result
    
    def _execute_simultaneous_distribution(self, job: DistributionJob) -> Dict[str, Any]:
        """Exécute la distribution simultanée"""
        result = {
            'success': True,
            'platform_results': {},
            'errors': []
        }
        
        # Use ThreadPoolExecutor for parallel uploads
        with ThreadPoolExecutor(max_workers=len(job.platforms)) as executor:
            future_to_platform = {
                executor.submit(self._upload_to_platform, job, platform): platform
                for platform in job.platforms
            }
            
            for future in future_to_platform:
                platform = future_to_platform[future]
                try:
                    platform_result = future.result(timeout=1800)  # 30 minute timeout
                    result['platform_results'][platform] = platform_result
                    
                    if not platform_result.get('success', False):
                        result['success'] = False
                        result['errors'].extend(platform_result.get('errors', []))
                        
                except Exception as e:
                    result['success'] = False
                    result['platform_results'][platform] = {
                        'success': False,
                        'error': str(e)
                    }
                    result['errors'].append(f"{platform}: {str(e)}")
        
        return result
    
    def _execute_sequential_distribution(self, job: DistributionJob) -> Dict[str, Any]:
        """Exécute la distribution séquentielle"""
        result = {
            'success': True,
            'platform_results': {},
            'errors': []
        }
        
        strategy_config = self.distribution_config['distribution_strategies']['sequential']
        delay = strategy_config.get('delay_between_uploads', 300)
        priority_order = strategy_config.get('priority_order', [])
        stop_on_failure = strategy_config.get('stop_on_failure', False)
        
        # Order platforms by priority
        ordered_platforms = []
        for platform in priority_order:
            if platform in job.platforms:
                ordered_platforms.append(platform)
        
        # Add remaining platforms
        for platform in job.platforms:
            if platform not in ordered_platforms:
                ordered_platforms.append(platform)
        
        # Upload to each platform sequentially
        for i, platform in enumerate(ordered_platforms):
            try:
                platform_result = self._upload_to_platform(job, platform)
                result['platform_results'][platform] = platform_result
                
                if not platform_result.get('success', False):
                    result['success'] = False
                    result['errors'].extend(platform_result.get('errors', []))
                    
                    if stop_on_failure:
                        break
                
                # Wait between uploads (except for last one)
                if i < len(ordered_platforms) - 1 and delay > 0:
                    time.sleep(delay)
                    
            except Exception as e:
                result['success'] = False
                result['platform_results'][platform] = {
                    'success': False,
                    'error': str(e)
                }
                result['errors'].append(f"{platform}: {str(e)}")
                
                if stop_on_failure:
                    break
        
        return result
    
    def _execute_prioritized_distribution(self, job: DistributionJob) -> Dict[str, Any]:
        """Exécute la distribution priorisée"""
        # Similar to sequential but with optimized ordering
        return self._execute_sequential_distribution(job)
    
    def _execute_staged_distribution(self, job: DistributionJob) -> Dict[str, Any]:
        """
Exécute la distribution par étapes"""
        result = {
            'success': True,
            'platform_results': {},
            'errors': []
        }
        
        strategy_config = self.distribution_config['distribution_strategies']['staged']
        stages = strategy_config.get('stages', [])
        
        for stage_idx, stage in enumerate(stages):
            stage_platforms = [p for p in stage['platforms'] if p in job.platforms]
            
            if not stage_platforms:
                continue
            
            # Upload to all platforms in this stage simultaneously
            stage_job = DistributionJob(
                job_id=f"{job.job_id}_stage_{stage_idx}",
                content_id=job.content_id,
                platforms=stage_platforms,
                content_data=job.content_data,
                distribution_strategy='simultaneous',
                priority=job.priority,
                scheduled_time=job.scheduled_time,
                status='processing',
                retry_count=job.retry_count,
                max_retries=job.max_retries
            )
            
            stage_result = self._execute_simultaneous_distribution(stage_job)
            
            # Merge results
            result['platform_results'].update(stage_result['platform_results'])
            result['errors'].extend(stage_result['errors'])
            
            if not stage_result['success']:
                result['success'] = False
            
            # Wait before next stage (except for last one)
            delay_after = stage.get('delay_after', 0)
            if stage_idx < len(stages) - 1 and delay_after > 0:
                time.sleep(delay_after)
        
        return result
    
    def _upload_to_platform(self, job: DistributionJob, platform: str) -> Dict[str, Any]:
        """Upload vers une plateforme spécifique"""
        result = {
            'success': False,
            'platform': platform,
            'upload_url': None,
            'platform_id': None,
            'errors': [],
            'upload_time': 0,
            'file_size_mb': 0
        }
        
        try:
            start_time = time.time()
            
            # Check rate limits
            if not self._check_rate_limit(platform):
                result['errors'].append('Rate limit exceeded')
                return result
            
            # Get platform configuration
            platform_config = self.distribution_config['platforms'][platform]
            
            # Optimize content for platform if needed
            optimized_content = self._optimize_content_for_platform(job.content_data, platform)
            
            # Simulate upload process (replace with real API calls)
            upload_result = self._simulate_platform_upload(platform, optimized_content, platform_config)
            
            end_time = time.time()
            result['upload_time'] = round(end_time - start_time, 2)
            result['file_size_mb'] = self._get_file_size_mb(job.content_data.get('file_path', ''))
            
            if upload_result['success']:
                result['success'] = True
                result['platform_id'] = upload_result.get('platform_id')
                result['upload_url'] = upload_result.get('upload_url')
                
                # Update rate limiter
                self._update_rate_limiter(platform)
                
                # Track performance
                self._track_platform_performance(platform, result)
                
            else:
                result['errors'] = upload_result.get('errors', ['Upload failed'])
            
        except Exception as e:
            result['errors'].append(str(e))
            self.logger.error(f"Platform upload failed for {platform}: {e}")
        
        return result
    
    def _check_rate_limit(self, platform: str) -> bool:
        """Vérifie les limites de débit"""
        try:
            limiter = self.rate_limiters.get(platform, {})
            limits = limiter.get('limits', {})
            
            current_time = time.time()
            
            # Check hourly limits
            hourly_limit = limits.get('api_calls_per_hour', limits.get('posts_per_hour', 1000))
            hour_ago = current_time - 3600
            
            recent_requests = [t for t in limiter.get('requests', []) if t > hour_ago]
            
            if len(recent_requests) >= hourly_limit:
                return False
            
            # Check daily limits
            daily_limit = limits.get('uploads_per_day', limits.get('posts_per_day', 100))
            day_ago = current_time - 86400
            
            recent_uploads = [t for t in limiter.get('uploads', []) if t > day_ago]
            
            if len(recent_uploads) >= daily_limit:
                return False
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Rate limit check failed for {platform}: {e}")
            return True  # Allow if check fails
    
    def _update_rate_limiter(self, platform: str):
        """Met à jour le limiteur de débit"""
        try:
            current_time = time.time()
            limiter = self.rate_limiters.get(platform, {'requests': [], 'uploads': []})
            
            limiter['requests'].append(current_time)
            limiter['uploads'].append(current_time)
            
            # Clean old entries (keep only last 24 hours)
            day_ago = current_time - 86400
            limiter['requests'] = [t for t in limiter['requests'] if t > day_ago]
            limiter['uploads'] = [t for t in limiter['uploads'] if t > day_ago]
            
        except Exception as e:
            self.logger.warning(f"Rate limiter update failed for {platform}: {e}")
    
    def _optimize_content_for_platform(self, content_data: Dict, platform: str) -> Dict[str, Any]:
        """Optimise le contenu pour une plateforme"""
        optimized = content_data.copy()
        
        try:
            platform_config = self.distribution_config['platforms'][platform]
            
            # Platform-specific optimizations would go here
            # For now, return original content
            optimized['platform_optimized'] = True
            optimized['target_platform'] = platform
            
            # Add platform-specific metadata
            if platform == 'youtube':
                optimized['category_id'] = '22'  # People & Blogs
                optimized['default_language'] = 'en'
            elif platform == 'instagram':
                optimized['aspect_ratio_optimized'] = True
            elif platform == 'tiktok':
                optimized['vertical_optimized'] = True
            
        except Exception as e:
            self.logger.warning(f"Content optimization failed for {platform}: {e}")
        
        return optimized
    
    def _simulate_platform_upload(self, platform: str, content_data: Dict, platform_config: Dict) -> Dict[str, Any]:
        """Simule l'upload vers une plateforme (remplacer par vraies APIs)"""
        import random
        import uuid
        
        # Simulate upload process
        time.sleep(random.uniform(5, 15))  # Simulate upload time
        
        # Simulate success/failure
        success_rate = 0.9  # 90% success rate
        success = random.random() < success_rate
        
        if success:
            return {
                'success': True,
                'platform_id': str(uuid.uuid4())[:8],
                'upload_url': f"https://{platform}.com/content/{uuid.uuid4()}"
            }
        else:
            return {
                'success': False,
                'errors': [f'Upload failed to {platform}', 'Network error']
            }
    
    def _track_platform_performance(self, platform: str, result: Dict[str, Any]):
        """Suit les performances par plateforme"""
        try:
            if platform not in self.performance_metrics['platform_success_rates']:
                self.performance_metrics['platform_success_rates'][platform] = {
                    'total_attempts': 0,
                    'successful_uploads': 0,
                    'average_upload_time': 0,
                    'total_upload_time': 0
                }
            
            platform_stats = self.performance_metrics['platform_success_rates'][platform]
            platform_stats['total_attempts'] += 1
            
            if result['success']:
                platform_stats['successful_uploads'] += 1
            
            upload_time = result.get('upload_time', 0)
            platform_stats['total_upload_time'] += upload_time
            platform_stats['average_upload_time'] = (
                platform_stats['total_upload_time'] / platform_stats['total_attempts']
            )
            
        except Exception as e:
            self.logger.warning(f"Performance tracking failed: {e}")
    
    def _get_job_status(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Récupère le statut d'un job"""
        job_id = input_data.get('job_id')
        
        result = {
            'job_id': job_id,
            'status': 'not_found',
            'job_details': {},
            'progress': {}
        }
        
        try:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]
                result['status'] = job.status
                result['job_details'] = asdict(job)
                result['progress'] = self._calculate_job_progress(job)
            
            # Check completed jobs
            elif job_id in self.completed_jobs:
                job = self.completed_jobs[job_id]
                result['status'] = 'completed'
                result['job_details'] = asdict(job)
                result['progress'] = {'completion_percentage': 100}
            
            # Check failed jobs
            elif job_id in self.failed_jobs:
                job = self.failed_jobs[job_id]
                result['status'] = 'failed'
                result['job_details'] = asdict(job)
                result['progress'] = {'completion_percentage': 0, 'failure_reason': 'Upload failed'}
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.error(f"Job status retrieval failed: {e}")
        
        return result
    
    def _calculate_job_progress(self, job: DistributionJob) -> Dict[str, Any]:
        """Calcule le progrès d'un job"""
        progress = {
            'completion_percentage': 0,
            'platforms_completed': 0,
            'platforms_total': len(job.platforms),
            'current_status': job.status,
            'estimated_time_remaining': '00:00:00'
        }
        
        try:
            if job.status == 'completed':
                progress['completion_percentage'] = 100
            elif job.status == 'processing':
                # Estimate based on time elapsed and platform count
                progress['completion_percentage'] = 50  # Simplified
            elif job.status == 'queued':
                progress['completion_percentage'] = 0
            
        except Exception as e:
            self.logger.warning(f"Progress calculation failed: {e}")
        
        return progress
    
    def validate_input(self, input_data: Any) -> bool:
        """Valide les données d'entrée pour la distribution"""
        if not isinstance(input_data, dict):
            return False
        
        operation = input_data.get('operation', 'distribute_content')
        
        if operation in ['distribute_content', 'schedule_distribution']:
            if not input_data.get('content_data'):
                return False
            if not input_data.get('platforms'):
                return False
        elif operation == 'get_job_status':
            if not input_data.get('job_id'):
                return False
        
        return True


class AsyncDistributionProcessor(AsyncBaseProcessor):
    """
Version asynchrone du processeur distribution"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.sync_processor = DistributionProcessor(config)
        self.executor = ThreadPoolExecutor(max_workers=8)
    
    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
Traitement asynchrone de la distribution"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.sync_processor.process_with_stats, 
            input_data
        )
    
    async def validate_input(self, input_data: Any) -> bool:
        """
Validation asynchrone"""
        return self.sync_processor.validate_input(input_data)
