"""
Payment Processing Agent - Main Entry Point

Industrial payment processing system entry point with initialization,
configuration management, and service orchestration.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  CRITICAL LEGAL NOTICE:
This code and architectural design are the exclusive intellectual property of Fahed Mlaiel.
Unauthorized use, copying, distribution, or commercialization is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import logging
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from .payment_agent import PaymentProcessingAgent
from .config import PaymentConfig
from .cache import PerformanceCache
from .fraud_detection import FraudDetectionEngine
from .compliance import ComplianceManager
from .analytics import PaymentAnalytics
from .schedulers import PayoutScheduler
from .currency import CurrencyConverter
from .exceptions import PaymentProcessingError, ConfigurationError

logger = logging.getLogger(__name__)


class PaymentProcessingService:
    """
    Main payment processing service orchestrator.
    
    Manages initialization, lifecycle, and coordination of all payment
    processing components with proper error handling and monitoring.
    """
    
    def __init__(
        self,
        config: Optional[PaymentConfig] = None,
        enable_cache: bool = True,
        enable_fraud_detection: bool = True,
        enable_analytics: bool = True,
        enable_compliance: bool = True,
        enable_scheduling: bool = True
    ):
        """
        Initialize payment processing service.
        
        Args:
            config: Payment configuration
            enable_cache: Enable performance caching
            enable_fraud_detection: Enable fraud detection engine
            enable_analytics: Enable payment analytics
            enable_compliance: Enable compliance management
            enable_scheduling: Enable payout scheduling
        """
        self.config = config or PaymentConfig()
        
        # Component enablement flags
        self.enable_cache = enable_cache
        self.enable_fraud_detection = enable_fraud_detection
        self.enable_analytics = enable_analytics
        self.enable_compliance = enable_compliance
        self.enable_scheduling = enable_scheduling
        
        # Service components
        self.cache: Optional[PerformanceCache] = None
        self.fraud_engine: Optional[FraudDetectionEngine] = None
        self.compliance_manager: Optional[ComplianceManager] = None
        self.analytics_engine: Optional[PaymentAnalytics] = None
        self.payout_scheduler: Optional[PayoutScheduler] = None
        self.currency_converter: Optional[CurrencyConverter] = None
        self.payment_agent: Optional[PaymentProcessingAgent] = None
        
        # Service state
        self.initialized = False
        self.running = False
        
        logger.info("Payment processing service created")
    
    async def initialize(self) -> None:
        """Initialize all service components"""
        if self.initialized:
            logger.warning("Service already initialized")
            return
        
        try:
            logger.info("Initializing payment processing service...")
            
            # Initialize cache system
            if self.enable_cache:
                self.cache = PerformanceCache(
                    config=self.config,
                    redis_url=self.config.redis_url
                )
                await self.cache.initialize()
                logger.info("✅ Performance cache initialized")
            
            # Initialize currency converter
            self.currency_converter = CurrencyConverter(
                config=self.config,
                cache=self.cache
            )
            await self.currency_converter.initialize()
            logger.info("✅ Currency converter initialized")
            
            # Initialize fraud detection engine
            if self.enable_fraud_detection:
                self.fraud_engine = FraudDetectionEngine(
                    config=self.config
                )
                logger.info("✅ Fraud detection engine initialized")
            
            # Initialize compliance manager
            if self.enable_compliance:
                self.compliance_manager = ComplianceManager(
                    config=self.config
                )
                await self.compliance_manager.initialize()
                logger.info("✅ Compliance manager initialized")
            
            # Initialize analytics engine
            if self.enable_analytics:
                self.analytics_engine = PaymentAnalytics(
                    config=self.config,
                    cache=self.cache
                )
                await self.analytics_engine.initialize()
                logger.info("✅ Analytics engine initialized")
            
            # Initialize payout scheduler
            if self.enable_scheduling:
                self.payout_scheduler = PayoutScheduler(
                    config=self.config
                )
                await self.payout_scheduler.initialize()
                logger.info("✅ Payout scheduler initialized")
            
            # Initialize main payment agent
            self.payment_agent = PaymentProcessingAgent(
                config=self.config,
                cache=self.cache,
                fraud_engine=self.fraud_engine,
                compliance_manager=self.compliance_manager,
                analytics_engine=self.analytics_engine,
                currency_converter=self.currency_converter
            )
            await self.payment_agent.initialize()
            logger.info("✅ Payment processing agent initialized")
            
            self.initialized = True
            logger.info("🎉 Payment processing service fully initialized")
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {str(e)}")
            await self.shutdown()  # Cleanup on failure
            raise PaymentProcessingError(f"Service initialization failed: {str(e)}")
    
    async def start(self) -> None:
        """Start all service components"""
        if not self.initialized:
            await self.initialize()
        
        if self.running:
            logger.warning("Service already running")
            return
        
        try:
            logger.info("Starting payment processing service...")
            
            # Start schedulers
            if self.payout_scheduler:
                await self.payout_scheduler.start()
                logger.info("✅ Payout scheduler started")
            
            # Start background tasks
            if self.analytics_engine:
                await self.analytics_engine.start_background_tasks()
                logger.info("✅ Analytics background tasks started")
            
            self.running = True
            logger.info("🚀 Payment processing service is now running")
            
        except Exception as e:
            logger.error(f"❌ Service start failed: {str(e)}")
            raise PaymentProcessingError(f"Service start failed: {str(e)}")
    
    async def stop(self) -> None:
        """Stop all service components gracefully"""
        if not self.running:
            logger.warning("Service not running")
            return
        
        logger.info("Stopping payment processing service...")
        
        # Stop schedulers
        if self.payout_scheduler:
            await self.payout_scheduler.stop()
            logger.info("✅ Payout scheduler stopped")
        
        # Stop background tasks
        if self.analytics_engine:
            await self.analytics_engine.stop_background_tasks()
            logger.info("✅ Analytics background tasks stopped")
        
        self.running = False
        logger.info("⏹️ Payment processing service stopped")
    
    async def shutdown(self) -> None:
        """Shutdown all service components"""
        if self.running:
            await self.stop()
        
        if not self.initialized:
            return
        
        logger.info("Shutting down payment processing service...")
        
        # Shutdown components in reverse order
        if self.payment_agent:
            await self.payment_agent.shutdown()
            logger.info("✅ Payment agent shutdown")
        
        if self.payout_scheduler:
            await self.payout_scheduler.shutdown()
            logger.info("✅ Payout scheduler shutdown")
        
        if self.analytics_engine:
            await self.analytics_engine.shutdown()
            logger.info("✅ Analytics engine shutdown")
        
        if self.compliance_manager:
            await self.compliance_manager.shutdown()
            logger.info("✅ Compliance manager shutdown")
        
        if self.currency_converter:
            await self.currency_converter.shutdown()
            logger.info("✅ Currency converter shutdown")
        
        if self.cache:
            await self.cache.shutdown()
            logger.info("✅ Performance cache shutdown")
        
        self.initialized = False
        logger.info("🔌 Payment processing service fully shutdown")
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all components"""
        health_status = {
            "service": {
                "initialized": self.initialized,
                "running": self.running,
                "status": "healthy" if self.initialized and self.running else "unhealthy"
            },
            "components": {}
        }
        
        # Check cache health
        if self.cache:
            try:
                cache_metrics = await self.cache.get_metrics()
                health_status["components"]["cache"] = {
                    "status": "healthy",
                    "metrics": cache_metrics
                }
            except Exception as e:
                health_status["components"]["cache"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check payment agent health
        if self.payment_agent:
            try:
                agent_health = await self.payment_agent.health_check()
                health_status["components"]["payment_agent"] = agent_health
            except Exception as e:
                health_status["components"]["payment_agent"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check scheduler health
        if self.payout_scheduler:
            try:
                scheduler_health = await self.payout_scheduler.get_status()
                health_status["components"]["scheduler"] = {
                    "status": "healthy",
                    "details": scheduler_health
                }
            except Exception as e:
                health_status["components"]["scheduler"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check analytics health
        if self.analytics_engine:
            try:
                analytics_metrics = await self.analytics_engine.get_performance_metrics()
                health_status["components"]["analytics"] = {
                    "status": "healthy",
                    "metrics": analytics_metrics
                }
            except Exception as e:
                health_status["components"]["analytics"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        return health_status
    
    def get_agent(self) -> PaymentProcessingAgent:
        """Get the main payment processing agent"""
        if not self.payment_agent:
            raise PaymentProcessingError("Payment agent not initialized")
        return self.payment_agent
    
    @asynccontextmanager
    async def lifespan(self):
        """Context manager for service lifecycle"""
        try:
            await self.start()
            yield self
        finally:
            await self.shutdown()


# Singleton service instance
_service_instance: Optional[PaymentProcessingService] = None


async def get_service(config: Optional[PaymentConfig] = None) -> PaymentProcessingService:
    """
    Get or create the global payment processing service instance.
    
    Args:
        config: Optional configuration override
        
    Returns:
        PaymentProcessingService instance
    """
    global _service_instance
    
    if _service_instance is None:
        _service_instance = PaymentProcessingService(config)
        await _service_instance.initialize()
    
    return _service_instance


async def get_payment_agent(config: Optional[PaymentConfig] = None) -> PaymentProcessingAgent:
    """
    Get the payment processing agent instance.
    
    Args:
        config: Optional configuration override
        
    Returns:
        PaymentProcessingAgent instance
    """
    service = await get_service(config)
    return service.get_agent()


async def shutdown_service():
    """Shutdown the global service instance"""
    global _service_instance
    
    if _service_instance:
        await _service_instance.shutdown()
        _service_instance = None


# Factory functions for individual components
async def create_fraud_engine(config: Optional[PaymentConfig] = None) -> FraudDetectionEngine:
    """Create fraud detection engine"""
    config = config or PaymentConfig()
    return FraudDetectionEngine(config=config)


async def create_compliance_manager(config: Optional[PaymentConfig] = None) -> ComplianceManager:
    """Create compliance manager"""
    config = config or PaymentConfig()
    manager = ComplianceManager(config=config)
    await manager.initialize()
    return manager


async def create_analytics_engine(
    config: Optional[PaymentConfig] = None,
    cache: Optional[PerformanceCache] = None
) -> PaymentAnalytics:
    """Create analytics engine"""
    config = config or PaymentConfig()
    engine = PaymentAnalytics(config=config, cache=cache)
    await engine.initialize()
    return engine


async def create_currency_converter(
    config: Optional[PaymentConfig] = None,
    cache: Optional[PerformanceCache] = None
) -> CurrencyConverter:
    """Create currency converter"""
    config = config or PaymentConfig()
    converter = CurrencyConverter(config=config, cache=cache)
    await converter.initialize()
    return converter


# CLI and testing utilities
async def run_health_check():
    """Run a comprehensive health check"""
    try:
        service = await get_service()
        health = await service.health_check()
        
        print("=== Payment Processing Service Health Check ===")
        print(f"Service Status: {health['service']['status']}")
        print(f"Initialized: {health['service']['initialized']}")
        print(f"Running: {health['service']['running']}")
        
        print("\n=== Component Status ===")
        for component, status in health['components'].items():
            print(f"{component}: {status['status']}")
            if status['status'] == 'unhealthy' and 'error' in status:
                print(f"  Error: {status['error']}")
        
        return health['service']['status'] == 'healthy'
        
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return False


async def run_performance_test():
    """Run basic performance tests"""
    try:
        service = await get_service()
        agent = service.get_agent()
        
        print("=== Performance Test ===")
        
        # Test cache performance
        if service.cache:
            import time
            start_time = time.time()
            
            # Write test
            await service.cache.set("test_key", "test_value")
            
            # Read test
            value = await service.cache.get("test_key")
            
            end_time = time.time()
            print(f"Cache round-trip: {(end_time - start_time) * 1000:.2f}ms")
        
        # Test currency conversion
        if service.currency_converter:
            start_time = time.time()
            
            from decimal import Decimal
            converted_amount, rate = await service.currency_converter.convert(
                amount=Decimal("100.00"),
                from_currency="USD",
                to_currency="EUR"
            )
            
            end_time = time.time()
            print(f"Currency conversion: {(end_time - start_time) * 1000:.2f}ms")
            print(f"Converted $100 USD to €{converted_amount} EUR (rate: {rate.rate})")
        
        print("Performance test completed successfully")
        return True
        
    except Exception as e:
        print(f"Performance test failed: {str(e)}")
        return False


if __name__ == "__main__":
    import sys
    
    async def main():
        """Main entry point for CLI usage"""
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "health":
                success = await run_health_check()
                sys.exit(0 if success else 1)
            
            elif command == "test":
                success = await run_performance_test()
                sys.exit(0 if success else 1)
            
            elif command == "run":
                # Run service indefinitely
                async with PaymentProcessingService().lifespan() as service:
                    print("Payment processing service is running...")
                    print("Press Ctrl+C to stop")
                    try:
                        while True:
                            await asyncio.sleep(1)
                    except KeyboardInterrupt:
                        print("\nShutting down...")
            
            else:
                print(f"Unknown command: {command}")
                print("Available commands: health, test, run")
                sys.exit(1)
        else:
            print("Payment Processing Agent - Industrial System")
            print("Usage: python index.py [health|test|run]")
            print("  health - Run health check")
            print("  test   - Run performance tests")  
            print("  run    - Start service")
    
    # Run main function
    asyncio.run(main())
