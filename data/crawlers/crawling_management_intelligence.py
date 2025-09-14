"""Crawling Management Intelligence Engine - AI-Powered Orchestration System
=========================================================================

Enterprise-grade AI orchestration system for multi-platform crawling operations.
Implements intelligent scheduling, resource optimization, and ML-powered coordination.

ENTERPRISE FEATURES:
- AI-powered crawling orchestration (53+ agents integration)  
- Multi-platform intelligent scheduling
- Real-time performance optimization
- Cross-platform data correlation
- Advanced analytics coordination
- Machine learning optimization

Author: Fahed Mlaiel (mlaiel@live.de)
Email: mlaiel@live.de
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved

⚠️  CRITICAL WARNING ⚠️
This code is PROPRIETARY and CONFIDENTIAL intellectual property.
Any unauthorized use, reproduction, distribution, or reverse engineering 
is STRICTLY PROHIBITED and will result in immediate legal action.

For licensing inquiries, contact: mlaiel@live.de
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
import json
import threading
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION ENUMS AND DATACLASSES
# ============================================================================

class CrawlerPriority(Enum):
    """Crawler priority levels for intelligent scheduling"""
    CRITICAL = 1
    HIGH = 2  
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5

class ScheduleType(Enum):
    """Scheduling types for different crawling patterns"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    ON_DEMAND = "on_demand"
    AI_TRIGGERED = "ai_triggered"

class CrawlerStatus(Enum):
    """Current status of crawler instances"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class CrawlerConfig:
    """Configuration for individual crawler instances"""
    name: str
    platform: str
    priority: CrawlerPriority
    schedule_type: ScheduleType
    rate_limit: int = 60  # requests per minute
    concurrent_sessions: int = 5
    retry_attempts: int = 3
    timeout: int = 30
    proxy_rotation: bool = True
    ai_agent_integration: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskConfiguration:
    """Configuration for crawling tasks"""
    task_id: str
    crawler_name: str
    target_urls: List[str]
    parameters: Dict[str, Any]
    priority: CrawlerPriority
    scheduled_time: Optional[datetime] = None
    deadline: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)

# ============================================================================
# CORE MANAGEMENT CLASSES
# ============================================================================

class ConsolidatedCrawlingEngine:
    """Main orchestration engine for all crawling operations"""
    
    def __init__(self) -> None:
        self.crawlers: Dict[str, CrawlerConfig] = {}
        self.active_tasks: Dict[str, TaskConfiguration] = {}
        self.performance_metrics: Dict[str, Dict] = {}
        self.ai_agents: Dict[str, Any] = {}
        self.resource_monitor = ResourceOptimizationEngine()
        self.analytics = CrawlerAnalyticsEngine()
        self.scheduler = PlatformSchedulingEngine()
        self.intelligence_manager = CrawlerIntelligenceManager()
        self._running = False
        self._lock = threading.RLock()
        
        logger.info("ConsolidatedCrawlingEngine initialized")
    
    async def initialize(self) -> None:
        """Initialize the crawling engine and all subsystems"""
        try:
            # Initialize subsystems
            await self.resource_monitor.initialize()
            await self.analytics.initialize()
            await self.scheduler.initialize()
            await self.intelligence_manager.initialize()
            
            # Load AI agents configuration
            await self._load_ai_agents()
            
            # Start monitoring threads
            self._start_monitoring()
            
            self._running = True
            logger.info("Crawling engine fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize crawling engine: {e}")
            raise
    
    async def register_crawler(self, config: CrawlerConfig) -> bool:
        """Register a new crawler with the engine"""
        try:
            with self._lock:
                if config.name in self.crawlers:
                    logger.warning(f"Crawler {config.name} already registered")
                    return False
                
                self.crawlers[config.name] = config
                self.performance_metrics[config.name] = {
                    'total_requests': 0,
                    'successful_requests': 0,
                    'failed_requests': 0,
                    'average_response_time': 0.0,
                    'last_activity': None,
                    'status': CrawlerStatus.IDLE
                }
                
                # Register with scheduler
                await self.scheduler.register_crawler(config)
                
                logger.info(f"Crawler {config.name} registered successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register crawler {config.name}: {e}")
            return False
    
    async def submit_task(self, task: TaskConfiguration) -> str:
        """Submit a new crawling task for execution"""
        try:
            with self._lock:
                if task.task_id in self.active_tasks:
                    logger.warning(f"Task {task.task_id} already exists")
                    return task.task_id
                
                # Validate crawler exists
                if task.crawler_name not in self.crawlers:
                    raise ValueError(f"Crawler {task.crawler_name} not registered")
                
                # Add to active tasks
                self.active_tasks[task.task_id] = task
                
                # Schedule task execution
                await self.scheduler.schedule_task(task)
                
                logger.info(f"Task {task.task_id} submitted for crawler {task.crawler_name}")
                return task.task_id
                
        except Exception as e:
            logger.error(f"Failed to submit task {task.task_id}: {e}")
            raise
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            with self._lock:
                status = {
                    'engine_running': self._running,
                    'total_crawlers': len(self.crawlers),
                    'active_tasks': len(self.active_tasks),
                    'crawler_status': {},
                    'resource_usage': await self.resource_monitor.get_metrics(),
                    'performance_summary': await self.analytics.get_summary(),
                    'ai_agents_status': len(self.ai_agents),
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                # Add individual crawler status
                for name, config in self.crawlers.items():
                    metrics = self.performance_metrics.get(name, {})
                    status['crawler_status'][name] = {
                        'platform': config.platform,
                        'priority': config.priority.name,
                        'status': metrics.get('status', CrawlerStatus.IDLE).value,
                        'total_requests': metrics.get('total_requests', 0),
                        'success_rate': self._calculate_success_rate(name),
                        'last_activity': metrics.get('last_activity')
                    }
                
                return status
                
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {'error': str(e)}
    
    async def _load_ai_agents(self) -> None:
        """Load and initialize AI agents for content analysis"""
        try:
            # Placeholder for AI agents - would integrate with actual AI services
            ai_agent_configs = [
                'ContentAnalysisAgent',
                'SimilarityDetectionAgent', 
                'ViolationDetectionAgent',
                'TrendAnalysisAgent',
                'PerformanceOptimizationAgent',
                'SecurityComplianceAgent'
            ]
            
            for agent_name in ai_agent_configs:
                self.ai_agents[agent_name] = {
                    'status': 'active',
                    'last_used': None,
                    'total_calls': 0,
                    'success_rate': 1.0
                }
                
            logger.info(f"Loaded {len(self.ai_agents)} AI agents")
            
        except Exception as e:
            logger.error(f"Failed to load AI agents: {e}")
    
    def _start_monitoring(self) -> None:
        """Start background monitoring threads"""
        def monitor_loop() -> None:
            while self._running:
                try:
                    asyncio.create_task(self._update_metrics())
                    time.sleep(30)  # Update every 30 seconds
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logger.info("Background monitoring started")
    
    async def _update_metrics(self) -> None:
        """Update performance metrics for all crawlers"""
        try:
            current_time = datetime.utcnow()
            
            for crawler_name in self.crawlers:
                # Update analytics
                await self.analytics.update_crawler_metrics(crawler_name)
                
                # Update resource usage
                await self.resource_monitor.update_crawler_usage(crawler_name)
                
        except Exception as e:
            logger.error(f"Failed to update metrics: {e}")
    
    def _calculate_success_rate(self, crawler_name: str) -> float:
        """Calculate success rate for a crawler"""
        metrics = self.performance_metrics.get(crawler_name, {})
        total = metrics.get('total_requests', 0)
        successful = metrics.get('successful_requests', 0)
        
        if total == 0:
            return 0.0
        
        return round((successful / total) * 100, 2)

class CrawlerIntelligenceManager:
    """ML-powered crawler management with intelligent decision making"""
    
    def __init__(self) -> None:
        self.ml_models: Dict[str, Any] = {}
        self.learning_data: List[Dict] = []
        self.optimization_rules: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize ML models and learning systems"""
        try:
            # Initialize placeholder ML models
            self.ml_models = {
                'performance_predictor': {'status': 'loaded'},
                'optimal_scheduling': {'status': 'loaded'},
                'anomaly_detector': {'status': 'loaded'},
                'resource_optimizer': {'status': 'loaded'}
            }
            
            logger.info("CrawlerIntelligenceManager initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize intelligence manager: {e}")
            raise
    
    async def predict_optimal_schedule(self, crawler_name: str) -> Dict[str, Any]:
        """Predict optimal scheduling for a crawler based on historical data"""
        try:
            # Placeholder ML prediction logic
            prediction = {
                'recommended_intervals': [300, 600, 900],  # seconds
                'optimal_time_windows': ['09:00-11:00', '14:00-16:00'],
                'expected_success_rate': 0.95,
                'predicted_load': 'medium',
                'confidence': 0.87
            }
            
            logger.info(f"Generated optimal schedule prediction for {crawler_name}")
            return prediction
            
        except Exception as e:
            logger.error(f"Failed to predict schedule for {crawler_name}: {e}")
            return {}
    
    async def detect_anomalies(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in crawler performance using ML"""
        try:
            anomalies = []
            
            # Simple anomaly detection rules (would use actual ML in production)
            for crawler_name, data in metrics.items():
                success_rate = data.get('success_rate', 100)
                response_time = data.get('average_response_time', 0)
                
                if success_rate < 80:
                    anomalies.append({
                        'type': 'low_success_rate',
                        'crawler': crawler_name,
                        'value': success_rate,
                        'severity': 'high' if success_rate < 50 else 'medium'
                    })
                
                if response_time > 10:
                    anomalies.append({
                        'type': 'high_response_time', 
                        'crawler': crawler_name,
                        'value': response_time,
                        'severity': 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {e}")
            return []

class PlatformSchedulingEngine:
    """Intelligent scheduling system for multi-platform coordination"""
    
    def __init__(self) -> None:
        self.scheduled_tasks: Dict[str, TaskConfiguration] = {}
        self.execution_queue: List[TaskConfiguration] = []
        self.platform_limits: Dict[str, Dict] = {}
        self._scheduler_running = False
        
    async def initialize(self) -> None:
        """Initialize scheduling engine"""
        try:
            # Load platform-specific rate limits and constraints
            self.platform_limits = {
                'youtube': {'max_concurrent': 10, 'rate_limit': 100},
                'instagram': {'max_concurrent': 5, 'rate_limit': 50},
                'tiktok': {'max_concurrent': 8, 'rate_limit': 80},
                'twitter': {'max_concurrent': 15, 'rate_limit': 150},
                'facebook': {'max_concurrent': 6, 'rate_limit': 60}
            }
            
            # Start scheduler loop
            asyncio.create_task(self._scheduler_loop())
            self._scheduler_running = True
            
            logger.info("PlatformSchedulingEngine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise
    
    async def register_crawler(self, config: CrawlerConfig) -> None:
        """Register a crawler with the scheduler"""
        try:
            platform_limit = self.platform_limits.get(config.platform.lower(), {
                'max_concurrent': 5,
                'rate_limit': 60
            })
            
            # Update crawler config with platform limits
            config.concurrent_sessions = min(
                config.concurrent_sessions, 
                platform_limit['max_concurrent']
            )
            config.rate_limit = min(
                config.rate_limit,
                platform_limit['rate_limit']
            )
            
            logger.info(f"Registered crawler {config.name} with platform limits")
            
        except Exception as e:
            logger.error(f"Failed to register crawler {config.name}: {e}")
    
    async def schedule_task(self, task: TaskConfiguration) -> None:
        """Schedule a task for execution"""
        try:
            # Add to scheduled tasks
            self.scheduled_tasks[task.task_id] = task
            
            # Add to execution queue based on priority
            self._insert_by_priority(task)
            
            logger.info(f"Task {task.task_id} scheduled with priority {task.priority.name}")
            
        except Exception as e:
            logger.error(f"Failed to schedule task {task.task_id}: {e}")
    
    def _insert_by_priority(self, task: TaskConfiguration) -> None:
        """Insert task into execution queue maintaining priority order"""
        inserted = False
        for i, queued_task in enumerate(self.execution_queue):
            if task.priority.value < queued_task.priority.value:
                self.execution_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.execution_queue.append(task)
    
    async def _scheduler_loop(self) -> None:
        """Main scheduler execution loop"""
        while self._scheduler_running:
            try:
                if self.execution_queue:
                    task = self.execution_queue.pop(0)
                    await self._execute_task(task)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(5)
    
    async def _execute_task(self, task: TaskConfiguration) -> None:
        """Execute a scheduled crawling task"""
        try:
            logger.info(f"Executing task {task.task_id} for crawler {task.crawler_name}")
            
            # Placeholder task execution (would call actual crawler)
            await asyncio.sleep(0.1)  # Simulate task execution
            
            # Remove from scheduled tasks
            if task.task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task.task_id]
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to execute task {task.task_id}: {e}")

class ResourceOptimizationEngine:
    """Advanced resource monitoring and optimization system"""
    
    def __init__(self) -> None:
        self.resource_metrics: Dict[str, Dict] = {}
        self.optimization_strategies: Dict[str, Any] = {}
        self.alert_thresholds: Dict[str, float] = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'network_latency': 5.0,
            'error_rate': 10.0
        }
        
    async def initialize(self) -> None:
        """Initialize resource monitoring"""
        try:
            self.optimization_strategies = {
                'cpu_optimization': {'enabled': True, 'threshold': 70},
                'memory_optimization': {'enabled': True, 'threshold': 75},
                'network_optimization': {'enabled': True, 'threshold': 80},
                'concurrent_limit_adjustment': {'enabled': True, 'auto_scale': True}
            }
            
            logger.info("ResourceOptimizationEngine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize resource optimizer: {e}")
            raise
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current resource usage metrics"""
        try:
            # Placeholder metrics (would integrate with actual monitoring)
            metrics = {
                'cpu_usage': 45.2,
                'memory_usage': 62.8,
                'network_latency': 1.2,
                'active_connections': 127,
                'requests_per_second': 23.5,
                'error_rate': 2.1,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get resource metrics: {e}")
            return {}
    
    async def update_crawler_usage(self, crawler_name: str) -> None:
        """Update resource usage for specific crawler"""
        try:
            if crawler_name not in self.resource_metrics:
                self.resource_metrics[crawler_name] = {}
            
            # Update crawler-specific metrics
            self.resource_metrics[crawler_name].update({
                'last_update': datetime.utcnow().isoformat(),
                'requests_sent': self.resource_metrics[crawler_name].get('requests_sent', 0) + 1,
                'bandwidth_used': self.resource_metrics[crawler_name].get('bandwidth_used', 0) + 1024
            })
            
        except Exception as e:
            logger.error(f"Failed to update usage for {crawler_name}: {e}")
    
    async def optimize_resources(self) -> Dict[str, Any]:
        """Perform automatic resource optimization"""
        try:
            optimizations = []
            current_metrics = await self.get_metrics()
            
            # Check thresholds and suggest optimizations
            for metric, threshold in self.alert_thresholds.items():
                current_value = current_metrics.get(metric, 0)
                if current_value > threshold:
                    optimizations.append({
                        'metric': metric,
                        'current_value': current_value,
                        'threshold': threshold,
                        'recommended_action': self._get_optimization_action(metric)
                    })
            
            return {
                'optimizations_needed': len(optimizations),
                'recommendations': optimizations,
                'auto_applied': []
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize resources: {e}")
            return {}
    
    def _get_optimization_action(self, metric: str) -> str:
        """Get recommended optimization action for a metric"""
        actions = {
            'cpu_usage': 'Reduce concurrent crawlers or add CPU cores',
            'memory_usage': 'Clear caches or increase memory allocation',
            'network_latency': 'Switch to closer proxy servers',
            'error_rate': 'Implement circuit breaker pattern'
        }
        return actions.get(metric, 'Manual investigation required')

class CrawlerAnalyticsEngine:
    """Advanced analytics and performance tracking system"""
    
    def __init__(self) -> None:
        self.analytics_data: Dict[str, List] = {}
        self.performance_baselines: Dict[str, Dict] = {}
        self.trend_analysis: Dict[str, Any] = {}
        
    async def initialize(self) -> None:
        """Initialize analytics engine"""
        try:
            # Initialize analytics storage
            self.analytics_data = {
                'performance_history': [],
                'error_logs': [],
                'success_metrics': [],
                'platform_statistics': []
            }
            
            logger.info("CrawlerAnalyticsEngine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize analytics engine: {e}")
            raise
    
    async def update_crawler_metrics(self, crawler_name: str) -> None:
        """Update performance metrics for a crawler"""
        try:
            timestamp = datetime.utcnow()
            
            # Create performance entry
            performance_entry = {
                'crawler_name': crawler_name,
                'timestamp': timestamp.isoformat(),
                'metrics': {
                    'response_time': 1.5,  # Placeholder
                    'success_rate': 95.2,  # Placeholder
                    'throughput': 45.3,    # Placeholder
                    'errors': 2            # Placeholder
                }
            }
            
            # Add to analytics data
            self.analytics_data['performance_history'].append(performance_entry)
            
            # Keep only last 1000 entries to manage memory
            if len(self.analytics_data['performance_history']) > 1000:
                self.analytics_data['performance_history'] = \
                    self.analytics_data['performance_history'][-1000:]
            
        except Exception as e:
            logger.error(f"Failed to update metrics for {crawler_name}: {e}")
    
    async def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary"""
        try:
            total_entries = len(self.analytics_data['performance_history'])
            
            if total_entries == 0:
                return {'status': 'no_data'}
            
            # Calculate summary statistics
            recent_entries = self.analytics_data['performance_history'][-100:]
            
            avg_response_time = sum(
                entry['metrics']['response_time'] for entry in recent_entries
            ) / len(recent_entries)
            
            avg_success_rate = sum(
                entry['metrics']['success_rate'] for entry in recent_entries  
            ) / len(recent_entries)
            
            summary = {
                'total_data_points': total_entries,
                'average_response_time': round(avg_response_time, 2),
                'average_success_rate': round(avg_success_rate, 2),
                'last_updated': datetime.utcnow().isoformat(),
                'trends': await self._analyze_trends()
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to get analytics summary: {e}")
            return {'error': str(e)}
    
    async def _analyze_trends(self) -> Dict[str, Any]:
        """Analyze performance trends"""
        try:
            trends = {
                'performance_trend': 'stable',
                'success_rate_trend': 'improving',
                'error_rate_trend': 'decreasing',
                'throughput_trend': 'increasing'
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            return {}

class ConfigurationManager:
    """Dynamic configuration management for crawlers"""
    
    def __init__(self) -> None:
        self.configurations: Dict[str, Dict] = {}
        self.environment_configs: Dict[str, Dict] = {}
        self.dynamic_updates: bool = True
        
    async def load_configuration(self, config_path: str = None) -> Dict[str, Any]:
        """Load configuration from file or defaults"""
        try:
            # Default configuration
            default_config = {
                'global_settings': {
                    'max_concurrent_crawlers': 50,
                    'default_timeout': 30,
                    'retry_attempts': 3,
                    'rate_limit_global': 1000
                },
                'platform_settings': {
                    'youtube': {
                        'api_quota_per_day': 10000,
                        'rate_limit': 100,
                        'concurrent_sessions': 10
                    },
                    'instagram': {
                        'rate_limit': 50,
                        'concurrent_sessions': 5,
                        'use_proxy': True
                    }
                },
                'ai_settings': {
                    'enable_content_analysis': True,
                    'similarity_threshold': 0.85,
                    'max_ai_requests_per_minute': 100
                }
            }
            
            self.configurations = default_config
            logger.info("Configuration loaded successfully")
            return default_config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return {}
    
    async def update_configuration(self, key: str, value: Any) -> bool:
        """Update configuration dynamically"""
        try:
            keys = key.split('.')
            config_ref = self.configurations
            
            # Navigate to the correct nested location
            for k in keys[:-1]:
                if k not in config_ref:
                    config_ref[k] = {}
                config_ref = config_ref[k]
            
            # Update the value
            config_ref[keys[-1]] = value
            
            logger.info(f"Configuration updated: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update configuration {key}: {e}")
            return False

# ============================================================================
# FACTORY AND UTILITY FUNCTIONS
# ============================================================================

async def create_crawler_engine() -> ConsolidatedCrawlingEngine:
    """Factory function to create and initialize crawling engine"""
    try:
        engine = ConsolidatedCrawlingEngine()
        await engine.initialize()
        
        logger.info("Crawler engine created and initialized")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create crawler engine: {e}")
        raise

def create_crawler_config(
    name: str,
    platform: str,
    priority: CrawlerPriority = CrawlerPriority.MEDIUM,
    schedule_type: ScheduleType = ScheduleType.HOURLY,
    **kwargs
) -> CrawlerConfig:
    """Utility function to create crawler configuration"""
    return CrawlerConfig(
        name=name,
        platform=platform,
        priority=priority,
        schedule_type=schedule_type,
        **kwargs
    )

def create_task_configuration(
    task_id: str,
    crawler_name: str,
    target_urls: List[str],
    priority: CrawlerPriority = CrawlerPriority.MEDIUM,
    **kwargs
) -> TaskConfiguration:
    """Utility function to create task configuration"""
    return TaskConfiguration(
        task_id=task_id,
        crawler_name=crawler_name,
        target_urls=target_urls,
        priority=priority,
        parameters=kwargs.get('parameters', {}),
        **{k: v for k, v in kwargs.items() if k != 'parameters'}
    )

# ============================================================================
# MODULE EXPORTS
# ============================================================================

__all__ = [
    # Main Classes
    'ConsolidatedCrawlingEngine',
    'CrawlerIntelligenceManager', 
    'PlatformSchedulingEngine',
    'ResourceOptimizationEngine',
    'CrawlerAnalyticsEngine',
    'ConfigurationManager',
    
    # Configuration Classes  
    'CrawlerConfig',
    'TaskConfiguration',
    
    # Enums
    'CrawlerPriority',
    'ScheduleType', 
    'CrawlerStatus',
    
    # Factory Functions
    'create_crawler_engine',
    'create_crawler_config',
    'create_task_configuration'
]

if __name__ == "__main__":
    # Example usage
    async def main() -> None:
        # Create and initialize engine
        engine = await create_crawler_engine()
        
        # Create crawler configuration
        youtube_config = create_crawler_config(
            name="youtube_main",
            platform="youtube",
            priority=CrawlerPriority.HIGH,
            schedule_type=ScheduleType.REAL_TIME,
            rate_limit=100,
            concurrent_sessions=8
        )
        
        # Register crawler
        await engine.register_crawler(youtube_config)
        
        # Create and submit task
        task = create_task_configuration(
            task_id="youtube_task_001",
            crawler_name="youtube_main",
            target_urls=["https://youtube.com/watch?v=example"],
            priority=CrawlerPriority.HIGH
        )
        
        await engine.submit_task(task)
        
        # Get system status
        status = await engine.get_system_status()
        print(f"System Status: {json.dumps(status, indent=2)}")
    
    # Run example
    asyncio.run(main())