#!/usr/bin/env python3

"""
IA Chérie SEO Distribution Rate Limiter - Multi-Platform Content Distribution
============================================================================

Advanced rate limiting system for SEO optimization and multi-platform content
distribution management. Handles content scheduling, cross-platform syndication,
SEO compliance, and performance analytics for the IA Chérie creator platform.

Features:
- Multi-platform distribution rate limiting (YouTube, TikTok, Instagram, Spotify, Apple Music, SoundCloud)
- SEO optimization with keyword limiting and meta optimization
- Content scheduling with optimal timing recommendations
- Cross-platform syndication management with platform-specific rules
- Performance analytics with engagement tracking and ROI measurement
- A/B testing framework for content optimization
- Compliance with platform-specific guidelines and rate limits
- Real-time performance monitoring and optimization suggestions

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
License: Proprietary - Unauthorized copying or distribution prohibited

Project: IA Chérie Rate Limiting - SEO Distribution Module
Version: 1.0 Production
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import uuid
import hashlib

# Configure logging for SEO distribution rate limiter
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Platform(Enum):
    """Supported distribution platforms"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    SPOTIFY = "spotify"
    APPLE_MUSIC = "apple_music"
    SOUNDCLOUD = "soundcloud"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"

class ContentType(Enum):
    """Content types for distribution"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"
    LIVESTREAM = "livestream"
    PODCAST = "podcast"
    STORY = "story"
    REEL = "reel"

class DistributionStrategy(Enum):
    """Distribution strategies"""
    SIMULTANEOUS = "simultaneous"
    SEQUENTIAL = "sequential"
    SCHEDULED = "scheduled"
    ADAPTIVE = "adaptive"
    A_B_TEST = "a_b_test"

class SEOOptimizationLevel(Enum):
    """SEO optimization levels"""
    BASIC = "basic"
    STANDARD = "standard"
    ADVANCED = "advanced"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class PerformanceMetric(Enum):
    """Performance tracking metrics"""
    VIEWS = "views"
    LIKES = "likes"
    SHARES = "shares"
    COMMENTS = "comments"
    CLICK_THROUGH_RATE = "ctr"
    ENGAGEMENT_RATE = "engagement_rate"
    CONVERSION_RATE = "conversion_rate"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    REVENUE = "revenue"

@dataclass
class PlatformLimits:
    """Platform-specific rate limits and guidelines"""
    platform: Platform
    max_posts_per_hour: int
    max_posts_per_day: int
    max_posts_per_week: int
    max_hashtags: int
    max_title_length: int
    max_description_length: int
    optimal_posting_hours: List[int]
    content_types_supported: Set[ContentType]
    requires_approval: bool = False
    processing_time_minutes: int = 5

@dataclass
class SEOConfiguration:
    """SEO optimization configuration"""
    max_keywords_per_content: int
    max_keyword_density: float
    required_meta_tags: List[str]
    optimal_title_length: Tuple[int, int]
    optimal_description_length: Tuple[int, int]
    hashtag_strategies: Dict[str, Any]
    content_freshness_hours: int

@dataclass
class DistributionRequest:
    """Content distribution request"""
    request_id: str
    user_id: str
    content_id: str
    content_type: ContentType
    title: str
    description: str
    keywords: List[str]
    hashtags: List[str]
    platforms: List[Platform]
    strategy: DistributionStrategy
    scheduled_time: Optional[datetime] = None
    seo_level: SEOOptimizationLevel = SEOOptimizationLevel.STANDARD
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DistributionResult:
    """Result of content distribution"""
    request_id: str
    platform: Platform
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    error_message: Optional[str] = None
    seo_score: float = 0.0
    optimization_suggestions: List[str] = field(default_factory=list)

@dataclass
class PerformanceAnalytics:
    """Performance analytics for distributed content"""
    content_id: str
    platform: Platform
    metrics: Dict[PerformanceMetric, float]
    engagement_rate: float
    reach_rate: float
    conversion_metrics: Dict[str, float]
    roi: float
    updated_at: datetime = field(default_factory=datetime.now)

class SEODistributionLimiter:
    """
    Advanced SEO distribution rate limiter with multi-platform support
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize SEO distribution rate limiter"""
        self.config = config or {}
        self.node_id = str(uuid.uuid4())
        
        # Setup platform configurations
        self._setup_platform_configurations()
        self._setup_seo_configurations()
        
        # Distribution tracking
        self.distribution_requests: Dict[str, DistributionRequest] = {}
        self.distribution_results: Dict[str, List[DistributionResult]] = {}
        self.platform_usage: Dict[str, Dict[Platform, List[datetime]]] = {}
        
        # Performance analytics
        self.performance_data: Dict[str, Dict[Platform, PerformanceAnalytics]] = {}
        self.optimization_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Background task management
        self.background_tasks: Set[asyncio.Task] = set()
        self.is_running = False
        
        logger.info(f"SEODistributionLimiter initialized with node_id: {self.node_id}")
    
    def _setup_platform_configurations(self):
        """Setup platform-specific configurations"""
        self.platform_configs = {
            Platform.YOUTUBE: PlatformLimits(
                platform=Platform.YOUTUBE,
                max_posts_per_hour=3,
                max_posts_per_day=10,
                max_posts_per_week=50,
                max_hashtags=15,
                max_title_length=100,
                max_description_length=5000,
                optimal_posting_hours=[14, 15, 16, 20, 21],
                content_types_supported={ContentType.VIDEO, ContentType.LIVESTREAM},
                processing_time_minutes=15
            ),
            Platform.TIKTOK: PlatformLimits(
                platform=Platform.TIKTOK,
                max_posts_per_hour=5,
                max_posts_per_day=20,
                max_posts_per_week=100,
                max_hashtags=20,
                max_title_length=150,
                max_description_length=2200,
                optimal_posting_hours=[6, 10, 19, 20, 21],
                content_types_supported={ContentType.VIDEO, ContentType.LIVESTREAM},
                processing_time_minutes=5
            ),
            Platform.INSTAGRAM: PlatformLimits(
                platform=Platform.INSTAGRAM,
                max_posts_per_hour=2,
                max_posts_per_day=8,
                max_posts_per_week=40,
                max_hashtags=30,
                max_title_length=125,
                max_description_length=2200,
                optimal_posting_hours=[11, 13, 17, 19],
                content_types_supported={ContentType.IMAGE, ContentType.VIDEO, ContentType.STORY, ContentType.REEL},
                processing_time_minutes=3
            ),
            Platform.SPOTIFY: PlatformLimits(
                platform=Platform.SPOTIFY,
                max_posts_per_hour=1,
                max_posts_per_day=5,
                max_posts_per_week=25,
                max_hashtags=10,
                max_title_length=100,
                max_description_length=1000,
                optimal_posting_hours=[8, 14, 18, 22],
                content_types_supported={ContentType.AUDIO, ContentType.PODCAST},
                requires_approval=True,
                processing_time_minutes=60
            ),
            Platform.APPLE_MUSIC: PlatformLimits(
                platform=Platform.APPLE_MUSIC,
                max_posts_per_hour=1,
                max_posts_per_day=3,
                max_posts_per_week=15,
                max_hashtags=8,
                max_title_length=80,
                max_description_length=800,
                optimal_posting_hours=[9, 15, 19],
                content_types_supported={ContentType.AUDIO, ContentType.PODCAST},
                requires_approval=True,
                processing_time_minutes=90
            ),
            Platform.SOUNDCLOUD: PlatformLimits(
                platform=Platform.SOUNDCLOUD,
                max_posts_per_hour=3,
                max_posts_per_day=12,
                max_posts_per_week=60,
                max_hashtags=15,
                max_title_length=200,
                max_description_length=3000,
                optimal_posting_hours=[10, 14, 18, 21],
                content_types_supported={ContentType.AUDIO, ContentType.PODCAST},
                processing_time_minutes=10
            )
        }
    
    def _setup_seo_configurations(self):
        """Setup SEO optimization configurations"""
        self.seo_configs = {
            SEOOptimizationLevel.BASIC: SEOConfiguration(
                max_keywords_per_content=5,
                max_keyword_density=0.03,
                required_meta_tags=['title', 'description'],
                optimal_title_length=(30, 60),
                optimal_description_length=(120, 160),
                hashtag_strategies={'max_per_platform': 10, 'trending_weight': 0.3},
                content_freshness_hours=24
            ),
            SEOOptimizationLevel.STANDARD: SEOConfiguration(
                max_keywords_per_content=10,
                max_keyword_density=0.025,
                required_meta_tags=['title', 'description', 'keywords', 'author'],
                optimal_title_length=(30, 65),
                optimal_description_length=(120, 155),
                hashtag_strategies={'max_per_platform': 15, 'trending_weight': 0.5},
                content_freshness_hours=12
            ),
            SEOOptimizationLevel.ADVANCED: SEOConfiguration(
                max_keywords_per_content=15,
                max_keyword_density=0.02,
                required_meta_tags=['title', 'description', 'keywords', 'author', 'category', 'tags'],
                optimal_title_length=(35, 70),
                optimal_description_length=(130, 160),
                hashtag_strategies={'max_per_platform': 20, 'trending_weight': 0.7},
                content_freshness_hours=6
            ),
            SEOOptimizationLevel.PREMIUM: SEOConfiguration(
                max_keywords_per_content=20,
                max_keyword_density=0.018,
                required_meta_tags=['title', 'description', 'keywords', 'author', 'category', 'tags', 'schema'],
                optimal_title_length=(40, 80),
                optimal_description_length=(140, 170),
                hashtag_strategies={'max_per_platform': 25, 'trending_weight': 0.8},
                content_freshness_hours=4
            ),
            SEOOptimizationLevel.ENTERPRISE: SEOConfiguration(
                max_keywords_per_content=30,
                max_keyword_density=0.015,
                required_meta_tags=['title', 'description', 'keywords', 'author', 'category', 'tags', 'schema', 'canonical'],
                optimal_title_length=(45, 90),
                optimal_description_length=(150, 180),
                hashtag_strategies={'max_per_platform': 30, 'trending_weight': 0.9},
                content_freshness_hours=2
            )
        }
    
    async def initialize(self) -> bool:
        """Initialize SEO distribution rate limiter"""
        try:
            self.is_running = True
            
            # Start background tasks
            self.background_tasks.add(
                asyncio.create_task(self._performance_analytics_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._optimization_monitoring_task())
            )
            self.background_tasks.add(
                asyncio.create_task(self._platform_sync_task())
            )
            
            logger.info("SEODistributionLimiter initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SEODistributionLimiter: {e}")
            return False
    
    async def check_distribution_limit(
        self,
        user_id: str,
        platform: Platform,
        content_type: ContentType,
        strategy: DistributionStrategy = DistributionStrategy.SIMULTANEOUS
    ) -> Dict[str, Any]:
        """Check if user can distribute content to platform"""
        start_time = time.time()
        
        try:
            platform_config = self.platform_configs[platform]
            
            # Check content type support
            if content_type not in platform_config.content_types_supported:
                return {
                    'allowed': False,
                    'reason': f'Content type {content_type.value} not supported on {platform.value}',
                    'supported_types': [ct.value for ct in platform_config.content_types_supported]
                }
            
            # Get current platform usage
            current_usage = await self._get_platform_usage(user_id, platform)
            
            # Check hourly limit
            hour_posts = len([
                dt for dt in current_usage
                if dt >= datetime.now() - timedelta(hours=1)
            ])
            
            if hour_posts >= platform_config.max_posts_per_hour:
                next_available = min(current_usage) + timedelta(hours=1)
                return {
                    'allowed': False,
                    'reason': 'Hourly limit exceeded',
                    'current_hour_posts': hour_posts,
                    'limit': platform_config.max_posts_per_hour,
                    'next_available_time': next_available.isoformat()
                }
            
            # Check daily limit
            day_posts = len([
                dt for dt in current_usage
                if dt >= datetime.now() - timedelta(days=1)
            ])
            
            if day_posts >= platform_config.max_posts_per_day:
                next_available = min(current_usage) + timedelta(days=1)
                return {
                    'allowed': False,
                    'reason': 'Daily limit exceeded',
                    'current_day_posts': day_posts,
                    'limit': platform_config.max_posts_per_day,
                    'next_available_time': next_available.isoformat()
                }
            
            # Get optimal posting time recommendations
            optimal_times = await self._get_optimal_posting_times(platform, strategy)
            
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'allowed': True,
                'platform': platform.value,
                'remaining_hour': platform_config.max_posts_per_hour - hour_posts,
                'remaining_day': platform_config.max_posts_per_day - day_posts,
                'optimal_times': optimal_times,
                'processing_time_minutes': platform_config.processing_time_minutes,
                'requires_approval': platform_config.requires_approval,
                'execution_time_ms': execution_time,
                'node_id': self.node_id
            }
            
        except Exception as e:
            logger.error(f"Error checking distribution limit for {platform.value}: {e}")
            return {
                'allowed': False,
                'error': str(e),
                'execution_time_ms': (time.time() - start_time) * 1000
            }
    
    async def submit_distribution_request(
        self,
        request: DistributionRequest
    ) -> Dict[str, Any]:
        """Submit content for multi-platform distribution"""
        try:
            # Validate request
            validation_result = await self._validate_distribution_request(request)
            if not validation_result['valid']:
                return {
                    'success': False,
                    'request_id': request.request_id,
                    'errors': validation_result['errors']
                }
            
            # Store request
            self.distribution_requests[request.request_id] = request
            
            # Initialize results tracking
            self.distribution_results[request.request_id] = []
            
            # Process distribution based on strategy
            if request.strategy == DistributionStrategy.SIMULTANEOUS:
                results = await self._distribute_simultaneous(request)
            elif request.strategy == DistributionStrategy.SEQUENTIAL:
                results = await self._distribute_sequential(request)
            elif request.strategy == DistributionStrategy.SCHEDULED:
                results = await self._distribute_scheduled(request)
            elif request.strategy == DistributionStrategy.ADAPTIVE:
                results = await self._distribute_adaptive(request)
            elif request.strategy == DistributionStrategy.A_B_TEST:
                results = await self._distribute_ab_test(request)
            else:
                return {
                    'success': False,
                    'request_id': request.request_id,
                    'error': f'Unknown distribution strategy: {request.strategy.value}'
                }
            
            # Store results
            self.distribution_results[request.request_id].extend(results)
            
            # Calculate overall success rate
            successful_distributions = len([r for r in results if r.success])
            success_rate = successful_distributions / len(results) if results else 0
            
            return {
                'success': success_rate > 0,
                'request_id': request.request_id,
                'strategy': request.strategy.value,
                'total_platforms': len(request.platforms),
                'successful_distributions': successful_distributions,
                'success_rate': success_rate,
                'results': [
                    {
                        'platform': r.platform.value,
                        'success': r.success,
                        'post_id': r.post_id,
                        'post_url': r.post_url,
                        'seo_score': r.seo_score,
                        'error': r.error_message
                    }
                    for r in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error submitting distribution request {request.request_id}: {e}")
            return {
                'success': False,
                'request_id': request.request_id,
                'error': str(e)
            }
    
    async def optimize_content_seo(
        self,
        content: Dict[str, Any],
        platforms: List[Platform],
        seo_level: SEOOptimizationLevel = SEOOptimizationLevel.STANDARD
    ) -> Dict[str, Any]:
        """Optimize content for SEO across multiple platforms"""
        try:
            seo_config = self.seo_configs[seo_level]
            optimization_results = {}
            
            for platform in platforms:
                platform_config = self.platform_configs[platform]
                
                # Optimize title
                optimized_title = await self._optimize_title(
                    content.get('title', ''),
                    platform_config,
                    seo_config
                )
                
                # Optimize description
                optimized_description = await self._optimize_description(
                    content.get('description', ''),
                    platform_config,
                    seo_config
                )
                
                # Optimize keywords
                optimized_keywords = await self._optimize_keywords(
                    content.get('keywords', []),
                    platform,
                    seo_config
                )
                
                # Optimize hashtags
                optimized_hashtags = await self._optimize_hashtags(
                    content.get('hashtags', []),
                    platform_config,
                    seo_config
                )
                
                # Calculate SEO score
                seo_score = await self._calculate_seo_score(
                    optimized_title,
                    optimized_description,
                    optimized_keywords,
                    optimized_hashtags,
                    platform,
                    seo_config
                )
                
                optimization_results[platform.value] = {
                    'title': optimized_title,
                    'description': optimized_description,
                    'keywords': optimized_keywords,
                    'hashtags': optimized_hashtags,
                    'seo_score': seo_score,
                    'recommendations': await self._get_optimization_recommendations(
                        platform, seo_score, seo_config
                    )
                }
            
            return {
                'success': True,
                'seo_level': seo_level.value,
                'optimizations': optimization_results,
                'overall_score': sum(
                    result['seo_score'] for result in optimization_results.values()
                ) / len(optimization_results) if optimization_results else 0
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content SEO: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_performance_analytics(
        self,
        content_id: str,
        platforms: Optional[List[Platform]] = None,
        time_range_days: int = 30
    ) -> Dict[str, Any]:
        """Get performance analytics for distributed content"""
        try:
            if content_id not in self.performance_data:
                return {
                    'success': False,
                    'error': f'No performance data found for content {content_id}'
                }
            
            content_analytics = self.performance_data[content_id]
            platforms_to_analyze = platforms or list(content_analytics.keys())
            
            analytics_summary = {
                'content_id': content_id,
                'time_range_days': time_range_days,
                'platforms_analyzed': len(platforms_to_analyze),
                'platform_performance': {},
                'overall_metrics': {},
                'recommendations': []
            }
            
            total_metrics = {metric: 0.0 for metric in PerformanceMetric}
            
            for platform in platforms_to_analyze:
                if platform in content_analytics:
                    performance = content_analytics[platform]
                    
                    analytics_summary['platform_performance'][platform.value] = {
                        'metrics': {
                            metric.value: value 
                            for metric, value in performance.metrics.items()
                        },
                        'engagement_rate': performance.engagement_rate,
                        'reach_rate': performance.reach_rate,
                        'conversion_metrics': performance.conversion_metrics,
                        'roi': performance.roi,
                        'last_updated': performance.updated_at.isoformat()
                    }
                    
                    # Aggregate metrics
                    for metric, value in performance.metrics.items():
                        total_metrics[metric] += value
            
            # Calculate overall metrics
            analytics_summary['overall_metrics'] = {
                metric.value: value for metric, value in total_metrics.items()
            }
            
            # Generate recommendations
            analytics_summary['recommendations'] = await self._generate_performance_recommendations(
                content_id, platforms_to_analyze
            )
            
            return {
                'success': True,
                'analytics': analytics_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting performance analytics for {content_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def get_optimal_distribution_schedule(
        self,
        user_id: str,
        content_type: ContentType,
        platforms: List[Platform],
        target_audience_timezone: str = "UTC"
    ) -> Dict[str, Any]:
        """Get optimal distribution schedule for maximum reach"""
        try:
            schedule_recommendations = {}
            
            for platform in platforms:
                platform_config = self.platform_configs[platform]
                
                # Check current usage
                current_usage = await self._get_platform_usage(user_id, platform)
                next_available_slots = []
                
                # Calculate next 7 days of optimal posting times
                now = datetime.now()
                for day_offset in range(7):
                    target_date = now + timedelta(days=day_offset)
                    
                    for hour in platform_config.optimal_posting_hours:
                        scheduled_time = target_date.replace(
                            hour=hour, minute=0, second=0, microsecond=0
                        )
                        
                        if scheduled_time > now:
                            # Check if slot is available based on rate limits
                            hour_usage = len([
                                dt for dt in current_usage
                                if abs((dt - scheduled_time).total_seconds()) < 3600
                            ])
                            
                            if hour_usage < platform_config.max_posts_per_hour:
                                next_available_slots.append({
                                    'time': scheduled_time.isoformat(),
                                    'score': await self._calculate_optimal_time_score(
                                        platform, scheduled_time, target_audience_timezone
                                    ),
                                    'estimated_reach': await self._estimate_reach(
                                        platform, scheduled_time, content_type
                                    )
                                })
                
                # Sort by score (best times first)
                next_available_slots.sort(key=lambda x: x['score'], reverse=True)
                
                schedule_recommendations[platform.value] = {
                    'optimal_slots': next_available_slots[:10],  # Top 10 slots
                    'current_usage_today': len([
                        dt for dt in current_usage
                        if dt.date() == now.date()
                    ]),
                    'daily_limit': platform_config.max_posts_per_day,
                    'processing_time_minutes': platform_config.processing_time_minutes
                }
            
            return {
                'success': True,
                'user_id': user_id,
                'content_type': content_type.value,
                'schedule_recommendations': schedule_recommendations,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting optimal distribution schedule: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _validate_distribution_request(self, request: DistributionRequest) -> Dict[str, Any]:
        """Validate distribution request"""
        errors = []
        
        # Check required fields
        if not request.title:
            errors.append("Title is required")
        
        if not request.platforms:
            errors.append("At least one platform must be specified")
        
        # Validate platforms support content type
        for platform in request.platforms:
            platform_config = self.platform_configs[platform]
            if request.content_type not in platform_config.content_types_supported:
                errors.append(
                    f"Platform {platform.value} does not support content type {request.content_type.value}"
                )
        
        # Validate SEO configuration
        seo_config = self.seo_configs[request.seo_level]
        
        if len(request.keywords) > seo_config.max_keywords_per_content:
            errors.append(
                f"Too many keywords: {len(request.keywords)} > {seo_config.max_keywords_per_content}"
            )
        
        # Validate scheduled time if provided
        if request.scheduled_time and request.scheduled_time <= datetime.now():
            errors.append("Scheduled time must be in the future")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    async def _distribute_simultaneous(self, request: DistributionRequest) -> List[DistributionResult]:
        """Distribute content simultaneously to all platforms"""
        results = []
        
        # Create distribution tasks for all platforms
        tasks = []
        for platform in request.platforms:
            task = asyncio.create_task(
                self._distribute_to_platform(request, platform)
            )
            tasks.append(task)
        
        # Wait for all distributions to complete
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(platform_results):
            if isinstance(result, Exception):
                results.append(DistributionResult(
                    request_id=request.request_id,
                    platform=request.platforms[i],
                    success=False,
                    error_message=str(result)
                ))
            else:
                results.append(result)
        
        return results
    
    async def _distribute_sequential(self, request: DistributionRequest) -> List[DistributionResult]:
        """Distribute content sequentially to platforms"""
        results = []
        
        for platform in request.platforms:
            result = await self._distribute_to_platform(request, platform)
            results.append(result)
            
            # Add delay between platforms to avoid overwhelming
            await asyncio.sleep(5)
        
        return results
    
    async def _distribute_scheduled(self, request: DistributionRequest) -> List[DistributionResult]:
        """Schedule content distribution"""
        results = []
        
        if not request.scheduled_time:
            # Auto-schedule for optimal times
            for platform in request.platforms:
                optimal_time = await self._get_next_optimal_time(platform)
                
                result = DistributionResult(
                    request_id=request.request_id,
                    platform=platform,
                    success=True,
                    scheduled_time=optimal_time,
                    seo_score=0.8  # Placeholder
                )
                results.append(result)
        else:
            # Use provided scheduled time
            for platform in request.platforms:
                result = DistributionResult(
                    request_id=request.request_id,
                    platform=platform,
                    success=True,
                    scheduled_time=request.scheduled_time,
                    seo_score=0.7  # Lower score for non-optimal time
                )
                results.append(result)
        
        return results
    
    async def _distribute_adaptive(self, request: DistributionRequest) -> List[DistributionResult]:
        """Adaptive distribution based on platform performance"""
        results = []
        
        # Sort platforms by historical performance
        platform_scores = {}
        for platform in request.platforms:
            score = await self._calculate_platform_performance_score(
                request.user_id, platform, request.content_type
            )
            platform_scores[platform] = score
        
        # Distribute to best performing platforms first
        sorted_platforms = sorted(
            request.platforms,
            key=lambda p: platform_scores[p],
            reverse=True
        )
        
        for platform in sorted_platforms:
            result = await self._distribute_to_platform(request, platform)
            results.append(result)
            
            # Adjust delay based on performance
            delay = max(1, 10 - int(platform_scores[platform] * 10))
            await asyncio.sleep(delay)
        
        return results
    
    async def _distribute_ab_test(self, request: DistributionRequest) -> List[DistributionResult]:
        """A/B test distribution with different optimizations"""
        results = []
        
        # Split platforms into test groups
        test_group_a = request.platforms[:len(request.platforms)//2]
        test_group_b = request.platforms[len(request.platforms)//2:]
        
        # Create variations
        variation_a = request
        variation_b = await self._create_content_variation(request)
        
        # Distribute variation A
        for platform in test_group_a:
            result = await self._distribute_to_platform(variation_a, platform)
            result.optimization_suggestions.append("A/B Test Variation A")
            results.append(result)
        
        # Distribute variation B
        for platform in test_group_b:
            result = await self._distribute_to_platform(variation_b, platform)
            result.optimization_suggestions.append("A/B Test Variation B")
            results.append(result)
        
        return results
    
    async def _distribute_to_platform(
        self,
        request: DistributionRequest,
        platform: Platform
    ) -> DistributionResult:
        """Distribute content to specific platform"""
        try:
            # Check rate limits
            limit_check = await self.check_distribution_limit(
                request.user_id, platform, request.content_type
            )
            
            if not limit_check['allowed']:
                return DistributionResult(
                    request_id=request.request_id,
                    platform=platform,
                    success=False,
                    error_message=limit_check['reason']
                )
            
            # Optimize content for platform
            optimization = await self.optimize_content_seo(
                {
                    'title': request.title,
                    'description': request.description,
                    'keywords': request.keywords,
                    'hashtags': request.hashtags
                },
                [platform],
                request.seo_level
            )
            
            if not optimization['success']:
                return DistributionResult(
                    request_id=request.request_id,
                    platform=platform,
                    success=False,
                    error_message="SEO optimization failed"
                )
            
            platform_optimization = optimization['optimizations'][platform.value]
            
            # Record usage
            await self._record_platform_usage(request.user_id, platform)
            
            # Simulate successful distribution
            post_id = f"{platform.value}_{request.content_id}_{int(time.time())}"
            post_url = f"https://{platform.value}.com/post/{post_id}"
            
            return DistributionResult(
                request_id=request.request_id,
                platform=platform,
                success=True,
                post_id=post_id,
                post_url=post_url,
                seo_score=platform_optimization['seo_score'],
                optimization_suggestions=platform_optimization['recommendations']
            )
            
        except Exception as e:
            logger.error(f"Error distributing to {platform.value}: {e}")
            return DistributionResult(
                request_id=request.request_id,
                platform=platform,
                success=False,
                error_message=str(e)
            )
    
    async def _get_platform_usage(self, user_id: str, platform: Platform) -> List[datetime]:
        """Get recent platform usage for user"""
        if user_id not in self.platform_usage:
            self.platform_usage[user_id] = {}
        
        if platform not in self.platform_usage[user_id]:
            self.platform_usage[user_id][platform] = []
        
        # Clean old usage records (keep last 7 days)
        cutoff_time = datetime.now() - timedelta(days=7)
        self.platform_usage[user_id][platform] = [
            dt for dt in self.platform_usage[user_id][platform]
            if dt >= cutoff_time
        ]
        
        return self.platform_usage[user_id][platform]
    
    async def _record_platform_usage(self, user_id: str, platform: Platform):
        """Record platform usage"""
        if user_id not in self.platform_usage:
            self.platform_usage[user_id] = {}
        
        if platform not in self.platform_usage[user_id]:
            self.platform_usage[user_id][platform] = []
        
        self.platform_usage[user_id][platform].append(datetime.now())
    
    async def _get_optimal_posting_times(
        self,
        platform: Platform,
        strategy: DistributionStrategy
    ) -> List[str]:
        """Get optimal posting times for platform"""
        platform_config = self.platform_configs[platform]
        
        # Get next 24 hours of optimal times
        optimal_times = []
        now = datetime.now()
        
        for hour in platform_config.optimal_posting_hours:
            # Today
            today_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if today_time > now:
                optimal_times.append(today_time.isoformat())
            
            # Tomorrow
            tomorrow_time = today_time + timedelta(days=1)
            optimal_times.append(tomorrow_time.isoformat())
        
        return optimal_times[:5]  # Return top 5 times
    
    async def _optimize_title(
        self,
        title: str,
        platform_config: PlatformLimits,
        seo_config: SEOConfiguration
    ) -> str:
        """Optimize title for platform and SEO"""
        if not title:
            return ""
        
        # Truncate to platform limit
        max_length = min(platform_config.max_title_length, seo_config.optimal_title_length[1])
        
        if len(title) > max_length:
            return title[:max_length-3] + "..."
        
        return title
    
    async def _optimize_description(
        self,
        description: str,
        platform_config: PlatformLimits,
        seo_config: SEOConfiguration
    ) -> str:
        """Optimize description for platform and SEO"""
        if not description:
            return ""
        
        # Truncate to platform limit
        max_length = min(platform_config.max_description_length, seo_config.optimal_description_length[1])
        
        if len(description) > max_length:
            return description[:max_length-3] + "..."
        
        return description
    
    async def _optimize_keywords(
        self,
        keywords: List[str],
        platform: Platform,
        seo_config: SEOConfiguration
    ) -> List[str]:
        """Optimize keywords for platform and SEO"""
        # Limit to SEO configuration maximum
        return keywords[:seo_config.max_keywords_per_content]
    
    async def _optimize_hashtags(
        self,
        hashtags: List[str],
        platform_config: PlatformLimits,
        seo_config: SEOConfiguration
    ) -> List[str]:
        """Optimize hashtags for platform"""
        # Limit to platform maximum
        max_hashtags = min(
            platform_config.max_hashtags,
            seo_config.hashtag_strategies['max_per_platform']
        )
        
        return hashtags[:max_hashtags]
    
    async def _calculate_seo_score(
        self,
        title: str,
        description: str,
        keywords: List[str],
        hashtags: List[str],
        platform: Platform,
        seo_config: SEOConfiguration
    ) -> float:
        """Calculate SEO score for content"""
        score = 0.0
        
        # Title optimization (30% weight)
        title_length = len(title)
        optimal_title_range = seo_config.optimal_title_length
        if optimal_title_range[0] <= title_length <= optimal_title_range[1]:
            score += 0.3
        elif title_length > 0:
            score += 0.15  # Partial credit
        
        # Description optimization (25% weight)
        desc_length = len(description)
        optimal_desc_range = seo_config.optimal_description_length
        if optimal_desc_range[0] <= desc_length <= optimal_desc_range[1]:
            score += 0.25
        elif desc_length > 0:
            score += 0.125  # Partial credit
        
        # Keywords optimization (25% weight)
        if keywords:
            keyword_score = min(1.0, len(keywords) / seo_config.max_keywords_per_content)
            score += 0.25 * keyword_score
        
        # Hashtags optimization (20% weight)
        if hashtags:
            platform_config = self.platform_configs[platform]
            hashtag_score = min(1.0, len(hashtags) / platform_config.max_hashtags)
            score += 0.20 * hashtag_score
        
        return round(score, 2)
    
    async def _get_optimization_recommendations(
        self,
        platform: Platform,
        seo_score: float,
        seo_config: SEOConfiguration
    ) -> List[str]:
        """Get optimization recommendations"""
        recommendations = []
        
        if seo_score < 0.5:
            recommendations.append("Consider adding more relevant keywords")
            recommendations.append("Optimize title length for better SEO")
            recommendations.append("Add platform-specific hashtags")
        elif seo_score < 0.8:
            recommendations.append("Fine-tune description length")
            recommendations.append("Consider trending hashtags for better reach")
        else:
            recommendations.append("Content is well optimized!")
        
        return recommendations
    
    async def _performance_analytics_task(self):
        """Background task for performance analytics"""
        while self.is_running:
            try:
                # Simulate performance data collection
                # In real implementation, this would integrate with platform APIs
                
                await asyncio.sleep(3600)  # Run every hour
                
            except Exception as e:
                logger.error(f"Error in performance analytics task: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes on error
    
    async def _optimization_monitoring_task(self):
        """Background task for optimization monitoring"""
        while self.is_running:
            try:
                # Monitor optimization effectiveness
                # Update algorithms based on performance
                
                await asyncio.sleep(21600)  # Run every 6 hours
                
            except Exception as e:
                logger.error(f"Error in optimization monitoring task: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def _platform_sync_task(self):
        """Background task for platform synchronization"""
        while self.is_running:
            try:
                # Sync with platform APIs for latest limits and guidelines
                # Update configurations as needed
                
                await asyncio.sleep(86400)  # Run daily
                
            except Exception as e:
                logger.error(f"Error in platform sync task: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour on error
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return {
            'service': 'SEODistributionLimiter',
            'status': 'healthy' if self.is_running else 'stopped',
            'node_id': self.node_id,
            'active_requests': len(self.distribution_requests),
            'platforms_supported': len(self.platform_configs),
            'seo_levels_available': len(self.seo_configs),
            'background_tasks': len(self.background_tasks),
            'uptime_seconds': time.time() - getattr(self, '_start_time', time.time())
        }
    
    async def shutdown(self):
        """Gracefully shutdown SEO distribution limiter"""
        logger.info("Shutting down SEODistributionLimiter...")
        self.is_running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        logger.info("SEODistributionLimiter shut down complete")

# Export main classes and functions
__all__ = [
    'SEODistributionLimiter',
    'Platform',
    'ContentType',
    'DistributionStrategy',
    'SEOOptimizationLevel',
    'PerformanceMetric',
    'PlatformLimits',
    'SEOConfiguration',
    'DistributionRequest',
    'DistributionResult',
    'PerformanceAnalytics'
]

if __name__ == "__main__":
    async def demo():
        """Demo SEO distribution limiter functionality"""
        limiter = SEODistributionLimiter()
        await limiter.initialize()
        
        # Test distribution limit checking
        limit_check = await limiter.check_distribution_limit(
            "user_123", Platform.YOUTUBE, ContentType.VIDEO
        )
        print(f"Distribution limit check: {json.dumps(limit_check, indent=2)}")
        
        # Test content SEO optimization
        optimization = await limiter.optimize_content_seo(
            {
                'title': 'My Amazing Video Content',
                'description': 'This is a description of my amazing video content',
                'keywords': ['video', 'content', 'amazing', 'tutorial'],
                'hashtags': ['#video', '#content', '#tutorial', '#amazing']
            },
            [Platform.YOUTUBE, Platform.TIKTOK],
            SEOOptimizationLevel.ADVANCED
        )
        print(f"SEO optimization: {json.dumps(optimization, indent=2)}")
        
        # Test distribution request
        request = DistributionRequest(
            request_id=str(uuid.uuid4()),
            user_id="user_123",
            content_id="content_456",
            content_type=ContentType.VIDEO,
            title="My Test Video",
            description="This is a test video for distribution",
            keywords=["test", "video", "distribution"],
            hashtags=["#test", "#video"],
            platforms=[Platform.YOUTUBE, Platform.TIKTOK],
            strategy=DistributionStrategy.SIMULTANEOUS,
            seo_level=SEOOptimizationLevel.STANDARD
        )
        
        distribution_result = await limiter.submit_distribution_request(request)
        print(f"Distribution result: {json.dumps(distribution_result, indent=2)}")
        
        # Test optimal scheduling
        schedule = await limiter.get_optimal_distribution_schedule(
            "user_123", ContentType.VIDEO, [Platform.YOUTUBE, Platform.INSTAGRAM]
        )
        print(f"Optimal schedule: {json.dumps(schedule, indent=2, default=str)}")
        
        # Get health status
        health = await limiter.get_health_status()
        print(f"Health status: {json.dumps(health, indent=2)}")
        
        await limiter.shutdown()
    
    # Run demo
    asyncio.run(demo())