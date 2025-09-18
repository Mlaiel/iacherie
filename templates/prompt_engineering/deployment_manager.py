"""
🎯 Deployment Manager - AI Prompt Template Deployment System
===========================================================

Enterprise-grade deployment management for AI prompt templates with version control,
rollback capabilities, and creator economy deployment strategies.

⚠️  PROTECTION INTELLECTUELLE - Fahed Mlaiel (mlaiel@live.de)
© 2025 Tous droits réservés - Usage commercial interdit sans autorisation

Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Expert + Backend Senior + IA Prompt Engineer
Team: Lead Dev IA + Backend Senior + ML Engineer + Security Expert
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis.asyncio as redis
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, validator
import semver

from core.config import get_settings
from utils.exceptions import DeploymentError, ValidationError
from .security_validator import SecurityValidator
from .performance_monitor import PerformanceMonitor
from .evaluation_framework import EvaluationFramework

logger = logging.getLogger(__name__)
settings = get_settings()


class DeploymentStage(Enum):
    """Deployment stages"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"


class DeploymentStrategy(Enum):
    """Deployment strategies"""
    IMMEDIATE = "immediate"
    ROLLING = "rolling"
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    A_B_TESTING = "a_b_testing"
    CREATOR_ECONOMY_GRADUAL = "creator_economy_gradual"


class DeploymentStatus(Enum):
    """Deployment status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class HealthCheckStatus(Enum):
    """Health check status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class DeploymentTarget:
    """Deployment target configuration"""
    environment: DeploymentStage
    region: str
    capacity_percentage: float
    creator_segments: List[str] = field(default_factory=list)
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    rollback_enabled: bool = True
    health_check_enabled: bool = True
    monitoring_enabled: bool = True


@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    template_id: str
    version: str
    strategy: DeploymentStrategy
    targets: List[DeploymentTarget]
    rollback_threshold: float = 0.8
    success_criteria: Dict[str, float] = field(default_factory=dict)
    timeout_minutes: int = 30
    approval_required: bool = False
    creator_economy_features: Dict[str, bool] = field(default_factory=dict)
    security_validation: bool = True
    performance_monitoring: bool = True
    evaluation_required: bool = True


@dataclass
class DeploymentResult:
    """Deployment result"""
    deployment_id: str
    status: DeploymentStatus
    deployed_version: str
    targets_deployed: List[str]
    deployment_time: datetime
    duration_seconds: int
    health_status: HealthCheckStatus
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    error_message: Optional[str] = None
    rollback_available: bool = True
    creator_feedback: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RollbackConfig:
    """Rollback configuration"""
    deployment_id: str
    target_version: str
    reason: str
    immediate: bool = True
    notify_creators: bool = True
    preserve_data: bool = True


class DeploymentRequest(BaseModel):
    """Deployment request"""
    template_id: str = Field(..., min_length=1)
    version: str = Field(..., regex=r"^\d+\.\d+\.\d+$")
    environment: DeploymentStage
    strategy: DeploymentStrategy = DeploymentStrategy.ROLLING
    target_regions: List[str] = Field(default_factory=lambda: ["global"])
    creator_segments: List[str] = Field(default_factory=list)
    rollback_enabled: bool = True
    approval_required: bool = False
    creator_context: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('version')
    def validate_version(cls, v):
        """Validate semantic version"""
        try:
            semver.parse(v)
            return v
        except ValueError:
            raise ValueError("Invalid semantic version format")


class RollbackRequest(BaseModel):
    """Rollback request"""
    deployment_id: str = Field(..., min_length=1)
    target_version: Optional[str] = None
    reason: str = Field(..., min_length=1)
    immediate: bool = True
    notify_creators: bool = True


class DeploymentManager:
    """
    🎯 Enterprise Deployment Management System
    
    Advanced deployment management with:
    - Multi-stage deployment pipelines
    - Blue-green and canary deployments
    - Creator economy aware deployments
    - Automated rollback capabilities
    - Health monitoring and validation
    - Version control and history
    - Performance impact tracking
    - Security validation integration
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.db_pool: Optional[asyncpg.Pool] = None
        self.mongo_client: Optional[AsyncIOMotorClient] = None
        self.security_validator = SecurityValidator()
        self.performance_monitor = PerformanceMonitor()
        self.evaluation_framework = EvaluationFramework()
        self._active_deployments: Dict[str, Dict] = {}
        self._deployment_history: Dict[str, List] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize deployment manager"""
        try:
            # Initialize Redis connection
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                settings.DATABASE_URL,
                min_size=3,
                max_size=10
            )
            
            # Initialize MongoDB connection
            self.mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
            
            # Create database tables
            await self._create_tables()
            
            # Initialize components
            await self.security_validator.initialize()
            await self.performance_monitor.initialize()
            await self.evaluation_framework.initialize()
            
            # Load active deployments
            await self._load_active_deployments()
            
            # Start background tasks
            asyncio.create_task(self._deployment_monitor_task())
            asyncio.create_task(self._health_check_task())
            
            self._initialized = True
            logger.info("Deployment Manager initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize Deployment Manager: {e}")
            raise DeploymentError(f"Deployment Manager initialization failed: {e}")
    
    async def _create_tables(self) -> None:
        """Create deployment-related database tables"""
        create_deployments_table = """
        CREATE TABLE IF NOT EXISTS deployments (
            id SERIAL PRIMARY KEY,
            deployment_id VARCHAR(255) UNIQUE NOT NULL,
            template_id VARCHAR(255) NOT NULL,
            version VARCHAR(50) NOT NULL,
            environment VARCHAR(50) NOT NULL,
            strategy VARCHAR(50) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            config JSONB NOT NULL,
            targets JSONB,
            deployed_at TIMESTAMP,
            completed_at TIMESTAMP,
            duration_seconds INTEGER,
            health_status VARCHAR(50),
            performance_metrics JSONB,
            error_message TEXT,
            rollback_available BOOLEAN DEFAULT TRUE,
            creator_context JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (template_id, version),
            INDEX (environment, status),
            INDEX (deployed_at DESC)
        );
        """
        
        create_deployment_history_table = """
        CREATE TABLE IF NOT EXISTS deployment_history (
            id SERIAL PRIMARY KEY,
            deployment_id VARCHAR(255) REFERENCES deployments(deployment_id),
            event_type VARCHAR(50) NOT NULL,
            event_data JSONB,
            health_metrics JSONB,
            creator_feedback JSONB,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_rollbacks_table = """
        CREATE TABLE IF NOT EXISTS rollbacks (
            id SERIAL PRIMARY KEY,
            rollback_id VARCHAR(255) UNIQUE NOT NULL,
            deployment_id VARCHAR(255) REFERENCES deployments(deployment_id),
            from_version VARCHAR(50) NOT NULL,
            to_version VARCHAR(50) NOT NULL,
            reason TEXT NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            initiated_by VARCHAR(255),
            completed_at TIMESTAMP,
            creator_notifications_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_deployment_approvals_table = """
        CREATE TABLE IF NOT EXISTS deployment_approvals (
            id SERIAL PRIMARY KEY,
            approval_id VARCHAR(255) UNIQUE NOT NULL,
            deployment_id VARCHAR(255) REFERENCES deployments(deployment_id),
            approver VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            comments TEXT,
            approved_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        async with self.db_pool.acquire() as conn:
            await conn.execute(create_deployments_table)
            await conn.execute(create_deployment_history_table)
            await conn.execute(create_rollbacks_table)
            await conn.execute(create_deployment_approvals_table)
    
    async def _load_active_deployments(self) -> None:
        """Load active deployments from database"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT deployment_id, template_id, version, environment, 
                           strategy, status, config, created_at
                    FROM deployments 
                    WHERE status IN ('pending', 'in_progress', 'paused')
                """)
                
                for row in rows:
                    self._active_deployments[row['deployment_id']] = {
                        "template_id": row['template_id'],
                        "version": row['version'],
                        "environment": row['environment'],
                        "strategy": row['strategy'],
                        "status": row['status'],
                        "config": json.loads(row['config']),
                        "created_at": row['created_at']
                    }
                
                logger.info(f"Loaded {len(self._active_deployments)} active deployments")
        
        except Exception as e:
            logger.error(f"Failed to load active deployments: {e}")
    
    async def deploy_template(self, request: DeploymentRequest) -> str:
        """
        Deploy prompt template to specified environment
        
        Args:
            request: Deployment request configuration
            
        Returns:
            Deployment ID for tracking
        """
        try:
            # Generate deployment ID
            deployment_id = f"deploy_{int(time.time())}_{request.template_id}"
            
            # Validate deployment request
            await self._validate_deployment_request(request)
            
            # Security validation
            if request.strategy != DeploymentStrategy.IMMEDIATE:
                await self._security_pre_deployment_check(request.template_id, request.version)
            
            # Create deployment configuration
            config = await self._create_deployment_config(request)
            
            # Store deployment record
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO deployments 
                    (deployment_id, template_id, version, environment, strategy, 
                     config, creator_context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, deployment_id, request.template_id, request.version,
                    request.environment.value, request.strategy.value,
                    json.dumps(config.__dict__), json.dumps(request.creator_context))
            
            # Add to active deployments
            self._active_deployments[deployment_id] = {
                "template_id": request.template_id,
                "version": request.version,
                "environment": request.environment.value,
                "strategy": request.strategy.value,
                "status": "pending",
                "config": config.__dict__,
                "created_at": datetime.utcnow()
            }
            
            # Check if approval required
            if request.approval_required:
                await self._request_deployment_approval(deployment_id)
                logger.info(f"Deployment {deployment_id} pending approval")
            else:
                # Start deployment asynchronously
                asyncio.create_task(self._execute_deployment(deployment_id, config))
                logger.info(f"Started deployment {deployment_id}")
            
            return deployment_id
        
        except Exception as e:
            logger.error(f"Deployment initiation failed: {e}")
            raise DeploymentError(f"Deployment failed: {e}")
    
    async def _validate_deployment_request(self, request: DeploymentRequest) -> None:
        """Validate deployment request"""
        # Check if template exists
        # In production, this would check the template registry
        if not request.template_id:
            raise ValidationError("Template ID is required")
        
        # Validate version format
        try:
            semver.parse(request.version)
        except ValueError:
            raise ValidationError("Invalid semantic version format")
        
        # Environment-specific validations
        if request.environment == DeploymentStage.PRODUCTION:
            if request.strategy == DeploymentStrategy.IMMEDIATE:
                raise ValidationError("Immediate deployment not allowed in production")
        
        # Creator segment validation
        if request.creator_segments:
            valid_segments = ["musicians", "bloggers", "photographers", "influencers", "educators"]
            invalid_segments = set(request.creator_segments) - set(valid_segments)
            if invalid_segments:
                raise ValidationError(f"Invalid creator segments: {invalid_segments}")
    
    async def _security_pre_deployment_check(self, template_id: str, version: str) -> None:
        """Perform security check before deployment"""
        try:
            # Get template content (placeholder - would fetch from registry)
            template_content = f"Template {template_id} version {version}"
            
            # Security validation
            security_result = await self.security_validator.validate_template(template_content, template_id)
            
            if not security_result.is_safe:
                raise ValidationError(f"Template failed security validation: {security_result.issues}")
            
            logger.info(f"Template {template_id} v{version} passed security validation")
        
        except Exception as e:
            logger.error(f"Security pre-deployment check failed: {e}")
            raise DeploymentError(f"Security validation failed: {e}")
    
    async def _create_deployment_config(self, request: DeploymentRequest) -> DeploymentConfig:
        """Create deployment configuration from request"""
        targets = []
        
        for region in request.target_regions:
            target = DeploymentTarget(
                environment=request.environment,
                region=region,
                capacity_percentage=100.0,  # Full deployment by default
                creator_segments=request.creator_segments,
                rollback_enabled=request.rollback_enabled
            )
            targets.append(target)
        
        # Strategy-specific configurations
        if request.strategy == DeploymentStrategy.CANARY:
            # Canary deployment - start with 10% capacity
            for target in targets:
                target.capacity_percentage = 10.0
        elif request.strategy == DeploymentStrategy.A_B_TESTING:
            # A/B testing - 50/50 split
            for target in targets:
                target.capacity_percentage = 50.0
        
        return DeploymentConfig(
            template_id=request.template_id,
            version=request.version,
            strategy=request.strategy,
            targets=targets,
            approval_required=request.approval_required,
            creator_economy_features=self._extract_creator_features(request.creator_context)
        )
    
    def _extract_creator_features(self, creator_context: Dict[str, Any]) -> Dict[str, bool]:
        """Extract creator economy features from context"""
        return {
            "multi_creator_support": bool(creator_context.get("creator_type")),
            "monetization_enabled": bool(creator_context.get("monetization_focus")),
            "collaboration_features": bool(creator_context.get("collaboration")),
            "analytics_integration": bool(creator_context.get("analytics"))
        }
    
    async def _request_deployment_approval(self, deployment_id: str) -> None:
        """Request approval for deployment"""
        try:
            approval_id = f"approve_{deployment_id}"
            
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO deployment_approvals 
                    (approval_id, deployment_id, approver, status)
                    VALUES ($1, $2, $3, $4)
                """, approval_id, deployment_id, "admin", "pending")
            
            # In production, this would send notifications to approvers
            logger.info(f"Approval requested for deployment {deployment_id}")
        
        except Exception as e:
            logger.error(f"Failed to request approval: {e}")
    
    async def _execute_deployment(self, deployment_id: str, config: DeploymentConfig) -> None:
        """Execute deployment based on strategy"""
        try:
            # Update status to in_progress
            await self._update_deployment_status(deployment_id, DeploymentStatus.IN_PROGRESS)
            
            start_time = datetime.utcnow()
            
            # Execute based on strategy
            if config.strategy == DeploymentStrategy.IMMEDIATE:
                success = await self._immediate_deployment(deployment_id, config)
            elif config.strategy == DeploymentStrategy.ROLLING:
                success = await self._rolling_deployment(deployment_id, config)
            elif config.strategy == DeploymentStrategy.BLUE_GREEN:
                success = await self._blue_green_deployment(deployment_id, config)
            elif config.strategy == DeploymentStrategy.CANARY:
                success = await self._canary_deployment(deployment_id, config)
            else:
                success = await self._default_deployment(deployment_id, config)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            # Update deployment status
            if success:
                await self._complete_deployment(deployment_id, duration)
            else:
                await self._fail_deployment(deployment_id, "Deployment execution failed")
        
        except Exception as e:
            logger.error(f"Deployment execution failed for {deployment_id}: {e}")
            await self._fail_deployment(deployment_id, str(e))
    
    async def _immediate_deployment(self, deployment_id: str, config: DeploymentConfig) -> bool:
        """Execute immediate deployment"""
        try:
            logger.info(f"Executing immediate deployment {deployment_id}")
            
            # Simulate deployment steps
            await asyncio.sleep(1)  # Deployment simulation
            
            # Perform health check
            health_status = await self._perform_health_check(deployment_id, config)
            
            # Record deployment event
            await self._record_deployment_event(
                deployment_id, "immediate_deployment_completed",
                {"health_status": health_status.value}
            )
            
            return health_status in [HealthCheckStatus.HEALTHY, HealthCheckStatus.DEGRADED]
        
        except Exception as e:
            logger.error(f"Immediate deployment failed: {e}")
            return False
    
    async def _rolling_deployment(self, deployment_id: str, config: DeploymentConfig) -> bool:
        """Execute rolling deployment"""
        try:
            logger.info(f"Executing rolling deployment {deployment_id}")
            
            success_count = 0
            total_targets = len(config.targets)
            
            for i, target in enumerate(config.targets):
                logger.info(f"Deploying to target {i+1}/{total_targets}: {target.region}")
                
                # Simulate target deployment
                await asyncio.sleep(2)
                
                # Health check for this target
                target_health = await self._perform_target_health_check(deployment_id, target)
                
                if target_health == HealthCheckStatus.HEALTHY:
                    success_count += 1
                    logger.info(f"Target {target.region} deployed successfully")
                else:
                    logger.error(f"Target {target.region} deployment failed")
                    
                    # Check if we should continue or rollback
                    success_rate = success_count / (i + 1)
                    if success_rate < config.rollback_threshold:
                        logger.warning(f"Success rate {success_rate:.2f} below threshold, stopping deployment")
                        break
                
                # Record progress
                await self._record_deployment_event(
                    deployment_id, "target_deployed",
                    {"target": target.region, "health": target_health.value, "progress": f"{i+1}/{total_targets}"}
                )
            
            overall_success_rate = success_count / total_targets
            return overall_success_rate >= config.rollback_threshold
        
        except Exception as e:
            logger.error(f"Rolling deployment failed: {e}")
            return False
    
    async def _blue_green_deployment(self, deployment_id: str, config: DeploymentConfig) -> bool:
        """Execute blue-green deployment"""
        try:
            logger.info(f"Executing blue-green deployment {deployment_id}")
            
            # Deploy to green environment
            logger.info("Deploying to green environment")
            await asyncio.sleep(3)
            
            # Health check green environment
            green_health = await self._perform_health_check(deployment_id, config)
            
            if green_health != HealthCheckStatus.HEALTHY:
                logger.error("Green environment health check failed")
                return False
            
            # Switch traffic to green
            logger.info("Switching traffic to green environment")
            await asyncio.sleep(1)
            
            # Final health check
            final_health = await self._perform_health_check(deployment_id, config)
            
            await self._record_deployment_event(
                deployment_id, "blue_green_completed",
                {"green_health": green_health.value, "final_health": final_health.value}
            )
            
            return final_health == HealthCheckStatus.HEALTHY
        
        except Exception as e:
            logger.error(f"Blue-green deployment failed: {e}")
            return False
    
    async def _canary_deployment(self, deployment_id: str, config: DeploymentConfig) -> bool:
        """Execute canary deployment"""
        try:
            logger.info(f"Executing canary deployment {deployment_id}")
            
            # Deploy canary (10% traffic)
            logger.info("Deploying canary version (10% traffic)")
            await asyncio.sleep(2)
            
            # Monitor canary for specified duration
            canary_duration = 300  # 5 minutes
            logger.info(f"Monitoring canary for {canary_duration} seconds")
            
            # Simulate monitoring
            await asyncio.sleep(5)  # Shortened for demo
            
            # Check canary metrics
            canary_metrics = await self._collect_canary_metrics(deployment_id)
            
            # Decide whether to proceed
            canary_success = canary_metrics.get("error_rate", 0) < 0.01  # < 1% error rate
            
            if canary_success:
                logger.info("Canary successful, proceeding with full deployment")
                
                # Deploy to remaining traffic
                await asyncio.sleep(3)
                
                final_health = await self._perform_health_check(deployment_id, config)
                
                await self._record_deployment_event(
                    deployment_id, "canary_completed",
                    {"canary_metrics": canary_metrics, "final_health": final_health.value}
                )
                
                return final_health == HealthCheckStatus.HEALTHY
            else:
                logger.error("Canary failed, rolling back")
                await self._record_deployment_event(
                    deployment_id, "canary_failed",
                    {"canary_metrics": canary_metrics}
                )
                return False
        
        except Exception as e:
            logger.error(f"Canary deployment failed: {e}")
            return False
    
    async def _default_deployment(self, deployment_id: str, config: DeploymentConfig) -> bool:
        """Execute default deployment strategy"""
        logger.info(f"Executing default deployment {deployment_id}")
        return await self._immediate_deployment(deployment_id, config)
    
    async def _perform_health_check(self, deployment_id: str, config: DeploymentConfig) -> HealthCheckStatus:
        """Perform health check on deployment"""
        try:
            # Simulate health check
            await asyncio.sleep(1)
            
            # In production, this would check:
            # - Template response quality
            # - Performance metrics
            # - Error rates
            # - Creator satisfaction
            
            # For demo, randomly determine health
            import random
            health_score = random.uniform(0.8, 1.0)  # Simulated high success rate
            
            if health_score >= 0.95:
                return HealthCheckStatus.HEALTHY
            elif health_score >= 0.85:
                return HealthCheckStatus.DEGRADED
            else:
                return HealthCheckStatus.UNHEALTHY
        
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckStatus.UNKNOWN
    
    async def _perform_target_health_check(self, deployment_id: str, target: DeploymentTarget) -> HealthCheckStatus:
        """Perform health check on specific target"""
        # Similar to general health check but target-specific
        return await self._perform_health_check(deployment_id, None)
    
    async def _collect_canary_metrics(self, deployment_id: str) -> Dict[str, float]:
        """Collect metrics from canary deployment"""
        try:
            # In production, this would collect real metrics
            import random
            
            return {
                "error_rate": random.uniform(0.001, 0.005),  # Low error rate
                "latency_p95": random.uniform(200, 400),     # Milliseconds
                "throughput": random.uniform(80, 120),       # Requests per second
                "creator_satisfaction": random.uniform(0.85, 0.95)
            }
        
        except Exception as e:
            logger.error(f"Failed to collect canary metrics: {e}")
            return {"error_rate": 1.0}  # High error rate on failure
    
    async def _update_deployment_status(self, deployment_id: str, status: DeploymentStatus) -> None:
        """Update deployment status"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE deployments SET status = $1 WHERE deployment_id = $2
                """, status.value, deployment_id)
            
            # Update active deployments cache
            if deployment_id in self._active_deployments:
                self._active_deployments[deployment_id]["status"] = status.value
        
        except Exception as e:
            logger.error(f"Failed to update deployment status: {e}")
    
    async def _complete_deployment(self, deployment_id: str, duration_seconds: float) -> None:
        """Mark deployment as completed"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE deployments 
                    SET status = $1, completed_at = NOW(), duration_seconds = $2
                    WHERE deployment_id = $3
                """, DeploymentStatus.COMPLETED.value, int(duration_seconds), deployment_id)
            
            # Remove from active deployments
            if deployment_id in self._active_deployments:
                del self._active_deployments[deployment_id]
            
            logger.info(f"Deployment {deployment_id} completed successfully in {duration_seconds:.1f}s")
        
        except Exception as e:
            logger.error(f"Failed to complete deployment: {e}")
    
    async def _fail_deployment(self, deployment_id: str, error_message: str) -> None:
        """Mark deployment as failed"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE deployments 
                    SET status = $1, error_message = $2, completed_at = NOW()
                    WHERE deployment_id = $3
                """, DeploymentStatus.FAILED.value, error_message, deployment_id)
            
            # Remove from active deployments
            if deployment_id in self._active_deployments:
                del self._active_deployments[deployment_id]
            
            logger.error(f"Deployment {deployment_id} failed: {error_message}")
        
        except Exception as e:
            logger.error(f"Failed to mark deployment as failed: {e}")
    
    async def _record_deployment_event(self, deployment_id: str, event_type: str, event_data: Dict[str, Any]) -> None:
        """Record deployment event"""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO deployment_history 
                    (deployment_id, event_type, event_data)
                    VALUES ($1, $2, $3)
                """, deployment_id, event_type, json.dumps(event_data))
        
        except Exception as e:
            logger.error(f"Failed to record deployment event: {e}")
    
    async def rollback_deployment(self, request: RollbackRequest) -> str:
        """
        Rollback deployment to previous version
        
        Args:
            request: Rollback request configuration
            
        Returns:
            Rollback ID for tracking
        """
        try:
            rollback_id = f"rollback_{int(time.time())}"
            
            # Get deployment details
            async with self.db_pool.acquire() as conn:
                deployment = await conn.fetchrow("""
                    SELECT template_id, version, environment FROM deployments 
                    WHERE deployment_id = $1
                """, request.deployment_id)
                
                if not deployment:
                    raise DeploymentError(f"Deployment {request.deployment_id} not found")
                
                # Determine target version for rollback
                target_version = request.target_version
                if not target_version:
                    # Get previous successful version
                    prev_deployment = await conn.fetchrow("""
                        SELECT version FROM deployments 
                        WHERE template_id = $1 AND environment = $2 
                        AND status = 'completed' AND deployment_id != $3
                        ORDER BY completed_at DESC LIMIT 1
                    """, deployment['template_id'], deployment['environment'], request.deployment_id)
                    
                    if prev_deployment:
                        target_version = prev_deployment['version']
                    else:
                        raise DeploymentError("No previous version available for rollback")
                
                # Create rollback record
                await conn.execute("""
                    INSERT INTO rollbacks 
                    (rollback_id, deployment_id, from_version, to_version, reason, initiated_by)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, rollback_id, request.deployment_id, deployment['version'],
                    target_version, request.reason, "system")
            
            # Execute rollback
            await self._execute_rollback(rollback_id, request)
            
            logger.info(f"Rollback {rollback_id} initiated for deployment {request.deployment_id}")
            return rollback_id
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            raise DeploymentError(f"Rollback failed: {e}")
    
    async def _execute_rollback(self, rollback_id: str, request: RollbackRequest) -> None:
        """Execute rollback operation"""
        try:
            # Simulate rollback execution
            logger.info(f"Executing rollback {rollback_id}")
            
            if request.immediate:
                # Immediate rollback
                await asyncio.sleep(2)
            else:
                # Gradual rollback
                await asyncio.sleep(5)
            
            # Update rollback status
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE rollbacks SET status = 'completed', completed_at = NOW()
                    WHERE rollback_id = $1
                """, rollback_id)
            
            # Send creator notifications if requested
            if request.notify_creators:
                await self._notify_creators_rollback(rollback_id, request)
            
            logger.info(f"Rollback {rollback_id} completed successfully")
        
        except Exception as e:
            logger.error(f"Rollback execution failed: {e}")
    
    async def _notify_creators_rollback(self, rollback_id: str, request: RollbackRequest) -> None:
        """Notify creators about rollback"""
        # In production, this would send notifications to affected creators
        logger.info(f"Creator notifications sent for rollback {rollback_id}")
    
    async def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status and details"""
        try:
            async with self.db_pool.acquire() as conn:
                deployment = await conn.fetchrow("""
                    SELECT * FROM deployments WHERE deployment_id = $1
                """, deployment_id)
                
                if not deployment:
                    return None
                
                # Get deployment history
                history = await conn.fetch("""
                    SELECT event_type, event_data, timestamp 
                    FROM deployment_history 
                    WHERE deployment_id = $1 
                    ORDER BY timestamp
                """, deployment_id)
                
                result = dict(deployment)
                result['history'] = [dict(h) for h in history]
                
                # Parse JSON fields
                if result['config']:
                    result['config'] = json.loads(result['config'])
                if result['creator_context']:
                    result['creator_context'] = json.loads(result['creator_context'])
                
                return result
        
        except Exception as e:
            logger.error(f"Failed to get deployment status: {e}")
            return None
    
    async def get_deployment_history(self, template_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get deployment history for a template"""
        try:
            async with self.db_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT deployment_id, version, environment, strategy, status,
                           deployed_at, completed_at, duration_seconds, health_status
                    FROM deployments 
                    WHERE template_id = $1 
                    ORDER BY deployed_at DESC 
                    LIMIT $2
                """, template_id, limit)
                
                return [dict(row) for row in rows]
        
        except Exception as e:
            logger.error(f"Failed to get deployment history: {e}")
            return []
    
    async def _deployment_monitor_task(self) -> None:
        """Background task for monitoring active deployments"""
        try:
            while True:
                await asyncio.sleep(60)  # Check every minute
                
                if not self._initialized:
                    continue
                
                try:
                    # Check for stuck deployments
                    current_time = datetime.utcnow()
                    
                    for deployment_id, deployment in list(self._active_deployments.items()):
                        age = (current_time - deployment['created_at']).total_seconds()
                        
                        # If deployment is running for more than 30 minutes, mark as failed
                        if age > 1800:  # 30 minutes
                            logger.warning(f"Deployment {deployment_id} timed out")
                            await self._fail_deployment(deployment_id, "Deployment timeout")
                
                except Exception as e:
                    logger.error(f"Deployment monitoring error: {e}")
        
        except asyncio.CancelledError:
            logger.info("Deployment monitor task cancelled")
        except Exception as e:
            logger.error(f"Deployment monitor task failed: {e}")
    
    async def _health_check_task(self) -> None:
        """Background task for periodic health checks"""
        try:
            while True:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                if not self._initialized:
                    continue
                
                try:
                    # Perform health checks on recent deployments
                    cutoff_time = datetime.utcnow() - timedelta(hours=24)
                    
                    async with self.db_pool.acquire() as conn:
                        deployments = await conn.fetch("""
                            SELECT deployment_id, template_id, version 
                            FROM deployments 
                            WHERE status = 'completed' AND completed_at >= $1
                        """, cutoff_time)
                        
                        for deployment in deployments:
                            try:
                                # Perform health check
                                config = DeploymentConfig(
                                    template_id=deployment['template_id'],
                                    version=deployment['version'],
                                    strategy=DeploymentStrategy.IMMEDIATE,
                                    targets=[]
                                )
                                
                                health = await self._perform_health_check(
                                    deployment['deployment_id'], config
                                )
                                
                                # Update health status
                                await conn.execute("""
                                    UPDATE deployments SET health_status = $1 
                                    WHERE deployment_id = $2
                                """, health.value, deployment['deployment_id'])
                                
                                # Record health check event
                                await self._record_deployment_event(
                                    deployment['deployment_id'],
                                    "health_check",
                                    {"status": health.value}
                                )
                            
                            except Exception as e:
                                logger.error(f"Health check failed for {deployment['deployment_id']}: {e}")
                
                except Exception as e:
                    logger.error(f"Health check task error: {e}")
        
        except asyncio.CancelledError:
            logger.info("Health check task cancelled")
        except Exception as e:
            logger.error(f"Health check task failed: {e}")
    
    async def get_deployment_metrics(self, template_id: str, days: int = 7) -> Dict[str, Any]:
        """Get deployment metrics for a template"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            async with self.db_pool.acquire() as conn:
                metrics = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_deployments,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                        AVG(duration_seconds) as avg_duration,
                        MAX(duration_seconds) as max_duration
                    FROM deployments 
                    WHERE template_id = $1 AND created_at >= $2
                """, template_id, cutoff_date)
                
                rollback_metrics = await conn.fetchrow("""
                    SELECT COUNT(*) as rollback_count
                    FROM rollbacks r
                    JOIN deployments d ON r.deployment_id = d.deployment_id
                    WHERE d.template_id = $1 AND r.created_at >= $2
                """, template_id, cutoff_date)
                
                result = dict(metrics) if metrics else {}
                result['rollbacks'] = rollback_metrics['rollback_count'] if rollback_metrics else 0
                result['success_rate'] = (
                    result['successful'] / result['total_deployments'] 
                    if result.get('total_deployments', 0) > 0 else 0
                )
                
                return result
        
        except Exception as e:
            logger.error(f"Failed to get deployment metrics: {e}")
            return {}
    
    async def cleanup(self) -> None:
        """Cleanup deployment manager resources"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.db_pool:
                await self.db_pool.close()
            
            if self.mongo_client:
                self.mongo_client.close()
            
            logger.info("Deployment Manager cleanup completed")
        
        except Exception as e:
            logger.error(f"Deployment Manager cleanup failed: {e}")


# Global deployment manager instance
deployment_manager = DeploymentManager()