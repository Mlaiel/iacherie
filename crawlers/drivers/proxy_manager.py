"""
Enterprise Proxy Management System
==================================

Professional proxy management and rotation for industrial-grade web automation.
Handles proxy validation, rotation, load balancing, and failover for anonymous crawling.

Key Features:
- Multi-proxy provider support (residential, datacenter, mobile)
- Intelligent proxy rotation and load balancing
- Health monitoring and automatic failover
- Geographic IP distribution management
- Performance optimization and caching
- Authentication and credential management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️  LEGAL WARNING:
This code is proprietary and confidential. Any unauthorized copying, modification, 
distribution, or use without explicit written permission from Fahed Mlaiel is strictly 
prohibited and may result in legal action.
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from urllib.parse import urlparse
import socket
import ssl
import aiohttp
import requests
from concurrent.futures import ThreadPoolExecutor

from ...core.config import settings
from ...core.exceptions import ProxyError, ConnectionError, ValidationError
from ...utils.rate_limiter import RateLimiter
from ...utils.health_checker import HealthChecker
from ...utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


class ProxyType(Enum):
    """Supported proxy types"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyProvider(Enum):
    """Supported proxy providers"""
    RESIDENTIAL = "residential"
    DATACENTER = "datacenter"
    MOBILE = "mobile"
    CUSTOM = "custom"


class ProxyStatus(Enum):
    """Proxy operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    BANNED = "banned"
    TESTING = "testing"


@dataclass
class ProxyCredentials:
    """Proxy authentication credentials"""
    username: Optional[str] = None
    password: Optional[str] = None
    auth_token: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ProxyConfiguration:
    """Comprehensive proxy configuration"""
    host: str
    port: int
    proxy_type: ProxyType = ProxyType.HTTP
    provider: ProxyProvider = ProxyProvider.DATACENTER
    credentials: Optional[ProxyCredentials] = None
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    anonymity_level: str = "high"  # low, medium, high, elite
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    timeout: int = 30
    retry_count: int = 3
    sticky_session: bool = False
    session_duration: int = 600  # 10 minutes
    custom_headers: Dict[str, str] = field(default_factory=dict)


@dataclass
class ProxyMetrics:
    """Proxy performance and usage metrics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    success_rate: float = 0.0
    last_used: float = 0.0
    last_success: float = 0.0
    consecutive_failures: int = 0
    total_uptime: float = 0.0
    bandwidth_used: float = 0.0  # MB
    errors: List[str] = field(default_factory=list)


@dataclass
class ProxyInstance:
    """Proxy instance with metrics and management"""
    config: ProxyConfiguration
    status: ProxyStatus = ProxyStatus.INACTIVE
    metrics: ProxyMetrics = field(default_factory=ProxyMetrics)
    created_at: float = field(default_factory=time.time)
    last_health_check: float = 0.0
    health_score: float = 1.0
    current_session_id: Optional[str] = None
    session_start_time: Optional[float] = None
    rate_limiter: Optional[RateLimiter] = None
    
    def __post_init__(self):
        self.rate_limiter = RateLimiter(
            max_requests=self.config.max_requests_per_minute,
            time_window=60
        )


class ProxyValidator:
    """Proxy validation and testing utilities"""
    
    def __init__(self):
        self.test_urls = [
            "http://httpbin.org/ip",
            "https://httpbin.org/headers",
            "http://icanhazip.com",
            "https://api.ipify.org"
        ]
    
    async def validate_proxy(self, proxy: ProxyInstance) -> bool:
        """Validate proxy functionality and performance"""
        try:
            proxy_url = self._build_proxy_url(proxy.config)
            
            # Test basic connectivity
            connector = aiohttp.TCPConnector()
            timeout = aiohttp.ClientTimeout(total=proxy.config.timeout)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                
                # Test multiple URLs
                success_count = 0
                total_tests = len(self.test_urls)
                total_response_time = 0.0
                
                for test_url in self.test_urls:
                    try:
                        start_time = time.time()
                        
                        async with session.get(
                            test_url,
                            proxy=proxy_url,
                            headers=proxy.config.custom_headers
                        ) as response:
                            
                            response_time = time.time() - start_time
                            total_response_time += response_time
                            
                            if response.status == 200:
                                success_count += 1
                                
                                # Validate response for IP tests
                                if "ip" in test_url.lower():
                                    data = await response.json()
                                    detected_ip = data.get('origin', '').split(',')[0].strip()
                                    if detected_ip != proxy.config.host:
                                        logger.debug(f"Proxy IP validation: {detected_ip} vs {proxy.config.host}")
                    
                    except Exception as e:
                        logger.debug(f"Proxy test failed for {test_url}: {str(e)}")
                        continue
                
                # Calculate success rate
                success_rate = success_count / total_tests
                avg_response_time = total_response_time / total_tests if total_tests > 0 else 0.0
                
                # Update metrics
                proxy.metrics.average_response_time = avg_response_time
                proxy.metrics.success_rate = success_rate
                proxy.health_score = success_rate
                
                # Determine if proxy is valid
                is_valid = success_rate >= 0.7 and avg_response_time < proxy.config.timeout
                
                if is_valid:
                    proxy.status = ProxyStatus.ACTIVE
                    proxy.metrics.last_success = time.time()
                    proxy.metrics.consecutive_failures = 0
                else:
                    proxy.status = ProxyStatus.FAILED
                    proxy.metrics.consecutive_failures += 1
                
                proxy.last_health_check = time.time()
                
                logger.debug(f"Proxy validation: {proxy.config.host}:{proxy.config.port} - "
                           f"Success rate: {success_rate:.2f}, Avg time: {avg_response_time:.2f}s")
                
                return is_valid
                
        except Exception as e:
            proxy.status = ProxyStatus.FAILED
            proxy.metrics.consecutive_failures += 1
            proxy.metrics.errors.append(str(e))
            logger.error(f"Proxy validation failed: {str(e)}")
            return False
    
    def _build_proxy_url(self, config: ProxyConfiguration) -> str:
        """Build proxy URL for aiohttp"""
        auth_part = ""
        if config.credentials and config.credentials.username:
            auth_part = f"{config.credentials.username}:{config.credentials.password}@"
        
        return f"{config.proxy_type.value}://{auth_part}{config.host}:{config.port}"


class ProxyRotator:
    """Intelligent proxy rotation and selection"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0
        self.last_selection_time = 0.0
    
    def select_proxy(self, proxies: List[ProxyInstance], 
                    requirements: Optional[Dict[str, Any]] = None) -> Optional[ProxyInstance]:
        """Select optimal proxy based on strategy and requirements"""
        
        # Filter active proxies
        active_proxies = [p for p in proxies if p.status == ProxyStatus.ACTIVE]
        
        if not active_proxies:
            return None
        
        # Apply requirements filtering
        if requirements:
            active_proxies = self._filter_by_requirements(active_proxies, requirements)
        
        if not active_proxies:
            return None
        
        # Select based on strategy
        if self.strategy == "round_robin":
            return self._round_robin_selection(active_proxies)
        elif self.strategy == "least_used":
            return self._least_used_selection(active_proxies)
        elif self.strategy == "performance_based":
            return self._performance_based_selection(active_proxies)
        elif self.strategy == "random":
            return random.choice(active_proxies)
        elif self.strategy == "geographic":
            return self._geographic_selection(active_proxies, requirements)
        
        return active_proxies[0]
    
    def _round_robin_selection(self, proxies: List[ProxyInstance]) -> ProxyInstance:
        """Round-robin proxy selection"""
        if self.current_index >= len(proxies):
            self.current_index = 0
        
        selected = proxies[self.current_index]
        self.current_index += 1
        return selected
    
    def _least_used_selection(self, proxies: List[ProxyInstance]) -> ProxyInstance:
        """Select least used proxy"""
        return min(proxies, key=lambda p: p.metrics.total_requests)
    
    def _performance_based_selection(self, proxies: List[ProxyInstance]) -> ProxyInstance:
        """Select proxy based on performance metrics"""
        def score(proxy: ProxyInstance) -> float:
            # Weight factors: success rate (50%), response time (30%), health score (20%)
            success_weight = proxy.metrics.success_rate * 0.5
            time_weight = (1.0 / max(proxy.metrics.average_response_time, 0.1)) * 0.3
            health_weight = proxy.health_score * 0.2
            return success_weight + time_weight + health_weight
        
        return max(proxies, key=score)
    
    def _geographic_selection(self, proxies: List[ProxyInstance], 
                            requirements: Dict[str, Any]) -> ProxyInstance:
        """Select proxy based on geographic requirements"""
        preferred_country = requirements.get('country')
        preferred_city = requirements.get('city')
        
        if preferred_country:
            country_matches = [p for p in proxies if p.config.country == preferred_country]
            if country_matches:
                proxies = country_matches
        
        if preferred_city:
            city_matches = [p for p in proxies if p.config.city == preferred_city]
            if city_matches:
                proxies = city_matches
        
        return self._performance_based_selection(proxies)
    
    def _filter_by_requirements(self, proxies: List[ProxyInstance], 
                              requirements: Dict[str, Any]) -> List[ProxyInstance]:
        """Filter proxies by specific requirements"""
        filtered = proxies
        
        # Filter by provider
        if 'provider' in requirements:
            filtered = [p for p in filtered if p.config.provider == requirements['provider']]
        
        # Filter by anonymity level
        if 'anonymity_level' in requirements:
            filtered = [p for p in filtered if p.config.anonymity_level == requirements['anonymity_level']]
        
        # Filter by minimum success rate
        if 'min_success_rate' in requirements:
            min_rate = requirements['min_success_rate']
            filtered = [p for p in filtered if p.metrics.success_rate >= min_rate]
        
        # Filter by maximum response time
        if 'max_response_time' in requirements:
            max_time = requirements['max_response_time']
            filtered = [p for p in filtered if p.metrics.average_response_time <= max_time]
        
        return filtered


class ProxyManager:
    """
    Enterprise Proxy Management System
    
    Manages proxy pools, rotation, health monitoring, and performance optimization
    for industrial-grade web automation and crawling operations.
    """
    
    def __init__(self, validation_interval: int = 300, max_concurrent_validations: int = 10):
        self.proxies: Dict[str, ProxyInstance] = {}
        self.proxy_groups: Dict[str, List[str]] = {}  # Group proxies by purpose
        
        # Components
        self.validator = ProxyValidator()
        self.rotator = ProxyRotator()
        self.health_checker = HealthChecker()
        self.performance_monitor = PerformanceMonitor()
        
        # Configuration
        self.validation_interval = validation_interval
        self.max_concurrent_validations = max_concurrent_validations
        
        # Monitoring
        self.monitoring_active = True
        self.validation_task = None
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_validations)
        
        # Statistics
        self.stats = {
            'total_proxies': 0,
            'active_proxies': 0,
            'failed_proxies': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'average_response_time': 0.0
        }
        
        logger.info("ProxyManager initialized")
    
    async def initialize(self) -> None:
        """Initialize proxy manager and start monitoring"""
        try:
            # Start validation monitoring
            self.validation_task = asyncio.create_task(self._monitor_proxy_health())
            
            logger.info("ProxyManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize ProxyManager: {str(e)}")
            raise ProxyError(f"Initialization failed: {str(e)}")
    
    async def add_proxy(self, config: ProxyConfiguration, 
                       group: str = "default") -> str:
        """Add proxy to management pool"""
        proxy_id = f"{config.host}:{config.port}"
        
        if proxy_id in self.proxies:
            logger.warning(f"Proxy {proxy_id} already exists")
            return proxy_id
        
        try:
            # Create proxy instance
            proxy = ProxyInstance(config=config)
            
            # Validate proxy
            is_valid = await self.validator.validate_proxy(proxy)
            
            if is_valid:
                self.proxies[proxy_id] = proxy
                
                # Add to group
                if group not in self.proxy_groups:
                    self.proxy_groups[group] = []
                self.proxy_groups[group].append(proxy_id)
                
                # Update statistics
                self.stats['total_proxies'] += 1
                if proxy.status == ProxyStatus.ACTIVE:
                    self.stats['active_proxies'] += 1
                
                logger.info(f"Added proxy {proxy_id} to group {group}")
                return proxy_id
            else:
                raise ProxyError(f"Proxy validation failed for {proxy_id}")
                
        except Exception as e:
            logger.error(f"Failed to add proxy {proxy_id}: {str(e)}")
            raise ProxyError(f"Failed to add proxy: {str(e)}")
    
    async def remove_proxy(self, proxy_id: str) -> bool:
        """Remove proxy from management pool"""
        proxy = self.proxies.get(proxy_id)
        if not proxy:
            return False
        
        try:
            # Remove from groups
            for group, proxy_list in self.proxy_groups.items():
                if proxy_id in proxy_list:
                    proxy_list.remove(proxy_id)
            
            # Remove from main collection
            del self.proxies[proxy_id]
            
            # Update statistics
            self.stats['total_proxies'] -= 1
            if proxy.status == ProxyStatus.ACTIVE:
                self.stats['active_proxies'] -= 1
            
            logger.info(f"Removed proxy {proxy_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove proxy {proxy_id}: {str(e)}")
            return False
    
    async def get_proxy(self, group: str = "default", 
                       requirements: Optional[Dict[str, Any]] = None) -> Optional[ProxyInstance]:
        """Get optimal proxy for use"""
        try:
            # Get proxies from group
            proxy_ids = self.proxy_groups.get(group, [])
            if not proxy_ids:
                logger.warning(f"No proxies available in group {group}")
                return None
            
            group_proxies = [self.proxies[pid] for pid in proxy_ids if pid in self.proxies]
            
            # Select optimal proxy
            selected_proxy = self.rotator.select_proxy(group_proxies, requirements)
            
            if selected_proxy:
                # Check rate limiting
                if selected_proxy.rate_limiter and not selected_proxy.rate_limiter.is_available():
                    selected_proxy.status = ProxyStatus.RATE_LIMITED
                    return None
                
                # Update usage metrics
                selected_proxy.metrics.total_requests += 1
                selected_proxy.metrics.last_used = time.time()
                
                # Acquire rate limit token
                if selected_proxy.rate_limiter:
                    await selected_proxy.rate_limiter.acquire()
                
                self.stats['total_requests'] += 1
                
                logger.debug(f"Selected proxy {selected_proxy.config.host}:{selected_proxy.config.port}")
                return selected_proxy
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get proxy from group {group}: {str(e)}")
            return None
    
    async def report_proxy_result(self, proxy: ProxyInstance, 
                                 success: bool, response_time: float = 0.0,
                                 error: Optional[str] = None) -> None:
        """Report proxy usage result for metrics update"""
        try:
            if success:
                proxy.metrics.successful_requests += 1
                proxy.metrics.last_success = time.time()
                proxy.metrics.consecutive_failures = 0
                
                # Update health score
                proxy.health_score = min(1.0, proxy.health_score + 0.05)
                
                self.stats['successful_requests'] += 1
            else:
                proxy.metrics.failed_requests += 1
                proxy.metrics.consecutive_failures += 1
                
                # Update health score
                proxy.health_score = max(0.0, proxy.health_score - 0.1)
                
                if error:
                    proxy.metrics.errors.append(error)
                
                # Mark as failed if too many consecutive failures
                if proxy.metrics.consecutive_failures >= 5:
                    proxy.status = ProxyStatus.FAILED
                    self.stats['active_proxies'] -= 1
                    self.stats['failed_proxies'] += 1
            
            # Update response time
            if response_time > 0:
                total_requests = proxy.metrics.total_requests
                current_avg = proxy.metrics.average_response_time
                proxy.metrics.average_response_time = (
                    (current_avg * (total_requests - 1) + response_time) / total_requests
                )
            
            # Update success rate
            if proxy.metrics.total_requests > 0:
                proxy.metrics.success_rate = (
                    proxy.metrics.successful_requests / proxy.metrics.total_requests
                )
            
        except Exception as e:
            logger.error(f"Failed to report proxy result: {str(e)}")
    
    async def bulk_add_proxies(self, proxy_configs: List[ProxyConfiguration],
                              group: str = "default") -> Dict[str, bool]:
        """Add multiple proxies in bulk"""
        results = {}
        
        # Create semaphore to limit concurrent validations
        semaphore = asyncio.Semaphore(self.max_concurrent_validations)
        
        async def add_single_proxy(config: ProxyConfiguration) -> Tuple[str, bool]:
            async with semaphore:
                try:
                    proxy_id = await self.add_proxy(config, group)
                    return proxy_id, True
                except Exception as e:
                    proxy_id = f"{config.host}:{config.port}"
                    logger.error(f"Failed to add proxy {proxy_id}: {str(e)}")
                    return proxy_id, False
        
        # Process all proxies concurrently
        tasks = [add_single_proxy(config) for config in proxy_configs]
        completed = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in completed:
            if isinstance(result, tuple):
                proxy_id, success = result
                results[proxy_id] = success
            else:
                logger.error(f"Bulk add proxy task failed: {str(result)}")
        
        successful_count = sum(1 for success in results.values() if success)
        logger.info(f"Bulk added {successful_count}/{len(proxy_configs)} proxies to group {group}")
        
        return results
    
    async def _monitor_proxy_health(self) -> None:
        """Monitor proxy health and performance"""
        while self.monitoring_active:
            try:
                # Create validation tasks for all proxies
                validation_tasks = []
                
                for proxy_id, proxy in list(self.proxies.items()):
                    # Skip recent validations
                    if time.time() - proxy.last_health_check < self.validation_interval:
                        continue
                    
                    validation_tasks.append(self._validate_single_proxy(proxy_id))
                
                # Execute validations with concurrency limit
                if validation_tasks:
                    semaphore = asyncio.Semaphore(self.max_concurrent_validations)
                    
                    async def limited_validation(task):
                        async with semaphore:
                            return await task
                    
                    await asyncio.gather(*[limited_validation(task) for task in validation_tasks])
                
                # Update statistics
                self._update_statistics()
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Proxy health monitoring error: {str(e)}")
                await asyncio.sleep(30)
    
    async def _validate_single_proxy(self, proxy_id: str) -> None:
        """Validate single proxy"""
        proxy = self.proxies.get(proxy_id)
        if not proxy:
            return
        
        try:
            old_status = proxy.status
            is_valid = await self.validator.validate_proxy(proxy)
            
            # Update statistics if status changed
            if old_status != proxy.status:
                if old_status == ProxyStatus.ACTIVE and proxy.status != ProxyStatus.ACTIVE:
                    self.stats['active_proxies'] -= 1
                    self.stats['failed_proxies'] += 1
                elif old_status != ProxyStatus.ACTIVE and proxy.status == ProxyStatus.ACTIVE:
                    self.stats['active_proxies'] += 1
                    if old_status == ProxyStatus.FAILED:
                        self.stats['failed_proxies'] -= 1
            
        except Exception as e:
            logger.error(f"Proxy validation failed for {proxy_id}: {str(e)}")
    
    def _update_statistics(self) -> None:
        """Update global statistics"""
        active_count = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.ACTIVE)
        failed_count = sum(1 for p in self.proxies.values() if p.status == ProxyStatus.FAILED)
        
        self.stats['active_proxies'] = active_count
        self.stats['failed_proxies'] = failed_count
        self.stats['total_proxies'] = len(self.proxies)
        
        # Calculate average response time
        total_time = sum(p.metrics.average_response_time for p in self.proxies.values())
        proxy_count = len(self.proxies)
        self.stats['average_response_time'] = total_time / proxy_count if proxy_count > 0 else 0.0
    
    async def get_proxy_status(self, group: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive proxy status information"""
        if group:
            proxy_ids = self.proxy_groups.get(group, [])
            group_proxies = {pid: self.proxies[pid] for pid in proxy_ids if pid in self.proxies}
        else:
            group_proxies = self.proxies
        
        status_summary = {
            'total_proxies': len(group_proxies),
            'active_proxies': sum(1 for p in group_proxies.values() if p.status == ProxyStatus.ACTIVE),
            'failed_proxies': sum(1 for p in group_proxies.values() if p.status == ProxyStatus.FAILED),
            'rate_limited_proxies': sum(1 for p in group_proxies.values() if p.status == ProxyStatus.RATE_LIMITED),
            'average_health_score': sum(p.health_score for p in group_proxies.values()) / len(group_proxies) if group_proxies else 0.0,
            'statistics': self.stats.copy()
        }
        
        return status_summary
    
    async def get_best_proxies(self, count: int = 10, 
                             group: str = "default") -> List[ProxyInstance]:
        """Get best performing proxies"""
        proxy_ids = self.proxy_groups.get(group, [])
        group_proxies = [self.proxies[pid] for pid in proxy_ids if pid in self.proxies]
        
        # Filter active proxies and sort by performance
        active_proxies = [p for p in group_proxies if p.status == ProxyStatus.ACTIVE]
        
        # Sort by composite score
        def performance_score(proxy: ProxyInstance) -> float:
            return (proxy.health_score * 0.4 + 
                   proxy.metrics.success_rate * 0.4 + 
                   (1.0 / max(proxy.metrics.average_response_time, 0.1)) * 0.2)
        
        best_proxies = sorted(active_proxies, key=performance_score, reverse=True)
        return best_proxies[:count]
    
    async def cleanup_failed_proxies(self, group: Optional[str] = None) -> int:
        """Remove failed proxies from management"""
        proxies_to_remove = []
        
        if group:
            proxy_ids = self.proxy_groups.get(group, [])
            target_proxies = {pid: self.proxies[pid] for pid in proxy_ids if pid in self.proxies}
        else:
            target_proxies = self.proxies
        
        # Identify failed proxies
        for proxy_id, proxy in target_proxies.items():
            if (proxy.status == ProxyStatus.FAILED or 
                proxy.metrics.consecutive_failures >= 10 or
                proxy.health_score < 0.2):
                proxies_to_remove.append(proxy_id)
        
        # Remove failed proxies
        removed_count = 0
        for proxy_id in proxies_to_remove:
            if await self.remove_proxy(proxy_id):
                removed_count += 1
        
        logger.info(f"Cleaned up {removed_count} failed proxies")
        return removed_count
    
    async def shutdown(self) -> None:
        """Shutdown proxy manager and cleanup resources"""
        logger.info("Shutting down ProxyManager")
        
        # Stop monitoring
        self.monitoring_active = False
        
        if self.validation_task:
            self.validation_task.cancel()
        
        # Shutdown executor
        self.executor.shutdown(wait=True)
        
        # Clear proxies
        self.proxies.clear()
        self.proxy_groups.clear()
        
        logger.info("ProxyManager shutdown completed")


# Factory functions for common proxy configurations
def create_residential_proxy_config(host: str, port: int, 
                                   username: str, password: str) -> ProxyConfiguration:
    """Create residential proxy configuration"""
    return ProxyConfiguration(
        host=host,
        port=port,
        proxy_type=ProxyType.HTTP,
        provider=ProxyProvider.RESIDENTIAL,
        credentials=ProxyCredentials(username=username, password=password),
        anonymity_level="elite",
        max_requests_per_minute=30,  # Conservative for residential
        sticky_session=True,
        session_duration=1800  # 30 minutes
    )


def create_datacenter_proxy_config(host: str, port: int,
                                  username: Optional[str] = None,
                                  password: Optional[str] = None) -> ProxyConfiguration:
    """Create datacenter proxy configuration"""
    credentials = None
    if username and password:
        credentials = ProxyCredentials(username=username, password=password)
    
    return ProxyConfiguration(
        host=host,
        port=port,
        proxy_type=ProxyType.HTTP,
        provider=ProxyProvider.DATACENTER,
        credentials=credentials,
        anonymity_level="high",
        max_requests_per_minute=120,  # Higher for datacenter
        sticky_session=False
    )
