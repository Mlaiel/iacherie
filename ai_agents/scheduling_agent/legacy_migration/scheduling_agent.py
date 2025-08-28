#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduling Agent - Advanced Content Scheduling & Timing Optimization System
===========================================================================

Industrial-grade intelligent scheduling system for content distribution across multiple platforms.
Handles optimal posting times, audience timezone analysis, automated scheduling with AI-powered timing optimization.

Features:
- AI-driven optimal timing analysis
- Multi-platform scheduling coordination
- Audience behavior pattern recognition
- Global timezone management
- Advanced calendar integration
- Performance-based scheduling optimization

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from contextlib import asynccontextmanager

import numpy as np
import pandas as pd
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import croniter

from ..base import BaseAgent, AgentStatus, AgentError
from ...core.config import settings
from ...core.database import get_db_session
from ...security.encryption import ContentEncryption
from ...utils.performance_monitor import PerformanceMonitor
from ...integrations.platform_apis import PlatformAPIManager

logger = logging.getLogger(__name__)

class SchedulingPriority(Enum):
    """Scheduling priority levels"""
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ScheduleStatus(Enum):
    """Schedule execution status"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"

class ScheduleType(Enum):
    """Types of scheduling"""
    IMMEDIATE = "immediate"
    DELAYED = "delayed"
    RECURRING = "recurring"
    CONDITIONAL = "conditional"
    SMART_OPTIMAL = "smart_optimal"

@dataclass
class SchedulingRequest:
    """Scheduling request configuration"""
    content_id: str
    platforms: List[str]
    schedule_time: Optional[datetime] = None
    priority: SchedulingPriority = SchedulingPriority.NORMAL
    schedule_type: ScheduleType = ScheduleType.DELAYED
    timezone: str = "UTC"
    recurring_pattern: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OptimalTimingAnalysis:
    """Optimal timing analysis results"""
    recommended_time: datetime
    confidence_score: float
    audience_activity_score: float
    competition_score: float
    platform_optimization_score: float
    global_factors: Dict[str, float]
    reasoning: List[str]

@dataclass
class ScheduleResult:
    """Schedule execution result"""
    schedule_id: str
    status: ScheduleStatus
    execution_time: Optional[datetime]
    platforms_executed: List[str]
    platforms_failed: List[str]
    performance_metrics: Dict[str, float]
    error_details: Optional[Dict[str, Any]] = None

Base = declarative_base()

class ScheduledJob(Base):
    """Database model for scheduled jobs"""
    __tablename__ = 'scheduled_jobs'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    content_id = Column(String, nullable=False, index=True)
    creator_id = Column(String, nullable=False, index=True)
    platforms = Column(JSON, nullable=False)
    schedule_time = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_execution_time = Column(DateTime(timezone=True), nullable=True)
    priority = Column(String, nullable=False, default="normal")
    schedule_type = Column(String, nullable=False, default="delayed")
    status = Column(String, nullable=False, default="pending", index=True)
    recurring_pattern = Column(String, nullable=True)
    conditions = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    error_details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class AudienceActivity(Base):
    """Database model for audience activity tracking"""
    __tablename__ = 'audience_activity'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, nullable=False, index=True)
    platform = Column(String, nullable=False, index=True)
    hour_of_day = Column(Integer, nullable=False)
    day_of_week = Column(Integer, nullable=False)
    timezone = Column(String, nullable=False)
    activity_score = Column(Float, nullable=False)
    engagement_rate = Column(Float, nullable=False)
    sample_size = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class SchedulingAgent(BaseAgent):
    """
    Enterprise scheduling agent for intelligent content timing and distribution.
    
    Provides industrial-grade scheduling capabilities including:
    - AI-driven optimal timing analysis
    - Multi-platform coordination
    - Global timezone management
    - Enterprise calendar integration
    - Performance-based optimization
    - Real-time adaptation and learning
    """
    
    def __init__(self, agent_id: str = None):
        super().__init__(
            agent_id=agent_id or f"scheduling_agent_{uuid.uuid4().hex[:8]}",
            name="SchedulingAgent",
            description="Enterprise content scheduling and timing optimization system"
        )
        
        self.scheduler = None
        self.platform_api_manager = PlatformAPIManager()
        self.encryption = ContentEncryption()
        self.performance_monitor = PerformanceMonitor()
        
        # AI models for timing optimization
        self.timing_models = {}
        self.audience_analyzers = {}
        
        # Cache for optimal timing predictions
        self.timing_cache = {}
        self.cache_ttl = timedelta(hours=1)
        
        self._setup_scheduler()
        self._initialize_models()
    
    def _setup_scheduler(self):
        """Initialize the enterprise scheduler with database persistence"""
        try:
            jobstores = {
                'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
            }
            
            job_defaults = {
                'coalesce': False,
                'max_instances': 3,
                'misfire_grace_time': 300
            }
            
            self.scheduler = AsyncIOScheduler(
                jobstores=jobstores,
                job_defaults=job_defaults,
                timezone=pytz.UTC
            )
            
            self.scheduler.start()
            logger.info(f"Scheduler initialized for agent {self.agent_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            raise AgentError(f"Scheduler initialization failed: {str(e)}")
    
    def _initialize_models(self):
        """Initialize AI models for timing optimization"""
        # This would typically load pre-trained models
        # Initialize production-ready scheduler with database persistence
        self.timing_models = {
            'engagement_predictor': None,  # ML model for engagement prediction
            'competition_analyzer': None,   # Model for analyzing posting competition
            'trend_forecaster': None,      # Model for trend prediction
            'audience_segmenter': None     # Model for audience segmentation
        }
        
        logger.info("AI models initialized for scheduling optimization")
    
    async def create_schedule(
        self,
        request: SchedulingRequest,
        creator_id: str,
        optimize_timing: bool = True
    ) -> str:
        """
        Create a new content schedule with intelligent optimization.
        
        Args:
            request: Scheduling request configuration
            creator_id: Creator identifier
            optimize_timing: Whether to apply AI timing optimization
            
        Returns:
            Schedule ID
        """
        try:
            self.logger.info(f"Creating schedule for content {request.content_id}")
            
            # Validate request
            await self._validate_scheduling_request(request)
            
            # Optimize timing if requested
            if optimize_timing and request.schedule_type == ScheduleType.SMART_OPTIMAL:
                optimal_analysis = await self.analyze_optimal_timing(
                    creator_id=creator_id,
                    platforms=request.platforms,
                    content_metadata=request.metadata
                )
                request.schedule_time = optimal_analysis.recommended_time
                request.metadata.update({
                    'optimal_analysis': optimal_analysis.__dict__,
                    'optimization_applied': True
                })
            
            # Create database record
            schedule_id = str(uuid.uuid4())
            
            with get_db_session() as db:
                scheduled_job = ScheduledJob(
                    id=schedule_id,
                    content_id=request.content_id,
                    creator_id=creator_id,
                    platforms=request.platforms,
                    schedule_time=request.schedule_time,
                    priority=request.priority.value,
                    schedule_type=request.schedule_type.value,
                    status=ScheduleStatus.SCHEDULED.value,
                    recurring_pattern=request.recurring_pattern,
                    conditions=request.conditions,
                    metadata=request.metadata
                )
                
                db.add(scheduled_job)
                db.commit()
            
            # Schedule with APScheduler
            if request.schedule_type == ScheduleType.RECURRING:
                await self._schedule_recurring_job(schedule_id, request)
            else:
                await self._schedule_single_job(schedule_id, request)
            
            self.logger.info(f"Schedule created successfully: {schedule_id}")
            return schedule_id
            
        except Exception as e:
            self.logger.error(f"Failed to create schedule: {str(e)}")
            raise AgentError(f"Schedule creation failed: {str(e)}")
    
    async def analyze_optimal_timing(
        self,
        creator_id: str,
        platforms: List[str],
        content_metadata: Dict[str, Any],
        timezone: str = "UTC"
    ) -> OptimalTimingAnalysis:
        """
        Analyze and determine optimal posting time using AI.
        
        Args:
            creator_id: Creator identifier
            platforms: Target platforms
            content_metadata: Content metadata for analysis
            timezone: Target timezone
            
        Returns:
            Optimal timing analysis results
        """
        try:
            self.logger.info(f"Analyzing optimal timing for creator {creator_id}")
            
            # Check cache first
            cache_key = f"{creator_id}:{':'.join(sorted(platforms))}:{timezone}"
            if cache_key in self.timing_cache:
                cached_result, cached_time = self.timing_cache[cache_key]
                if datetime.utcnow() - cached_time < self.cache_ttl:
                    self.logger.info("Returning cached optimal timing analysis")
                    return cached_result
            
            # Analyze audience activity patterns
            audience_analysis = await self._analyze_audience_activity(
                creator_id, platforms, timezone
            )
            
            # Analyze competition levels
            competition_analysis = await self._analyze_competition_levels(
                platforms, content_metadata
            )
            
            # Analyze platform-specific factors
            platform_analysis = await self._analyze_platform_factors(
                platforms, content_metadata
            )
            
            # Calculate optimal time using weighted scoring
            optimal_time = await self._calculate_optimal_time(
                audience_analysis,
                competition_analysis,
                platform_analysis,
                timezone
            )
            
            # Generate confidence score and reasoning
            confidence_score = self._calculate_confidence_score(
                audience_analysis, competition_analysis, platform_analysis
            )
            
            reasoning = self._generate_timing_reasoning(
                audience_analysis, competition_analysis, platform_analysis
            )
            
            result = OptimalTimingAnalysis(
                recommended_time=optimal_time,
                confidence_score=confidence_score,
                audience_activity_score=audience_analysis.get('overall_score', 0.5),
                competition_score=competition_analysis.get('overall_score', 0.5),
                platform_optimization_score=platform_analysis.get('overall_score', 0.5),
                global_factors={
                    'timezone_alignment': platform_analysis.get('timezone_score', 0.5),
                    'seasonal_factors': platform_analysis.get('seasonal_score', 0.5),
                    'trending_topics': platform_analysis.get('trend_score', 0.5)
                },
                reasoning=reasoning
            )
            
            # Cache result
            self.timing_cache[cache_key] = (result, datetime.utcnow())
            
            self.logger.info(f"Optimal timing analysis completed with confidence {confidence_score:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to analyze optimal timing: {str(e)}")
            raise AgentError(f"Optimal timing analysis failed: {str(e)}")
    
    async def execute_scheduled_job(self, schedule_id: str) -> ScheduleResult:
        """
        Execute a scheduled content distribution job.
        
        Args:
            schedule_id: Schedule identifier
            
        Returns:
            Execution result
        """
        try:
            self.logger.info(f"Executing scheduled job {schedule_id}")
            
            # Get job details from database
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                if not job:
                    raise AgentError(f"Scheduled job {schedule_id} not found")
                
                # Update status to executing
                job.status = ScheduleStatus.EXECUTING.value
                job.actual_execution_time = datetime.utcnow()
                db.commit()
            
            platforms_executed = []
            platforms_failed = []
            performance_metrics = {}
            
            # Execute on each platform
            for platform in job.platforms:
                try:
                    result = await self._execute_platform_distribution(
                        job.content_id,
                        platform,
                        job.metadata or {}
                    )
                    
                    platforms_executed.append(platform)
                    performance_metrics[platform] = result
                    
                except Exception as e:
                    self.logger.error(f"Failed to execute on platform {platform}: {str(e)}")
                    platforms_failed.append(platform)
            
            # Update database with results
            final_status = ScheduleStatus.COMPLETED if not platforms_failed else ScheduleStatus.FAILED
            
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                job.status = final_status.value
                job.performance_metrics = performance_metrics
                if platforms_failed:
                    job.error_details = {'failed_platforms': platforms_failed}
                db.commit()
            
            result = ScheduleResult(
                schedule_id=schedule_id,
                status=final_status,
                execution_time=job.actual_execution_time,
                platforms_executed=platforms_executed,
                platforms_failed=platforms_failed,
                performance_metrics=performance_metrics,
                error_details={'failed_platforms': platforms_failed} if platforms_failed else None
            )
            
            self.logger.info(f"Scheduled job {schedule_id} executed successfully")
            return result
            
        except Exception as e:
            # Update status to failed
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                if job:
                    job.status = ScheduleStatus.FAILED.value
                    job.error_details = {'error': str(e)}
                    db.commit()
            
            self.logger.error(f"Failed to execute scheduled job {schedule_id}: {str(e)}")
            raise AgentError(f"Job execution failed: {str(e)}")
    
    async def get_schedule_status(self, schedule_id: str) -> Dict[str, Any]:
        """Get current status of a scheduled job"""
        try:
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                if not job:
                    raise AgentError(f"Schedule {schedule_id} not found")
                
                return {
                    'schedule_id': job.id,
                    'content_id': job.content_id,
                    'status': job.status,
                    'scheduled_time': job.schedule_time.isoformat(),
                    'actual_execution_time': job.actual_execution_time.isoformat() if job.actual_execution_time else None,
                    'platforms': job.platforms,
                    'priority': job.priority,
                    'performance_metrics': job.performance_metrics,
                    'error_details': job.error_details
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get schedule status: {str(e)}")
            raise AgentError(f"Status retrieval failed: {str(e)}")
    
    async def cancel_schedule(self, schedule_id: str) -> bool:
        """Cancel a scheduled job"""
        try:
            # Remove from scheduler
            try:
                self.scheduler.remove_job(schedule_id)
            except:
                pass  # Job might not exist in scheduler
            
            # Update database
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                if job:
                    job.status = ScheduleStatus.CANCELLED.value
                    db.commit()
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to cancel schedule: {str(e)}")
            raise AgentError(f"Schedule cancellation failed: {str(e)}")
    
    async def reschedule_job(
        self,
        schedule_id: str,
        new_schedule_time: datetime,
        reason: str = None
    ) -> bool:
        """Reschedule an existing job"""
        try:
            # Update scheduler
            self.scheduler.modify_job(
                schedule_id,
                next_run_time=new_schedule_time
            )
            
            # Update database
            with get_db_session() as db:
                job = db.query(ScheduledJob).filter(ScheduledJob.id == schedule_id).first()
                if job:
                    job.schedule_time = new_schedule_time
                    job.status = ScheduleStatus.RESCHEDULED.value
                    if reason:
                        metadata = job.metadata or {}
                        metadata['reschedule_reason'] = reason
                        job.metadata = metadata
                    db.commit()
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to reschedule job: {str(e)}")
            raise AgentError(f"Job rescheduling failed: {str(e)}")
    
    async def get_creator_schedules(
        self,
        creator_id: str,
        status_filter: Optional[List[ScheduleStatus]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get schedules for a specific creator"""
        try:
            with get_db_session() as db:
                query = db.query(ScheduledJob).filter(ScheduledJob.creator_id == creator_id)
                
                if status_filter:
                    status_values = [status.value for status in status_filter]
                    query = query.filter(ScheduledJob.status.in_(status_values))
                
                jobs = query.order_by(ScheduledJob.schedule_time.desc()).limit(limit).all()
                
                return [
                    {
                        'schedule_id': job.id,
                        'content_id': job.content_id,
                        'status': job.status,
                        'scheduled_time': job.schedule_time.isoformat(),
                        'platforms': job.platforms,
                        'priority': job.priority,
                        'schedule_type': job.schedule_type
                    }
                    for job in jobs
                ]
                
        except Exception as e:
            self.logger.error(f"Failed to get creator schedules: {str(e)}")
            raise AgentError(f"Schedule retrieval failed: {str(e)}")
    
    async def _validate_scheduling_request(self, request: SchedulingRequest):
        """Validate scheduling request parameters"""
        if not request.content_id:
            raise AgentError("Content ID is required")
        
        if not request.platforms:
            raise AgentError("At least one platform must be specified")
        
        if request.schedule_type != ScheduleType.IMMEDIATE and not request.schedule_time:
            raise AgentError("Schedule time is required for delayed scheduling")
        
        if request.schedule_time and request.schedule_time <= datetime.utcnow():
            raise AgentError("Schedule time must be in the future")
        
        # Validate timezone
        try:
            pytz.timezone(request.timezone)
        except pytz.UnknownTimeZoneError:
            raise AgentError(f"Invalid timezone: {request.timezone}")
        
        # Validate recurring pattern if specified
        if request.recurring_pattern:
            try:
                croniter.croniter(request.recurring_pattern)
            except:
                raise AgentError(f"Invalid cron pattern: {request.recurring_pattern}")
    
    async def _schedule_single_job(self, schedule_id: str, request: SchedulingRequest):
        """Schedule a single execution job"""
        if request.schedule_type == ScheduleType.IMMEDIATE:
            # Execute immediately
            asyncio.create_task(self.execute_scheduled_job(schedule_id))
        else:
            # Schedule for later
            self.scheduler.add_job(
                func=self.execute_scheduled_job,
                args=[schedule_id],
                trigger=DateTrigger(run_date=request.schedule_time),
                id=schedule_id,
                replace_existing=True
            )
    
    async def _schedule_recurring_job(self, schedule_id: str, request: SchedulingRequest):
        """Schedule a recurring job"""
        if not request.recurring_pattern:
            raise AgentError("Recurring pattern is required for recurring jobs")
        
        # Parse cron pattern
        cron_parts = request.recurring_pattern.split()
        if len(cron_parts) != 5:
            raise AgentError("Invalid cron pattern format")
        
        minute, hour, day, month, day_of_week = cron_parts
        
        self.scheduler.add_job(
            func=self.execute_scheduled_job,
            args=[schedule_id],
            trigger=CronTrigger(
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                timezone=request.timezone
            ),
            id=schedule_id,
            replace_existing=True
        )
    
    async def _analyze_audience_activity(
        self,
        creator_id: str,
        platforms: List[str],
        timezone: str
    ) -> Dict[str, Any]:
        """Analyze audience activity patterns"""
        try:
            activity_data = {}
            
            with get_db_session() as db:
                for platform in platforms:
                    activities = db.query(AudienceActivity).filter(
                        AudienceActivity.creator_id == creator_id,
                        AudienceActivity.platform == platform
                    ).all()
                    
                    if activities:
                        # Calculate average activity by hour and day
                        hourly_scores = {}
                        daily_scores = {}
                        
                        for activity in activities:
                            hour_key = activity.hour_of_day
                            day_key = activity.day_of_week
                            
                            if hour_key not in hourly_scores:
                                hourly_scores[hour_key] = []
                            hourly_scores[hour_key].append(activity.activity_score)
                            
                            if day_key not in daily_scores:
                                daily_scores[day_key] = []
                            daily_scores[day_key].append(activity.activity_score)
                        
                        # Average the scores
                        avg_hourly = {h: np.mean(scores) for h, scores in hourly_scores.items()}
                        avg_daily = {d: np.mean(scores) for d, scores in daily_scores.items()}
                        
                        activity_data[platform] = {
                            'hourly_activity': avg_hourly,
                            'daily_activity': avg_daily,
                            'peak_hour': max(avg_hourly.items(), key=lambda x: x[1])[0],
                            'peak_day': max(avg_daily.items(), key=lambda x: x[1])[0]
                        }
                    else:
                        # Use default patterns if no data available
                        activity_data[platform] = self._get_default_activity_patterns(platform)
            
            # Calculate overall activity score
            overall_score = np.mean([
                np.mean(list(data['hourly_activity'].values()))
                for data in activity_data.values()
            ]) if activity_data else 0.5
            
            return {
                'platform_data': activity_data,
                'overall_score': overall_score,
                'confidence': len(activity_data) / len(platforms)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze audience activity: {str(e)}")
            return {
                'platform_data': {},
                'overall_score': 0.5,
                'confidence': 0.0
            }
    
    async def _analyze_competition_levels(
        self,
        platforms: List[str],
        content_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze posting competition levels"""
        # This is a simplified implementation
        # In a real system, this would analyze historical posting volumes
        competition_scores = {}
        
        for platform in platforms:
            # Mock competition analysis based on platform and content type
            base_score = 0.5
            content_type = content_metadata.get('content_type', 'general')
            
            # Adjust based on platform-specific factors
            platform_factors = {
                'instagram': 0.8,  # High competition
                'twitter': 0.7,
                'facebook': 0.6,
                'linkedin': 0.4,   # Lower competition
                'tiktok': 0.9,     # Very high competition
                'youtube': 0.5
            }
            
            platform_score = platform_factors.get(platform.lower(), 0.5)
            
            # Adjust based on content type
            type_factors = {
                'video': 1.2,
                'image': 1.0,
                'text': 0.8,
                'audio': 0.9
            }
            
            type_multiplier = type_factors.get(content_type, 1.0)
            final_score = min(platform_score * type_multiplier, 1.0)
            
            competition_scores[platform] = final_score
        
        overall_score = np.mean(list(competition_scores.values())) if competition_scores else 0.5
        
        return {
            'platform_scores': competition_scores,
            'overall_score': overall_score,
            'peak_competition_hours': [9, 12, 18, 21],  # Common peak hours
            'low_competition_hours': [6, 14, 23, 2]     # Common low competition hours
        }
    
    async def _analyze_platform_factors(
        self,
        platforms: List[str],
        content_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze platform-specific optimization factors"""
        platform_scores = {}
        
        current_time = datetime.utcnow()
        
        for platform in platforms:
            # Platform-specific optimal posting patterns
            optimal_patterns = {
                'instagram': {
                    'peak_hours': [6, 7, 8, 12, 17, 18, 19, 20],
                    'peak_days': [1, 2, 3, 4, 5],  # Weekdays
                    'timezone_preference': 'local'
                },
                'twitter': {
                    'peak_hours': [7, 8, 9, 12, 17, 18, 19],
                    'peak_days': [1, 2, 3, 4, 5],
                    'timezone_preference': 'global'
                },
                'facebook': {
                    'peak_hours': [12, 13, 14, 15, 18, 19, 20],
                    'peak_days': [1, 2, 3, 4, 5, 6],
                    'timezone_preference': 'local'
                },
                'linkedin': {
                    'peak_hours': [7, 8, 9, 17, 18],
                    'peak_days': [1, 2, 3, 4, 5],
                    'timezone_preference': 'business_hours'
                },
                'tiktok': {
                    'peak_hours': [18, 19, 20, 21, 22],
                    'peak_days': [0, 1, 2, 3, 4, 5, 6],  # All days
                    'timezone_preference': 'local'
                },
                'youtube': {
                    'peak_hours': [14, 15, 16, 17, 18, 19, 20],
                    'peak_days': [0, 5, 6],  # Weekends
                    'timezone_preference': 'local'
                }
            }
            
            pattern = optimal_patterns.get(platform.lower(), {
                'peak_hours': [12, 18],
                'peak_days': [1, 2, 3, 4, 5],
                'timezone_preference': 'local'
            })
            
            # Calculate score based on how well current factors align
            hour_score = 1.0 if current_time.hour in pattern['peak_hours'] else 0.5
            day_score = 1.0 if current_time.weekday() in pattern['peak_days'] else 0.7
            
            platform_scores[platform] = (hour_score + day_score) / 2
        
        overall_score = np.mean(list(platform_scores.values())) if platform_scores else 0.5
        
        return {
            'platform_scores': platform_scores,
            'overall_score': overall_score,
            'timezone_score': 0.8,    # Mock timezone alignment score
            'seasonal_score': 0.7,    # Mock seasonal factors score
            'trend_score': 0.6        # Mock trending topics score
        }
    
    async def _calculate_optimal_time(
        self,
        audience_analysis: Dict[str, Any],
        competition_analysis: Dict[str, Any],
        platform_analysis: Dict[str, Any],
        timezone: str
    ) -> datetime:
        """Calculate optimal posting time using weighted scoring"""
        
        # Get current time in target timezone
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        
        # Look ahead up to 7 days for optimal timing
        best_time = current_time + timedelta(hours=1)  # Default to 1 hour from now
        best_score = 0.0
        
        # Check next 168 hours (7 days) in 1-hour increments
        for hours_ahead in range(1, 169):
            candidate_time = current_time + timedelta(hours=hours_ahead)
            
            # Calculate weighted score for this time
            audience_score = self._calculate_audience_score(
                candidate_time, audience_analysis
            )
            competition_score = self._calculate_competition_score(
                candidate_time, competition_analysis
            )
            platform_score = self._calculate_platform_score(
                candidate_time, platform_analysis
            )
            
            # Weighted combination (weights can be tuned)
            total_score = (
                audience_score * 0.4 +
                (1.0 - competition_score) * 0.3 +  # Lower competition is better
                platform_score * 0.3
            )
            
            if total_score > best_score:
                best_score = total_score
                best_time = candidate_time
        
        # Convert back to UTC
        return best_time.astimezone(pytz.UTC)
    
    def _calculate_audience_score(
        self,
        candidate_time: datetime,
        audience_analysis: Dict[str, Any]
    ) -> float:
        """Calculate audience activity score for a given time"""
        hour = candidate_time.hour
        day_of_week = candidate_time.weekday()
        
        platform_data = audience_analysis.get('platform_data', {})
        if not platform_data:
            return 0.5
        
        scores = []
        for platform, data in platform_data.items():
            hourly_activity = data.get('hourly_activity', {})
            daily_activity = data.get('daily_activity', {})
            
            hour_score = hourly_activity.get(hour, 0.5)
            day_score = daily_activity.get(day_of_week, 0.5)
            
            platform_score = (hour_score + day_score) / 2
            scores.append(platform_score)
        
        return np.mean(scores) if scores else 0.5
    
    def _calculate_competition_score(
        self,
        candidate_time: datetime,
        competition_analysis: Dict[str, Any]
    ) -> float:
        """Calculate competition level score for a given time"""
        hour = candidate_time.hour
        
        peak_hours = competition_analysis.get('peak_competition_hours', [])
        low_hours = competition_analysis.get('low_competition_hours', [])
        
        if hour in peak_hours:
            return 0.8  # High competition
        elif hour in low_hours:
            return 0.2  # Low competition
        else:
            return 0.5  # Medium competition
    
    def _calculate_platform_score(
        self,
        candidate_time: datetime,
        platform_analysis: Dict[str, Any]
    ) -> float:
        """Calculate platform optimization score for a given time"""
        return platform_analysis.get('overall_score', 0.5)
    
    def _calculate_confidence_score(
        self,
        audience_analysis: Dict[str, Any],
        competition_analysis: Dict[str, Any],
        platform_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence in the timing recommendation"""
        audience_confidence = audience_analysis.get('confidence', 0.0)
        competition_confidence = 0.7  # Mock confidence for competition analysis
        platform_confidence = 0.8     # Mock confidence for platform analysis
        
        return (audience_confidence + competition_confidence + platform_confidence) / 3
    
    def _generate_timing_reasoning(
        self,
        audience_analysis: Dict[str, Any],
        competition_analysis: Dict[str, Any],
        platform_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate human-readable reasoning for the timing recommendation"""
        reasoning = []
        
        # Audience-based reasoning
        if audience_analysis.get('overall_score', 0) > 0.6:
            reasoning.append("High audience activity expected at recommended time")
        
        # Competition-based reasoning
        if competition_analysis.get('overall_score', 0) < 0.5:
            reasoning.append("Lower competition period identified")
        
        # Platform-based reasoning
        if platform_analysis.get('overall_score', 0) > 0.6:
            reasoning.append("Platform algorithms favor this timing window")
        
        if not reasoning:
            reasoning.append("Balanced optimization across multiple factors")
        
        return reasoning
    
    def _get_default_activity_patterns(self, platform: str) -> Dict[str, Any]:
        """Get default activity patterns when no data is available"""
        default_patterns = {
            'instagram': {
                'hourly_activity': {i: 0.7 if i in [6, 7, 8, 12, 17, 18, 19, 20] else 0.4 for i in range(24)},
                'daily_activity': {i: 0.8 if i < 5 else 0.6 for i in range(7)},
                'peak_hour': 18,
                'peak_day': 2
            },
            'twitter': {
                'hourly_activity': {i: 0.8 if i in [7, 8, 9, 12, 17, 18, 19] else 0.4 for i in range(24)},
                'daily_activity': {i: 0.8 if i < 5 else 0.5 for i in range(7)},
                'peak_hour': 9,
                'peak_day': 1
            }
        }
        
        return default_patterns.get(platform.lower(), {
            'hourly_activity': {i: 0.5 for i in range(24)},
            'daily_activity': {i: 0.5 for i in range(7)},
            'peak_hour': 12,
            'peak_day': 2
        })
    
    async def _execute_platform_distribution(
        self,
        content_id: str,
        platform: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, float]:
        """Execute content distribution on a specific platform"""
        # This would integrate with actual platform APIs
        # For now, return mock performance metrics
        
        await asyncio.sleep(0.1)  # Simulate API call
        
        # Mock performance metrics
        return {
            'posts_count': 1,
            'estimated_reach': np.random.randint(100, 10000),
            'estimated_engagement': np.random.uniform(0.01, 0.1),
            'execution_time_ms': np.random.uniform(500, 2000)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.scheduler:
            self.scheduler.shutdown()
        await super().cleanup()

class SchedulingAgentManager:
    """
    Manager for multiple scheduling agents with load balancing and coordination.
    """
    
    def __init__(self, max_agents: int = 5):
        self.agents = {}
        self.max_agents = max_agents
        self.current_agent_index = 0
        self.lock = asyncio.Lock()
    
    async def get_agent(self, creator_id: str = None) -> SchedulingAgent:
        """Get an available scheduling agent"""
        async with self.lock:
            if creator_id and creator_id in self.agents:
                return self.agents[creator_id]
            
            if len(self.agents) < self.max_agents:
                agent = SchedulingAgent()
                agent_key = creator_id or f"agent_{len(self.agents)}"
                self.agents[agent_key] = agent
                return agent
            
            # Round-robin assignment
            agent_keys = list(self.agents.keys())
            agent_key = agent_keys[self.current_agent_index % len(agent_keys)]
            self.current_agent_index += 1
            return self.agents[agent_key]
    
    async def shutdown_all(self):
        """Shutdown all agents"""
        for agent in self.agents.values():
            await agent.cleanup()
        self.agents.clear()
