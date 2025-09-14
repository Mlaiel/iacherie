"""
Index module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""IA Influencer Agent - Logging Module Entry Point
import json
from datetime import datetime

Enterprise logging infrastructure - Main entry point

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited

WARNING: This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit 
written permission is strictly prohibited and will result in legal action.
Contact: mlaiel@live.de for licensing inquiries.

Team Expertise:
- Lead Developer & AI Architect: Fahed Mlaiel
- Backend Senior Engineer: Advanced Python/FastAPI
- ML Engineer: AI/ML Algorithms & Analytics
- DevOps Engineer: Infrastructure & Deployment
- Database Administrator: Performance & Optimization
- Security Specialist: Enterprise Security & Compliance
- Microservices Architect: Distributed Systems
- IA Prompt Engineer: Advanced AI Integration
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import all logging components
from . import (
    LogAggregator,
    LogEntry,
    LogLevel,
    LogFormat,
    ElasticsearchManager,
    ElasticsearchConfig,
    FluentdManager,
    FluentdConfig,
    LogRetentionManager,
    LogAnalyticsEngine,
    LogMonitoringService,
    NotificationChannel
)
from .config import DEFAULT_LOGGING_CONFIG


class IAInfluencerLoggingSystem:
    """
    Main entry point for IA Influencer Agent Logging System
    Enterprise-grade logging infrastructure with AI-powered analytics
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """
Initialize the complete logging system"""
        self.config = config or DEFAULT_LOGGING_CONFIG
        self.aggregator = None
        self.es_manager = None
        self.fluentd_manager = None
        self.retention_manager = None
        self.analytics_engine = None
        self.monitoring_service = None
        self._is_running = False
        
        # Setup basic logging
        self._setup_basic_logging()
    
    def _setup_basic_logging(self) -> None:
        """
Setup basic Python logging configuration"""
        logging.basicConfig(
            level=getattr(logging, self.config['environment']['log_level']),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Set third-party loggers to WARNING to reduce noise
        for logger_name in ['elasticsearch', 'urllib3', 'aiohttp', 'fluent']:
            logging.getLogger(logger_name).setLevel(logging.WARNING)
    
    async def initialize(self) -> bool:
        """
        Initialize all logging components
        Returns True if successful, False otherwise
        """
        try:
            logger = logging.getLogger(__name__)
            logger.info("Initializing IA Influencer Agent Logging System...")
            
            # 1. Initialize Log Aggregator
            logger.info("Setting up Log Aggregator...")
            self.aggregator = LogAggregator(self.config['aggregator'])
            await self.aggregator.start()
            logger.info("Log Aggregator initialized successfully")
            
            # 2. Initialize Elasticsearch Manager
            if self.config['elasticsearch']['hosts']:
                logger.info("Setting up Elasticsearch Manager...")
                es_config = ElasticsearchConfig(**self.config['elasticsearch'])
                self.es_manager = ElasticsearchManager(es_config)
                await self.es_manager.connect()
                logger.info("Elasticsearch Manager initialized successfully")
            
            # 3. Initialize Fluentd Manager
            if self.config['fluentd']['host']:
                logger.info("Setting up Fluentd Manager...")
                fluentd_config = FluentdConfig(**self.config['fluentd'])
                self.fluentd_manager = FluentdManager(fluentd_config)
                await self.fluentd_manager.start()
                logger.info("Fluentd Manager initialized successfully")
            
            # 4. Initialize Retention Manager
            logger.info("Setting up Log Retention Manager...")
            self.retention_manager = LogRetentionManager()
            await self.retention_manager.load_config()
            logger.info("Log Retention Manager initialized successfully")
            
            # 5. Initialize Analytics Engine (requires Elasticsearch)
            if self.es_manager:
                logger.info("Setting up Analytics Engine...")
                self.analytics_engine = LogAnalyticsEngine(self.es_manager)
                logger.info("Analytics Engine initialized successfully")
            
            # 6. Initialize Monitoring Service
            if self.analytics_engine:
                logger.info("Setting up Monitoring Service...")
                self.monitoring_service = LogMonitoringService(
                    self.analytics_engine,
                    redis_url=self.config['monitoring']['redis_url']
                )
                
                # Configure notification channels
                await self._configure_notifications()
                
                await self.monitoring_service.start()
                logger.info("Monitoring Service initialized successfully")
            
            self._is_running = True
            logger.info("IA Influencer Agent Logging System initialized successfully!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize logging system: {e}")
            await self.shutdown()
            return False
    
    async def _configure_notifications(self) -> None:
        """Configure notification channels for monitoring"""
        if not self.monitoring_service:
            return
        
        notifications_config = self.config['monitoring']['notifications']
        
        # Configure Email notifications
        if notifications_config['email']['enabled']:
            self.monitoring_service.configure_notification_channel(
                NotificationChannel.EMAIL,
                notifications_config['email']
            )
        
        # Configure Slack notifications
        if notifications_config['slack']['enabled']:
            self.monitoring_service.configure_notification_channel(
                NotificationChannel.SLACK,
                notifications_config['slack']
            )
        
        # Configure Webhook notifications
        if notifications_config['webhook']['enabled']:
            self.monitoring_service.configure_notification_channel(
                NotificationChannel.WEBHOOK,
                notifications_config['webhook']
            )
        
        # Configure Teams notifications
        if notifications_config['teams']['enabled']:
            self.monitoring_service.configure_notification_channel(
                NotificationChannel.TEAMS,
                notifications_config['teams']
            )
    
    async def create_service_logger(self, service_name -> None: str, module_name -> None: str = None) -> None:
        """
Create a service-specific logger"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        return self.aggregator.create_service_logger(service_name, module_name)
    
    async def log_ai_processing(self, 
                               message -> None: str,
                               user_id -> None: str = None,
                               processing_type -> None: str = "general",
                               metadata -> None: Dict[str, Any] = None) -> None:
        """Log AI processing events with standardized format"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        enhanced_metadata = {
            "processing_type": processing_type,
            "ai_service": True,
            **(metadata or {})
        }
        
        await self.aggregator.log(
            level=LogLevel.INFO,
            message=message,
            service="ai_processing",
            module=processing_type,
            user_id=user_id,
            metadata=enhanced_metadata
        )
    
    async def log_fingerprinting(self,
                                message -> None: str,
                                user_id -> None: str = None,
                                content_type -> None: str = "audio",
                                algorithm -> None: str = "chromaprint",
                                metadata -> None: Dict[str, Any] = None) -> None:
        """Log fingerprinting events with standardized format"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        enhanced_metadata = {
            "content_type": content_type,
            "algorithm": algorithm,
            "service_type": "fingerprinting",
            **(metadata or {})
        }
        
        await self.aggregator.log(
            level=LogLevel.INFO,
            message=message,
            service="fingerprinting",
            module="content_processor",
            user_id=user_id,
            metadata=enhanced_metadata
        )
    
    async def log_revenue_processing(self,
                                   message -> None: str,
                                   user_id -> None: str = None,
                                   amount -> None: float = None,
                                   currency -> None: str = "EUR",
                                   metadata -> None: Dict[str, Any] = None) -> None:
        """Log revenue processing events with standardized format"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        enhanced_metadata = {
            "revenue_amount": amount,
            "currency": currency,
            "service_type": "monetization",
            **(metadata or {})
        }
        
        level = LogLevel.INFO
        if "error" in message.lower() or "failed" in message.lower():
            level = LogLevel.CRITICAL  # Revenue errors are critical
        
        await self.aggregator.log(
            level=level,
            message=message,
            service="monetization",
            module="revenue_processor",
            user_id=user_id,
            metadata=enhanced_metadata
        )
    
    async def log_user_activity(self,
                              message -> None: str,
                              user_id -> None: str,
                              activity_type -> None: str,
                              metadata -> None: Dict[str, Any] = None) -> None:
        """Log user activity events with standardized format"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        enhanced_metadata = {
            "activity_type": activity_type,
            "user_activity": True,
            **(metadata or {})
        }
        
        await self.aggregator.log(
            level=LogLevel.INFO,
            message=message,
            service="user_activity",
            module=activity_type,
            user_id=user_id,
            metadata=enhanced_metadata
        )
    
    async def log_security_event(self,
                               message -> None: str,
                               severity -> None: str = "medium",
                               event_type -> None: str = "general",
                               metadata -> None: Dict[str, Any] = None) -> None:
        """Log security events with standardized format"""
        if not self.aggregator:
            raise RuntimeError("Logging system not initialized")
        
        # Map severity to log level
        level_mapping = {
            "low": LogLevel.INFO,
            "medium": LogLevel.WARNING,
            "high": LogLevel.ERROR,
            "critical": LogLevel.CRITICAL
        }
        
        enhanced_metadata = {
            "security_event": True,
            "event_type": event_type,
            "severity": severity,
            **(metadata or {})
        }
        
        await self.aggregator.log(
            level=level_mapping.get(severity, LogLevel.WARNING),
            message=message,
            service="security",
            module="security_monitor",
            metadata=enhanced_metadata
        )
    
    async def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics and status"""
        if not self.analytics_engine:
            return {"error": "Analytics engine not available"}
        
        try:
            # Get basic metrics
            metrics = await self.analytics_engine.compute_metrics(hours_back=1)
            
            # Get active alerts
            alerts = await self.analytics_engine.check_alerts()
            
            # Get system status
            system_status = {
                "aggregator_running": self._is_running and self.aggregator is not None,
                "elasticsearch_connected": self.es_manager is not None,
                "fluentd_connected": self.fluentd_manager is not None,
                "monitoring_active": self.monitoring_service is not None,
                "analytics_enabled": self.analytics_engine is not None
            }
            
            return {
                "system_status": system_status,
                "metrics": [asdict(metric) for metric in metrics],
                "active_alerts": len(alerts),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def run_retention_check(self) -> Dict[str, Any]:
        """Run log retention policies manually"""
        if not self.retention_manager:
            return {"error": "Retention manager not available"}
        
        try:
            log_directory = self.config['aggregator']['file']['directory']
            results = await self.retention_manager.run_retention(log_directory)
            return results
        except Exception as e:
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform system health check"""
        health_status = {
            "overall_status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {}
        }
        
        # Check aggregator
        if self.aggregator:
            health_status["components"]["aggregator"] = "healthy"
        else:
            health_status["components"]["aggregator"] = "unavailable"
            health_status["overall_status"] = "degraded"
        
        # Check Elasticsearch
        if self.es_manager:
            try:
                # Simple connectivity test
                health_status["components"]["elasticsearch"] = "healthy"
            except:
                health_status["components"]["elasticsearch"] = "unhealthy"
                health_status["overall_status"] = "degraded"
        else:
            health_status["components"]["elasticsearch"] = "not_configured"
        
        # Check other components
        health_status["components"]["fluentd"] = "healthy" if self.fluentd_manager else "not_configured"
        health_status["components"]["retention"] = "healthy" if self.retention_manager else "unavailable"
        health_status["components"]["analytics"] = "healthy" if self.analytics_engine else "unavailable"
        health_status["components"]["monitoring"] = "healthy" if self.monitoring_service else "unavailable"
        
        return health_status
    
    async def shutdown(self) -> None:
        """Gracefully shutdown all logging components"""
        logger = logging.getLogger(__name__)
        logger.info("Shutting down IA Influencer Agent Logging System...")
        
        # Stop monitoring service
        if self.monitoring_service:
            await self.monitoring_service.stop()
            logger.info("Monitoring service stopped")
        
        # Stop retention manager
        if self.retention_manager:
            await self.retention_manager.stop_scheduler()
            logger.info("Retention manager stopped")
        
        # Stop Fluentd manager
        if self.fluentd_manager:
            await self.fluentd_manager.stop()
            logger.info("Fluentd manager stopped")
        
        # Disconnect Elasticsearch
        if self.es_manager:
            await self.es_manager.disconnect()
            logger.info("Elasticsearch disconnected")
        
        # Stop aggregator (should be last)
        if self.aggregator:
            await self.aggregator.stop()
            logger.info("Log aggregator stopped")
        
        self._is_running = False
        logger.info("IA Influencer Agent Logging System shutdown completed")
    
    @property
    def is_running(self) -> bool:
        """Check if the logging system is running"""
        return self._is_running


# Global logging system instance
_logging_system = None


async def get_logging_system(config: Optional[Dict[str, Any]] = None) -> IAInfluencerLoggingSystem:
    """
Get or create global logging system instance"""
    global _logging_system
    
    if _logging_system is None:
        _logging_system = IAInfluencerLoggingSystem(config)
        await _logging_system.initialize()
    
    return _logging_system


async def shutdown_logging_system() -> None:
    """
Shutdown global logging system"""
    global _logging_system
    
    if _logging_system:
        await _logging_system.shutdown()
        _logging_system = None


# Convenience functions for common operations
async def log_ai_event(message -> None: str, user_id -> None: str = None, **kwargs) -> None:
    """
Quick AI event logging"""
    system = await get_logging_system()
    await system.log_ai_processing(message, user_id, **kwargs)


async def log_fingerprint_event(message -> None: str, user_id -> None: str = None, **kwargs) -> None:
    """
Quick fingerprinting event logging"""
    system = await get_logging_system()
    await system.log_fingerprinting(message, user_id, **kwargs)


async def log_revenue_event(message -> None: str, user_id -> None: str = None, **kwargs) -> None:
    """
Quick revenue event logging"""
    system = await get_logging_system()
    await system.log_revenue_processing(message, user_id, **kwargs)


async def log_security_alert(message -> None: str, severity -> None: str = "medium", **kwargs) -> None:
    """Quick security alert logging"""
    system = await get_logging_system()
    await system.log_security_event(message, severity, **kwargs)


def main() -> None:
    """
CLI entry point for logging system management"""
    import argparse
    
    parser = argparse.ArgumentParser(description="IA Influencer Agent Logging System")
    parser.add_argument("command", choices=["start", "stop", "status", "health", "metrics"],
                       help="Command to execute")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    async def run_command() -> None:
        system = await get_logging_system()
        
        if args.command == "start":
            print("✅ Logging system started successfully")
        
        elif args.command == "stop":
            await shutdown_logging_system()
            print("✅ Logging system stopped successfully")
        
        elif args.command == "status":
            status = await system.health_check()
            print(f"Overall Status: {status['overall_status']}")
            for component, state in status['components'].items():
                print(f"  {component}: {state}")
        
        elif args.command == "health":
            health = await system.health_check()
            print(json.dumps(health, indent=2))
        
        elif args.command == "metrics":
            metrics = await system.get_system_metrics()
            print(json.dumps(metrics, indent=2))
    
    try:
        asyncio.run(run_command())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
