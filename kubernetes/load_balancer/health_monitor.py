"""Health Monitor for Load Balancer Services

Comprehensive health monitoring system for the IA Influencer Agent
platform's load balancer services, providing real-time health checks,
alerting, and automated recovery mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""

import asyncio
import logging
import time
import socket
import ssl
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import requests
import aiohttp
import psutil
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """
Health status enumeration"""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class CheckType(Enum):
    """Health check type enumeration"""

    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    PING = "ping"
    CUSTOM = "custom"


@dataclass
class HealthCheckConfig:
    """Health check configuration"""
    name: str
    type: CheckType
    target: str
    port: Optional[int] = None
    path: str = "/"
    method: str = "GET"
    headers: Dict[str, str] = field(default_factory=dict)
    timeout: float = 5.0
    interval: float = 10.0
    retries: int = 3
    expected_codes: List[int] = field(default_factory=lambda: [200])
    expected_response: Optional[str] = None
    ssl_verify: bool = True
    custom_check: Optional[Callable] = None


@dataclass
class HealthCheckResult:
    """Health check result"""
    name: str
    status: HealthStatus
    response_time: float
    timestamp: datetime
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceEndpoint:
    """
Service endpoint configuration"""
    name: str
    host: str
    port: int
    weight: int = 1
    health_checks: List[HealthCheckConfig] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HealthChecker:
    """
Individual health checker implementation"""
    
    def __init__(self, config -> None: HealthCheckConfig) -> None:
        self.config = config
        self.session = None
        
    async def __aenter__(self) -> None:
        if self.config.type in [CheckType.HTTP, CheckType.HTTPS]:
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context() if self.config.ssl_verify else False
            )
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        try:
            logger.info(f"Executing __aexit__")
            
            # Implementation for __aexit__
            # TODO: Add specific business logic here
            
            result = {

            
                'success': True,

            
                'timestamp': datetime.utcnow(),

            
                'completed': True

            
            }
            
            logger.info(f"__aexit__ completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"__aexit__ failed: {e}")
            raise
            await self.session.close()
    
    async def check_http(self) -> HealthCheckResult:
        """
Perform HTTP/HTTPS health check"""
        start_time = time.time()
        
        try:
            scheme = "https" if self.config.type == CheckType.HTTPS else "http"
            port_suffix = f":{self.config.port}" if self.config.port else ""
            url = f"{scheme}://{self.config.target}{port_suffix}{self.config.path}"
            
            async with self.session.request(
                method=self.config.method,
                url=url,
                headers=self.config.headers
            ) as response:
                response_time = time.time() - start_time
                content = await response.text()
                
                # Check status code
                if response.status not in self.config.expected_codes:
                    return HealthCheckResult(
                        name=self.config.name,
                        status=HealthStatus.UNHEALTHY,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        error_message=f"Unexpected status code: {response.status}",
                        details={
                            "status_code": response.status,
                            "response_headers": dict(response.headers),
                            "content_length": len(content)
                        }
                    )
                
                # Check expected response content
                if self.config.expected_response and self.config.expected_response not in content:
                    return HealthCheckResult(
                        name=self.config.name,
                        status=HealthStatus.UNHEALTHY,
                        response_time=response_time,
                        timestamp=datetime.now(),
                        error_message="Expected response content not found",
                        details={
                            "status_code": response.status,
                            "expected_content": self.config.expected_response,
                            "actual_content": content[:500]  # Truncate for logging
                        }
                    )
                
                return HealthCheckResult(
                    name=self.config.name,
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={
                        "status_code": response.status,
                        "content_length": len(content),
                        "response_headers": dict(response.headers)
                    }
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.config.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e),
                details={"exception_type": type(e).__name__}
            )
    
    async def check_tcp(self) -> HealthCheckResult:
        """Perform TCP port health check"""
        start_time = time.time()
        
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.config.target, self.config.port),
                timeout=self.config.timeout
            )
            
            response_time = time.time() - start_time
            writer.close()
            await writer.wait_closed()
            
            return HealthCheckResult(
                name=self.config.name,
                status=HealthStatus.HEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                details={"connection_established": True}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.config.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e),
                details={"exception_type": type(e).__name__}
            )
    
    async def check_ping(self) -> HealthCheckResult:
        """Perform ping health check"""
        start_time = time.time()
        
        try:
            # Use asyncio subprocess for ping
            process = await asyncio.create_subprocess_exec(
                'ping', '-c', '1', '-W', str(int(self.config.timeout)), self.config.target,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            response_time = time.time() - start_time
            
            if process.returncode == 0:
                return HealthCheckResult(
                    name=self.config.name,
                    status=HealthStatus.HEALTHY,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={"ping_output": stdout.decode().strip()}
                )
            else:
                return HealthCheckResult(
                    name=self.config.name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    error_message=stderr.decode().strip(),
                    details={"return_code": process.returncode}
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.config.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e),
                details={"exception_type": type(e).__name__}
            )
    
    async def check_custom(self) -> HealthCheckResult:
        """Perform custom health check"""
        start_time = time.time()
        
        try:
            if not self.config.custom_check:
                raise ValueError("Custom check function not provided")
            
            # Run custom check in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor,
                    self.config.custom_check,
                    self.config
                )
            
            response_time = time.time() - start_time
            
            if isinstance(result, bool):
                status = HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY
                return HealthCheckResult(
                    name=self.config.name,
                    status=status,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    details={"custom_result": result}
                )
            elif isinstance(result, dict):
                return HealthCheckResult(
                    name=self.config.name,
                    status=result.get('status', HealthStatus.UNKNOWN),
                    response_time=response_time,
                    timestamp=datetime.now(),
                    error_message=result.get('error'),
                    details=result.get('details', {})
                )
            else:
                raise ValueError(f"Invalid custom check result type: {type(result)}")
                
        except Exception as e:
            response_time = time.time() - start_time
            return HealthCheckResult(
                name=self.config.name,
                status=HealthStatus.UNHEALTHY,
                response_time=response_time,
                timestamp=datetime.now(),
                error_message=str(e),
                details={"exception_type": type(e).__name__}
            )
    
    async def perform_check(self) -> HealthCheckResult:
        """Perform health check based on type"""
        for attempt in range(self.config.retries):
            try:
                if self.config.type in [CheckType.HTTP, CheckType.HTTPS]:
                    result = await self.check_http()
                elif self.config.type == CheckType.TCP:
                    result = await self.check_tcp()
                elif self.config.type == CheckType.PING:
                    result = await self.check_ping()
                elif self.config.type == CheckType.CUSTOM:
                    result = await self.check_custom()
                else:
                    raise ValueError(f"Unsupported check type: {self.config.type}")
                
                # If check is successful, return immediately
                if result.status == HealthStatus.HEALTHY:
                    return result
                
                # If this is the last attempt, return the result
                if attempt == self.config.retries - 1:
                    return result
                
                # Wait before retry
                await asyncio.sleep(1)
                
            except Exception as e:
                if attempt == self.config.retries - 1:
                    return HealthCheckResult(
                        name=self.config.name,
                        status=HealthStatus.UNHEALTHY,
                        response_time=self.config.timeout,
                        timestamp=datetime.now(),
                        error_message=f"Check failed after {self.config.retries} attempts: {str(e)}",
                        details={"exception_type": type(e).__name__, "attempts": attempt + 1}
                    )


class HealthMonitor:
    """Enterprise Health Monitor for Load Balancer Services"""
    
    def __init__(self) -> None:
        self.endpoints: Dict[str, ServiceEndpoint] = {}
        self.health_history: Dict[str, List[HealthCheckResult]] = {}
        self.alert_callbacks: List[Callable] = []
        self.running = False
        self.tasks: List[asyncio.Task] = []
        self.history_retention = timedelta(hours=24)
    
    def add_endpoint(self, endpoint: ServiceEndpoint) -> bool:
        """
Add service endpoint for monitoring"""
        try:
            self.endpoints[endpoint.name] = endpoint
            self.health_history[endpoint.name] = []
            logger.info(f"Endpoint {endpoint.name} added to monitoring")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add endpoint {endpoint.name}: {e}")
            return False
    
    def remove_endpoint(self, endpoint_name: str) -> bool:
        """Remove service endpoint from monitoring"""
        try:
            if endpoint_name in self.endpoints:
                del self.endpoints[endpoint_name]
                del self.health_history[endpoint_name]
                logger.info(f"Endpoint {endpoint_name} removed from monitoring")
                return True
            else:
                logger.warning(f"Endpoint {endpoint_name} not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove endpoint {endpoint_name}: {e}")
            return False
    
    def add_alert_callback(self, callback: Callable[[HealthCheckResult], None]) -> None:
        """Add callback for health status alerts"""
        self.alert_callbacks.append(callback)
    
    async def check_endpoint_health(self, endpoint: ServiceEndpoint) -> List[HealthCheckResult]:
        """
Check health of a single endpoint"""
        results = []
        
        for health_check in endpoint.health_checks:
            async with HealthChecker(health_check) as checker:
                result = await checker.perform_check()
                results.append(result)
                
                # Store in history
                self.health_history[endpoint.name].append(result)
                
                # Trigger alerts if unhealthy
                if result.status != HealthStatus.HEALTHY:
                    for callback in self.alert_callbacks:
                        try:
                            callback(result)
                        except Exception as e:
                            logger.error(f"Alert callback failed: {e}")
        
        # Clean old history
        self._clean_history(endpoint.name)
        
        return results
    
    def _clean_history(self, endpoint_name: str) -> None:
        """Clean old health check history"""
        cutoff_time = datetime.now() - self.history_retention
        self.health_history[endpoint_name] = [
            result for result in self.health_history[endpoint_name]
            if result.timestamp > cutoff_time
        ]
    
    async def monitor_endpoint(self, endpoint: ServiceEndpoint) -> None:
        """
Continuously monitor a single endpoint"""
        while self.running:
            try:
                await self.check_endpoint_health(endpoint)
                
                # Calculate next check interval
                min_interval = min(
                    check.interval for check in endpoint.health_checks
                ) if endpoint.health_checks else 60.0
                
                await asyncio.sleep(min_interval)
                
            except Exception as e:
                logger.error(f"Error monitoring endpoint {endpoint.name}: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def start_monitoring(self) -> None:
        """Start health monitoring for all endpoints"""
        if self.running:
            logger.warning("Health monitoring is already running")
            return
        
        self.running = True
        logger.info("Starting health monitoring")
        
        # Create monitoring tasks for each endpoint
        for endpoint in self.endpoints.values():
            task = asyncio.create_task(self.monitor_endpoint(endpoint))
            self.tasks.append(task)
        
        logger.info(f"Health monitoring started for {len(self.endpoints)} endpoints")
    
    async def stop_monitoring(self) -> None:
        """Stop health monitoring"""
        if not self.running:
            logger.warning("Health monitoring is not running")
            return
        
        self.running = False
        logger.info("Stopping health monitoring")
        
        # Cancel all monitoring tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("Health monitoring stopped")
    
    def get_endpoint_status(self, endpoint_name: str) -> Dict[str, Any]:
        """Get current status of an endpoint"""
        if endpoint_name not in self.endpoints:
            return {"error": f"Endpoint {endpoint_name} not found"}
        
        endpoint = self.endpoints[endpoint_name]
        history = self.health_history.get(endpoint_name, [])
        
        if not history:
            return {
                "name": endpoint_name,
                "status": HealthStatus.UNKNOWN.value,
                "last_check": None,
                "checks_count": 0
            }
        
        # Get latest results for each check
        latest_results = {}
        for result in reversed(history):
            if result.name not in latest_results:
                latest_results[result.name] = result
        
        # Determine overall status
        statuses = [result.status for result in latest_results.values()]
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNHEALTHY
        
        # Calculate uptime
        recent_checks = history[-100:] if len(history) > 100 else history
        healthy_checks = sum(1 for result in recent_checks if result.status == HealthStatus.HEALTHY)
        uptime_percentage = (healthy_checks / len(recent_checks)) * 100 if recent_checks else 0
        
        return {
            "name": endpoint_name,
            "host": endpoint.host,
            "port": endpoint.port,
            "status": overall_status.value,
            "uptime_percentage": round(uptime_percentage, 2),
            "last_check": max(result.timestamp for result in latest_results.values()).isoformat(),
            "checks_count": len(history),
            "check_results": [
                {
                    "name": result.name,
                    "status": result.status.value,
                    "response_time": result.response_time,
                    "timestamp": result.timestamp.isoformat(),
                    "error": result.error_message
                }
                for result in latest_results.values()
            ]
        }
    
    def get_all_endpoints_status(self) -> Dict[str, Any]:
        """Get status of all monitored endpoints"""
        return {
            "monitoring_active": self.running,
            "endpoints_count": len(self.endpoints),
            "endpoints": [
                self.get_endpoint_status(name) for name in self.endpoints.keys()
            ],
            "timestamp": datetime.now().isoformat()
        }
    
    def configure_platform_endpoints(self) -> bool:
        """Configure health monitoring for platform services"""
        try:
            # Configure fingerprinting service endpoints
            fingerprinting_endpoints = [
                ServiceEndpoint(
                    name="fingerprinting-service-1",
                    host="fingerprint-service-1",
                    port=8001,
                    health_checks=[
                        HealthCheckConfig(
                            name="fingerprinting_http_health",
                            type=CheckType.HTTP,
                            target="fingerprint-service-1",
                            port=8001,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        ),
                        HealthCheckConfig(
                            name="fingerprinting_api_health",
                            type=CheckType.HTTP,
                            target="fingerprint-service-1",
                            port=8001,
                            path="/api/v1/fingerprinting/status",
                            interval=30.0,
                            timeout=10.0,
                            expected_codes=[200]
                        )
                    ]
                ),
                ServiceEndpoint(
                    name="fingerprinting-service-2",
                    host="fingerprint-service-2",
                    port=8001,
                    health_checks=[
                        HealthCheckConfig(
                            name="fingerprinting_http_health",
                            type=CheckType.HTTP,
                            target="fingerprint-service-2",
                            port=8001,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        )
                    ]
                )
            ]
            
            # Configure protection service endpoints
            protection_endpoints = [
                ServiceEndpoint(
                    name="protection-service-1",
                    host="protection-service-1",
                    port=8002,
                    health_checks=[
                        HealthCheckConfig(
                            name="protection_http_health",
                            type=CheckType.HTTP,
                            target="protection-service-1",
                            port=8002,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        )
                    ]
                ),
                ServiceEndpoint(
                    name="protection-service-2",
                    host="protection-service-2",
                    port=8002,
                    health_checks=[
                        HealthCheckConfig(
                            name="protection_http_health",
                            type=CheckType.HTTP,
                            target="protection-service-2",
                            port=8002,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        )
                    ]
                )
            ]
            
            # Configure monetization service endpoints
            monetization_endpoints = [
                ServiceEndpoint(
                    name="monetization-service-1",
                    host="monetization-service-1",
                    port=8003,
                    health_checks=[
                        HealthCheckConfig(
                            name="monetization_http_health",
                            type=CheckType.HTTP,
                            target="monetization-service-1",
                            port=8003,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        ),
                        HealthCheckConfig(
                            name="monetization_payment_health",
                            type=CheckType.HTTP,
                            target="monetization-service-1",
                            port=8003,
                            path="/api/v1/monetization/payment/status",
                            interval=60.0,
                            timeout=15.0,
                            expected_codes=[200]
                        )
                    ]
                )
            ]
            
            # Configure AI agent service endpoints
            ai_agent_endpoints = [
                ServiceEndpoint(
                    name="ai-agent-service-1",
                    host="ai-agent-service-1",
                    port=8004,
                    health_checks=[
                        HealthCheckConfig(
                            name="ai_agent_http_health",
                            type=CheckType.HTTP,
                            target="ai-agent-service-1",
                            port=8004,
                            path="/health",
                            interval=10.0,
                            timeout=5.0,
                            expected_codes=[200]
                        )
                    ]
                )
            ]
            
            # Add all endpoints
            all_endpoints = (
                fingerprinting_endpoints +
                protection_endpoints +
                monetization_endpoints +
                ai_agent_endpoints
            )
            
            for endpoint in all_endpoints:
                self.add_endpoint(endpoint)
            
            logger.info(f"Platform endpoints configured: {len(all_endpoints)} endpoints")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform endpoints: {e}")
            return False
