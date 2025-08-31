"""
 Challenge System Index - IA Influencer Agent Platform Enterprise
===================================================================
Module: backend/core/challenges/index.py
Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
Type: Industrial Challenge System Registry - Production-Ready
Responsibility: Centralized challenge system management and service orchestration
============================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Email: mlaiel@live.de

BUSINESS LOGIC:
Service Registry → Dependency Injection → Factory Pattern → 
Configuration Management → Performance Monitoring → Health Checks

CHALLENGE SYSTEM INDEX ARCHITECTURE:
Service Locator → Factory Registry → Configuration Manager → 
Health Monitor → Performance Tracker → Resource Manager
"""

from typing import Dict, List, Optional, Any, Type, TypeVar, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone
import logging
import asyncio
from contextlib import asynccontextmanager

from .challenge_engine import ChallengeEngine, ChallengeConfiguration
from .competition_manager import CompetitionManager, CompetitionConfiguration  
from .scoring_system import ScoringSystem, ScoreCalculator, RankingEngine, LeaderboardManager
from .challenge_validator import ChallengeValidator, ValidationResult

T = TypeVar('T')

class ServiceType(Enum):
    """Available service types in challenge system"""
    CHALLENGE_ENGINE = "challenge_engine"
    COMPETITION_MANAGER = "competition_manager"
    SCORING_SYSTEM = "scoring_system"
    CHALLENGE_VALIDATOR = "challenge_validator"
    SCORE_CALCULATOR = "score_calculator"
    RANKING_ENGINE = "ranking_engine"
    LEADERBOARD_MANAGER = "leaderboard_manager"

class ServiceStatus(Enum):
    """Service status levels"""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    STOPPED = "stopped"

@dataclass
class ServiceConfiguration:
    """Service configuration specification"""
    service_type: ServiceType
    enabled: bool = True
    auto_start: bool = True
    health_check_interval: int = 60
    performance_monitoring: bool = True
    cache_enabled: bool = True
    cache_ttl: int = 300
    retry_attempts: int = 3
    timeout_seconds: int = 30
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[ServiceType] = field(default_factory=list)

@dataclass  
class ServiceMetrics:
    """Service performance metrics"""
    service_type: ServiceType
    status: ServiceStatus
    uptime_seconds: float
    requests_total: int
    requests_success: int
    requests_failed: int
    average_response_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    last_health_check: datetime
    error_rate: float = 0.0
    throughput_per_minute: float = 0.0

class ChallengeSystemRegistry:
    """Centralized registry and orchestrator for challenge system services"""
    
    def __init__(self,
                 challenge_repository=None,
                 competition_repository=None,
                 user_service=None,
                 analytics_service=None,
                 notification_service=None,
                 reward_service=None,
                 cache_service=None,
                 fraud_detection_service=None,
                 streaming_service=None,
                 matchmaking_service=None,
                 content_service=None,
                 payment_service=None,
                 virtual_economy_service=None,
                 gamification_service=None):
        """Initialize challenge system registry with all dependencies"""
        # External dependencies
        self.challenge_repository = challenge_repository
        self.competition_repository = competition_repository
        self.user_service = user_service
        self.analytics_service = analytics_service
        self.notification_service = notification_service
        self.reward_service = reward_service
        self.cache_service = cache_service
        self.fraud_detection_service = fraud_detection_service
        self.streaming_service = streaming_service
        self.matchmaking_service = matchmaking_service
        self.content_service = content_service
        self.payment_service = payment_service
        self.virtual_economy_service = virtual_economy_service
        self.gamification_service = gamification_service
        
        self.logger = logging.getLogger(__name__)
        
        # Service instances registry
        self._services: Dict[ServiceType, Any] = {}
        
        # Service configurations
        self._service_configs: Dict[ServiceType, ServiceConfiguration] = {}
        
        # Service metrics
        self._service_metrics: Dict[ServiceType, ServiceMetrics] = {}
        
        # Service startup order based on dependencies
        self._startup_order = [
            ServiceType.SCORE_CALCULATOR,
            ServiceType.RANKING_ENGINE,
            ServiceType.LEADERBOARD_MANAGER,
            ServiceType.CHALLENGE_VALIDATOR,
            ServiceType.SCORING_SYSTEM,
            ServiceType.CHALLENGE_ENGINE,
            ServiceType.COMPETITION_MANAGER
        ]
        
        # Initialize default configurations
        self._initialize_default_configs()
        
        # System state
        self._system_started = False
        self._startup_time = None
    
    def _initialize_default_configs(self):
        """Initialize default service configurations"""
        # Challenge Engine Configuration
        self._service_configs[ServiceType.CHALLENGE_ENGINE] = ServiceConfiguration(
            service_type=ServiceType.CHALLENGE_ENGINE,
            enabled=True,
            health_check_interval=60,
            cache_enabled=True,
            cache_ttl=600,
            dependencies=[ServiceType.CHALLENGE_VALIDATOR, ServiceType.SCORING_SYSTEM]
        )
        
        # Competition Manager Configuration
        self._service_configs[ServiceType.COMPETITION_MANAGER] = ServiceConfiguration(
            service_type=ServiceType.COMPETITION_MANAGER,
            enabled=True,
            health_check_interval=30,
            cache_enabled=True,
            cache_ttl=300,
            dependencies=[ServiceType.CHALLENGE_ENGINE, ServiceType.SCORING_SYSTEM]
        )
        
        # Scoring System Configuration
        self._service_configs[ServiceType.SCORING_SYSTEM] = ServiceConfiguration(
            service_type=ServiceType.SCORING_SYSTEM,
            enabled=True,
            health_check_interval=45,
            cache_enabled=True,
            cache_ttl=300,
            dependencies=[ServiceType.SCORE_CALCULATOR, ServiceType.RANKING_ENGINE, ServiceType.LEADERBOARD_MANAGER]
        )
        
        # Challenge Validator Configuration
        self._service_configs[ServiceType.CHALLENGE_VALIDATOR] = ServiceConfiguration(
            service_type=ServiceType.CHALLENGE_VALIDATOR,
            enabled=True,
            health_check_interval=120,
            cache_enabled=False,  # Validation should be fresh
            dependencies=[]
        )
        
        # Score Calculator Configuration
        self._service_configs[ServiceType.SCORE_CALCULATOR] = ServiceConfiguration(
            service_type=ServiceType.SCORE_CALCULATOR,
            enabled=True,
            health_check_interval=300,
            cache_enabled=True,
            cache_ttl=600,
            dependencies=[]
        )
        
        # Ranking Engine Configuration
        self._service_configs[ServiceType.RANKING_ENGINE] = ServiceConfiguration(
            service_type=ServiceType.RANKING_ENGINE,
            enabled=True,
            health_check_interval=120,
            cache_enabled=True,
            cache_ttl=300,
            dependencies=[ServiceType.SCORE_CALCULATOR]
        )
        
        # Leaderboard Manager Configuration
        self._service_configs[ServiceType.LEADERBOARD_MANAGER] = ServiceConfiguration(
            service_type=ServiceType.LEADERBOARD_MANAGER,
            enabled=True,
            health_check_interval=60,
            cache_enabled=True,
            cache_ttl=120,  # Frequent updates
            dependencies=[ServiceType.RANKING_ENGINE]
        )
    
    async def start_system(self) -> Dict[str, Any]:
        """Start the complete challenge system"""



        try:
            self.logger.info("Starting Challenge System...")
            start_time = datetime.now()
            
            startup_results = {
                "success": True,
                "services_started": [],
                "services_failed": [],
                "startup_time_seconds": 0.0,
                "system_status": "healthy"
            }
            
            # Start services in dependency order
            for service_type in self._startup_order:
                config = self._service_configs.get(service_type)
                
                if not config or not config.enabled:
                    continue
                
                try:
                    # Check dependencies are running
                    if not await self._check_dependencies_ready(service_type):
                        startup_results["services_failed"].append({
                            "service": service_type.value,
                            "error": "Dependencies not ready"
                        })
                        continue
                    
                    # Start service
                    service = await self._start_service(service_type, config)
                    
                    if service:
                        self._services[service_type] = service
                        startup_results["services_started"].append(service_type.value)
                        
                        # Initialize metrics
                        self._service_metrics[service_type] = ServiceMetrics(
                            service_type=service_type,
                            status=ServiceStatus.HEALTHY,
                            uptime_seconds=0.0,
                            requests_total=0,
                            requests_success=0,
                            requests_failed=0,
                            average_response_time=0.0,
                            memory_usage_mb=0.0,
                            cpu_usage_percent=0.0,
                            last_health_check=datetime.now(timezone.utc)
                        )
                        
                        self.logger.info(f"Service started: {service_type.value}")
                    else:
                        startup_results["services_failed"].append({
                            "service": service_type.value,
                            "error": "Service initialization failed"
                        })
                
                except Exception as e:
                    self.logger.error(f"Failed to start service {service_type.value}: {str(e)}")
                    startup_results["services_failed"].append({
                        "service": service_type.value,
                        "error": str(e)
                    })
            
            # Calculate startup time
            startup_time = (datetime.now() - start_time).total_seconds()
            startup_results["startup_time_seconds"] = startup_time
            
            # Determine overall success
            if startup_results["services_failed"]:
                startup_results["success"] = False
                startup_results["system_status"] = "degraded"
            
            # Mark system as started
            self._system_started = True
            self._startup_time = start_time
            
            # Start background monitoring
            if startup_results["success"]:
                asyncio.create_task(self._start_monitoring())
            
            self.logger.info(f"Challenge System startup completed in {startup_time:.2f} seconds")
            
            return startup_results
            
        except Exception as e:
            self.logger.error(f"Challenge System startup failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "system_status": "unhealthy"
            }
    
    async def _start_service(self, service_type: ServiceType, config: ServiceConfiguration) -> Optional[Any]:
        """Start individual service"""



        try:
            if service_type == ServiceType.CHALLENGE_ENGINE:
                return ChallengeEngine(
                    challenge_repository=self.challenge_repository,
                    user_service=self.user_service,
                    analytics_service=self.analytics_service,
                    notification_service=self.notification_service,
                    reward_service=self.reward_service,
                    validation_service=self._services.get(ServiceType.CHALLENGE_VALIDATOR),
                    gamification_service=self.gamification_service
                )
            
            elif service_type == ServiceType.COMPETITION_MANAGER:
                return CompetitionManager(
                    competition_repository=self.competition_repository,
                    challenge_repository=self.challenge_repository,
                    user_service=self.user_service,
                    analytics_service=self.analytics_service,
                    notification_service=self.notification_service,
                    reward_service=self.reward_service,
                    streaming_service=self.streaming_service,
                    matchmaking_service=self.matchmaking_service
                )
            
            elif service_type == ServiceType.SCORING_SYSTEM:
                return ScoringSystem(
                    analytics_service=self.analytics_service,
                    user_service=self.user_service,
                    cache_service=self.cache_service,
                    notification_service=self.notification_service
                )
            
            elif service_type == ServiceType.CHALLENGE_VALIDATOR:
                return ChallengeValidator(
                    analytics_service=self.analytics_service,
                    user_service=self.user_service,
                    content_service=self.content_service,
                    fraud_detection_service=self.fraud_detection_service
                )
            
            elif service_type == ServiceType.SCORE_CALCULATOR:
                return ScoreCalculator()
            
            elif service_type == ServiceType.RANKING_ENGINE:
                score_calculator = self._services.get(ServiceType.SCORE_CALCULATOR)
                if score_calculator:
                    return RankingEngine(score_calculator)
            
            elif service_type == ServiceType.LEADERBOARD_MANAGER:
                ranking_engine = self._services.get(ServiceType.RANKING_ENGINE)
                if ranking_engine:
                    return LeaderboardManager(ranking_engine)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to instantiate service {service_type.value}: {str(e)}")
            return None
    
    async def _check_dependencies_ready(self, service_type: ServiceType) -> bool:
        """Check if service dependencies are ready"""
        config = self._service_configs.get(service_type)
        if not config:
            return True
        
        for dependency in config.dependencies:
            if dependency not in self._services:
                return False
            
            # Check dependency health
            metrics = self._service_metrics.get(dependency)
            if metrics and metrics.status != ServiceStatus.HEALTHY:
                return False
        
        return True
    
    def get_service(self, service_type: ServiceType) -> Optional[Any]:
        """Get service instance"""



        return self._services.get(service_type)
    
    def get_challenge_engine(self) -> Optional[ChallengeEngine]:
        """Get challenge engine instance"""



        return self.get_service(ServiceType.CHALLENGE_ENGINE)
    
    def get_competition_manager(self) -> Optional[CompetitionManager]:
        """Get competition manager instance"""



        return self.get_service(ServiceType.COMPETITION_MANAGER)
    
    def get_scoring_system(self) -> Optional[ScoringSystem]:
        """Get scoring system instance"""



        return self.get_service(ServiceType.SCORING_SYSTEM)
    
    def get_challenge_validator(self) -> Optional[ChallengeValidator]:
        """Get challenge validator instance"""



        return self.get_service(ServiceType.CHALLENGE_VALIDATOR)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check"""



        try:
            health_status = {
                "system_healthy": True,
                "services": {},
                "overall_status": "healthy",
                "uptime_seconds": 0.0,
                "last_check": datetime.now(timezone.utc).isoformat()
            }
            
            if self._startup_time:
                uptime = (datetime.now() - self._startup_time).total_seconds()
                health_status["uptime_seconds"] = uptime
            
            unhealthy_services = 0
            
            # Check each service
            for service_type, service in self._services.items():
                try:
                    service_health = await self._check_service_health(service_type, service)
                    health_status["services"][service_type.value] = service_health
                    
                    if service_health["status"] != "healthy":
                        unhealthy_services += 1
                
                except Exception as e:
                    health_status["services"][service_type.value] = {
                        "status": "unhealthy",
                        "error": str(e)
                    }
                    unhealthy_services += 1
            
            # Determine overall status
            total_services = len(self._services)
            if unhealthy_services == 0:
                health_status["overall_status"] = "healthy"
            elif unhealthy_services < total_services * 0.5:
                health_status["overall_status"] = "degraded"
                health_status["system_healthy"] = False
            else:
                health_status["overall_status"] = "unhealthy"
                health_status["system_healthy"] = False
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {str(e)}")
            return {
                "system_healthy": False,
                "overall_status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_service_health(self, service_type: ServiceType, service: Any) -> Dict[str, Any]:
        """Check individual service health"""



        try:
            # Basic availability check
            if not service:
                return {"status": "unhealthy", "reason": "Service not available"}
            
            # Service-specific health checks
            if hasattr(service, 'health_check'):
                health_result = await service.health_check()
                return {
                    "status": "healthy" if health_result.get("healthy", False) else "unhealthy",
                    "details": health_result
                }
            
            # Default health check based on metrics
            metrics = self._service_metrics.get(service_type)
            if metrics:
                if metrics.error_rate > 50:  # More than 50% error rate
                    return {"status": "unhealthy", "reason": "High error rate"}
                elif metrics.error_rate > 20:  # More than 20% error rate
                    return {"status": "degraded", "reason": "Elevated error rate"}
            
            return {"status": "healthy"}
            
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get comprehensive system metrics"""



        try:
            metrics = {
                "system_uptime_seconds": 0.0,
                "total_services": len(self._services),
                "healthy_services": 0,
                "degraded_services": 0,
                "unhealthy_services": 0,
                "service_metrics": {},
                "aggregate_metrics": {
                    "total_requests": 0,
                    "total_successes": 0,
                    "total_failures": 0,
                    "average_response_time": 0.0,
                    "system_error_rate": 0.0
                },
                "resource_usage": {
                    "total_memory_mb": 0.0,
                    "average_cpu_percent": 0.0
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
            if self._startup_time:
                uptime = (datetime.now() - self._startup_time).total_seconds()
                metrics["system_uptime_seconds"] = uptime
            
            # Aggregate service metrics
            total_requests = 0
            total_successes = 0
            total_failures = 0
            total_response_time = 0.0
            total_memory = 0.0
            total_cpu = 0.0
            
            for service_type, service_metrics in self._service_metrics.items():
                # Count service status
                if service_metrics.status == ServiceStatus.HEALTHY:
                    metrics["healthy_services"] += 1
                elif service_metrics.status == ServiceStatus.DEGRADED:
                    metrics["degraded_services"] += 1
                else:
                    metrics["unhealthy_services"] += 1
                
                # Aggregate metrics
                total_requests += service_metrics.requests_total
                total_successes += service_metrics.requests_success
                total_failures += service_metrics.requests_failed
                total_response_time += service_metrics.average_response_time
                total_memory += service_metrics.memory_usage_mb
                total_cpu += service_metrics.cpu_usage_percent
                
                # Individual service metrics
                metrics["service_metrics"][service_type.value] = {
                    "status": service_metrics.status.value,
                    "uptime_seconds": service_metrics.uptime_seconds,
                    "requests_total": service_metrics.requests_total,
                    "requests_success": service_metrics.requests_success,
                    "requests_failed": service_metrics.requests_failed,
                    "error_rate": service_metrics.error_rate,
                    "average_response_time": service_metrics.average_response_time,
                    "memory_usage_mb": service_metrics.memory_usage_mb,
                    "cpu_usage_percent": service_metrics.cpu_usage_percent,
                    "throughput_per_minute": service_metrics.throughput_per_minute
                }
            
            # Calculate aggregates
            service_count = len(self._service_metrics)
            if service_count > 0:
                metrics["aggregate_metrics"] = {
                    "total_requests": total_requests,
                    "total_successes": total_successes,
                    "total_failures": total_failures,
                    "average_response_time": total_response_time / service_count,
                    "system_error_rate": (total_failures / total_requests * 100) if total_requests > 0 else 0.0
                }
                
                metrics["resource_usage"] = {
                    "total_memory_mb": total_memory,
                    "average_cpu_percent": total_cpu / service_count
                }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get system metrics: {str(e)}")
            return {"error": str(e)}
    
    async def _start_monitoring(self):
        """Start background monitoring tasks"""



        try:
            while self._system_started:
                # Update service metrics
                await self._update_service_metrics()
                
                # Perform health checks
                await self._periodic_health_checks()
                
                # Sleep for monitoring interval
                await asyncio.sleep(30)  # Check every 30 seconds
                
        except Exception as e:
            self.logger.error(f"Monitoring task error: {str(e)}")
    
    async def _update_service_metrics(self):
        """Update service metrics"""



        try:
            for service_type, service in self._services.items():
                metrics = self._service_metrics.get(service_type)
                if metrics:
                    # Update uptime
                    if self._startup_time:
                        metrics.uptime_seconds = (datetime.now() - self._startup_time).total_seconds()
                    
                    # Update last health check
                    metrics.last_health_check = datetime.now(timezone.utc)
                    
                    # Calculate error rate
                    if metrics.requests_total > 0:
                        metrics.error_rate = (metrics.requests_failed / metrics.requests_total) * 100
                    
                    # Calculate throughput
                    if metrics.uptime_seconds > 0:
                        metrics.throughput_per_minute = (metrics.requests_total / metrics.uptime_seconds) * 60
        
        except Exception as e:
            self.logger.error(f"Failed to update service metrics: {str(e)}")
    
    async def _periodic_health_checks(self):
        """Perform periodic health checks"""



        try:
            for service_type, service in self._services.items():
                config = self._service_configs.get(service_type)
                if not config:
                    continue
                
                # Check if health check is due
                metrics = self._service_metrics.get(service_type)
                if metrics:
                    time_since_check = (datetime.now(timezone.utc) - metrics.last_health_check).total_seconds()
                    
                    if time_since_check >= config.health_check_interval:
                        health_result = await self._check_service_health(service_type, service)
                        
                        # Update service status
                        if health_result["status"] == "healthy":
                            metrics.status = ServiceStatus.HEALTHY
                        elif health_result["status"] == "degraded":
                            metrics.status = ServiceStatus.DEGRADED
                        else:
                            metrics.status = ServiceStatus.UNHEALTHY
        
        except Exception as e:
            self.logger.error(f"Periodic health check error: {str(e)}")
    
    async def shutdown_system(self) -> Dict[str, Any]:
        """Gracefully shutdown the challenge system"""



        try:
            self.logger.info("Shutting down Challenge System...")
            
            shutdown_results = {
                "success": True,
                "services_stopped": [],
                "services_failed": [],
                "shutdown_time_seconds": 0.0
            }
            
            start_time = datetime.now()
            
            # Stop monitoring
            self._system_started = False
            
            # Shutdown services in reverse order
            for service_type in reversed(self._startup_order):
                if service_type in self._services:
                    try:
                        service = self._services[service_type]
                        
                        # Call shutdown method if available
                        if hasattr(service, 'shutdown'):
                            await service.shutdown()
                        
                        # Remove from registry
                        del self._services[service_type]
                        del self._service_metrics[service_type]
                        
                        shutdown_results["services_stopped"].append(service_type.value)
                        
                    except Exception as e:
                        self.logger.error(f"Failed to stop service {service_type.value}: {str(e)}")
                        shutdown_results["services_failed"].append({
                            "service": service_type.value,
                            "error": str(e)
                        })
            
            # Calculate shutdown time
            shutdown_time = (datetime.now() - start_time).total_seconds()
            shutdown_results["shutdown_time_seconds"] = shutdown_time
            
            # Determine overall success
            if shutdown_results["services_failed"]:
                shutdown_results["success"] = False
            
            self.logger.info(f"Challenge System shutdown completed in {shutdown_time:.2f} seconds")
            
            return shutdown_results
            
        except Exception as e:
            self.logger.error(f"Challenge System shutdown failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @asynccontextmanager
    async def system_context(self):
        """Context manager for system lifecycle"""



        try:
            # Start system
            startup_result = await self.start_system()
            if not startup_result["success"]:
                raise Exception(f"System startup failed: {startup_result}")
            
            yield self
            
        finally:
            # Shutdown system
            await self.shutdown_system()

class ChallengeServiceFactory:
    """Factory for creating challenge system services with proper configuration"""
    
    @staticmethod
    def create_challenge_engine(**dependencies) -> ChallengeEngine:
        """Create configured challenge engine"""



        return ChallengeEngine(**dependencies)
    
    @staticmethod
    def create_competition_manager(**dependencies) -> CompetitionManager:
        """Create configured competition manager"""



        return CompetitionManager(**dependencies)
    
    @staticmethod
    def create_scoring_system(**dependencies) -> ScoringSystem:
        """Create configured scoring system"""



        return ScoringSystem(**dependencies)
    
    @staticmethod
    def create_challenge_validator(**dependencies) -> ChallengeValidator:
        """Create configured challenge validator"""



        return ChallengeValidator(**dependencies)
    
    @staticmethod
    def create_complete_system(**dependencies) -> ChallengeSystemRegistry:
        """Create complete challenge system registry"""



        return ChallengeSystemRegistry(**dependencies)

# Factory functions for easy service creation

def create_challenge_system(**dependencies) -> ChallengeSystemRegistry:
    """Factory function to create configured challenge system"""



    return ChallengeSystemRegistry(**dependencies)

def create_challenge_engine(**dependencies) -> ChallengeEngine:
    """Factory function to create challenge engine"""



    return ChallengeServiceFactory.create_challenge_engine(**dependencies)

def create_competition_manager(**dependencies) -> CompetitionManager:
    """Factory function to create competition manager"""



    return ChallengeServiceFactory.create_competition_manager(**dependencies)

def create_scoring_system(**dependencies) -> ScoringSystem:
    """Factory function to create scoring system"""



    return ChallengeServiceFactory.create_scoring_system(**dependencies)

def create_challenge_validator(**dependencies) -> ChallengeValidator:
    """Factory function to create challenge validator"""



    return ChallengeServiceFactory.create_challenge_validator(**dependencies)

# Default system instance (singleton pattern)
_default_system: Optional[ChallengeSystemRegistry] = None

def get_default_challenge_system() -> Optional[ChallengeSystemRegistry]:
    """Get default challenge system instance"""



    return _default_system

def set_default_challenge_system(system: ChallengeSystemRegistry):
    """Set default challenge system instance"""
    global _default_system
    _default_system = system

async def initialize_default_system(**dependencies) -> ChallengeSystemRegistry:
    """Initialize default challenge system with dependencies"""
    global _default_system
    
    if _default_system is None:
        _default_system = create_challenge_system(**dependencies)
        startup_result = await _default_system.start_system()
        
        if not startup_result["success"]:
            raise Exception(f"Default system initialization failed: {startup_result}")
    
    return _default_system

# Convenience functions using default system

async def get_challenge_engine() -> Optional[ChallengeEngine]:
    """Get challenge engine from default system"""
    system = get_default_challenge_system()
    return system.get_challenge_engine() if system else None

async def get_competition_manager() -> Optional[CompetitionManager]:
    """Get competition manager from default system"""
    system = get_default_challenge_system()
    return system.get_competition_manager() if system else None

async def get_scoring_system() -> Optional[ScoringSystem]:
    """Get scoring system from default system"""
    system = get_default_challenge_system()
    return system.get_scoring_system() if system else None

async def get_challenge_validator() -> Optional[ChallengeValidator]:
    """Get challenge validator from default system"""
    system = get_default_challenge_system()
    return system.get_challenge_validator() if system else None

# Health and monitoring convenience functions

async def system_health_check() -> Dict[str, Any]:
    """Perform system health check using default system"""
    system = get_default_challenge_system()
    if system:
        return await system.health_check()
    return {"system_healthy": False, "error": "No default system available"}

async def system_metrics() -> Dict[str, Any]:
    """Get system metrics using default system"""
    system = get_default_challenge_system()
    if system:
        return await system.get_system_metrics()
    return {"error": "No default system available"}

# Example usage and configuration helpers

def get_production_config() -> Dict[str, Any]:
    """Get production-ready configuration"""



    return {
        "health_check_intervals": {
            "challenge_engine": 60,
            "competition_manager": 30,
            "scoring_system": 45,
            "challenge_validator": 120
        },
        "cache_settings": {
            "enabled": True,
            "default_ttl": 300,
            "leaderboard_ttl": 120
        },
        "performance_monitoring": True,
        "retry_attempts": 3,
        "timeout_seconds": 30
    }

def get_development_config() -> Dict[str, Any]:
    """Get development configuration"""



    return {
        "health_check_intervals": {
            "challenge_engine": 300,
            "competition_manager": 300,
            "scoring_system": 300,
            "challenge_validator": 600
        },
        "cache_settings": {
            "enabled": False,
            "default_ttl": 60
        },
        "performance_monitoring": False,
        "retry_attempts": 1,
        "timeout_seconds": 60
    }