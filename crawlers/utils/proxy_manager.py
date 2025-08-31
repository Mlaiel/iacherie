"""Proxy Manager Module
====================

Professional proxy management for web crawling with rotation and validation.
Implements intelligent proxy rotation, health monitoring, and failover.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

WARNING: This code is protected by copyright law. Any unauthorized copying, 
distribution, or modification is strictly prohibited and will result in 
legal action. Contact mlaiel@live.de for licensing.
"""import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import random
import aiohttp
import time
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

@dataclass
class ProxyInfo:
    """Proxy information structure."""    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = 'http'
    country: Optional[str] = None
    region: Optional[str] = None
    is_residential: bool = False
    is_datacenter: bool = True

@dataclass
class ProxyMetrics:
    """Proxy performance metrics."""    success_rate: float = 1.0
    average_response_time: float = 0.0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    consecutive_failures: int = 0
    is_banned: bool = False
    ban_expires: Optional[datetime] = None

class ProxyManager:
    """    Professional proxy management system.
    
    Features:
    - Intelligent proxy rotation
    - Health monitoring and validation
    - Automatic failover
    - Geographic distribution
    - Performance tracking
    - Ban detection and recovery
    - Load balancing
    - Proxy type optimization
    """    
    def __init__(self):
        """Initialize proxy manager."""        self.proxies: List[ProxyInfo] = []
        self.proxy_metrics: Dict[str, ProxyMetrics] = {}
        self.current_proxy_index = 0
        self.rotation_strategy = 'round_robin'  # round_robin, random, performance_based
        self.health_check_interval = 300  # 5 minutes
        self.max_consecutive_failures = 3
        self.ban_duration = 3600  # 1 hour
        self.test_url = "https://httpbin.org/ip"
        
        # Load proxies from configuration
        self._load_proxy_configuration()
        
        # Start background health monitoring
        asyncio.create_task(self._health_monitor())
    
    def _load_proxy_configuration(self):
        """Load proxy configuration from settings."""        # This would load from environment variables or config files
        # For now, we'll use sample configuration
        sample_proxies = [
            ProxyInfo("proxy1.example.com", 8080, "user1", "pass1"),
            ProxyInfo("proxy2.example.com", 8080, "user2", "pass2"),
            ProxyInfo("proxy3.example.com", 8080, "user3", "pass3"),
        ]
        
        for proxy in sample_proxies:
            self.add_proxy(proxy)
    
    def add_proxy(self, proxy: ProxyInfo) -> None:
        """Add a proxy to the pool."""        proxy_key = self._get_proxy_key(proxy)
        
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.proxy_metrics[proxy_key] = ProxyMetrics()
            logger.info(f"Added proxy: {proxy.host}:{proxy.port}")
    
    def remove_proxy(self, proxy: ProxyInfo) -> None:
        """Remove a proxy from the pool."""        if proxy in self.proxies:
            self.proxies.remove(proxy)
            proxy_key = self._get_proxy_key(proxy)
            if proxy_key in self.proxy_metrics:
                del self.proxy_metrics[proxy_key]
            logger.info(f"Removed proxy: {proxy.host}:{proxy.port}")
    
    def _get_proxy_key(self, proxy: ProxyInfo) -> str:
        """Generate unique key for proxy."""        return f"{proxy.host}:{proxy.port}"
    
    async def get_proxy(self, target_country: Optional[str] = None) -> Optional[ProxyInfo]:
        """        Get next available proxy based on rotation strategy.
        
        Args:
            target_country: Preferred country for geo-targeting
            
        Returns:
            ProxyInfo object or None if no proxies available
        """        if not self.proxies:
            logger.warning("No proxies available")
            return None
        
        # Filter available proxies
        available_proxies = self._get_available_proxies(target_country)
        
        if not available_proxies:
            logger.warning("No available proxies found")
            return None
        
        # Select proxy based on strategy
        if self.rotation_strategy == 'round_robin':
            return self._get_next_round_robin(available_proxies)
        elif self.rotation_strategy == 'random':
            return random.choice(available_proxies)
        elif self.rotation_strategy == 'performance_based':
            return self._get_best_performing_proxy(available_proxies)
        else:
            return available_proxies[0]
    
    def _get_available_proxies(self, target_country: Optional[str] = None) -> List[ProxyInfo]:
        """Get list of available (non-banned) proxies."""        available = []
        current_time = datetime.now()
        
        for proxy in self.proxies:
            proxy_key = self._get_proxy_key(proxy)
            metrics = self.proxy_metrics.get(proxy_key)
            
            if not metrics:
                available.append(proxy)
                continue
            
            # Check if proxy is banned and ban has expired
            if metrics.is_banned:
                if metrics.ban_expires and current_time > metrics.ban_expires:
                    metrics.is_banned = False
                    metrics.consecutive_failures = 0
                    logger.info(f"Proxy ban expired: {proxy.host}:{proxy.port}")
                else:
                    continue
            
            # Filter by country if specified
            if target_country and proxy.country != target_country:
                continue
            
            available.append(proxy)
        
        return available
    
    def _get_next_round_robin(self, available_proxies: List[ProxyInfo]) -> ProxyInfo:
        """Get next proxy using round-robin strategy."""        if self.current_proxy_index >= len(available_proxies):
            self.current_proxy_index = 0
        
        proxy = available_proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(available_proxies)
        
        return proxy
    
    def _get_best_performing_proxy(self, available_proxies: List[ProxyInfo]) -> ProxyInfo:
        """Get proxy with best performance metrics."""        best_proxy = None
        best_score = -1
        
        for proxy in available_proxies:
            proxy_key = self._get_proxy_key(proxy)
            metrics = self.proxy_metrics.get(proxy_key)
            
            if not metrics:
                score = 1.0  # New proxy gets high score
            else:
                # Calculate performance score
                score = self._calculate_performance_score(metrics)
            
            if score > best_score:
                best_score = score
                best_proxy = proxy
        
        return best_proxy
    
    def _calculate_performance_score(self, metrics: ProxyMetrics) -> float:
        """Calculate performance score for proxy."""        if metrics.total_requests == 0:
            return 1.0
        
        # Base score from success rate
        score = metrics.success_rate
        
        # Penalty for slow response times
        if metrics.average_response_time > 5.0:
            score *= 0.5
        elif metrics.average_response_time > 2.0:
            score *= 0.8
        
        # Penalty for recent failures
        if metrics.consecutive_failures > 0:
            score *= (0.5 ** metrics.consecutive_failures)
        
        # Bonus for recent successful use
        if metrics.last_success:
            hours_since_success = (datetime.now() - metrics.last_success).total_seconds() / 3600
            if hours_since_success < 1:
                score *= 1.2
        
        return max(0.0, min(1.0, score))
    
    async def record_proxy_usage(
        self,
        proxy: ProxyInfo,
        success: bool,
        response_time: float,
        error_type: Optional[str] = None
    ) -> None:
        """Record proxy usage metrics."""        proxy_key = self._get_proxy_key(proxy)
        metrics = self.proxy_metrics.get(proxy_key)
        
        if not metrics:
            metrics = ProxyMetrics()
            self.proxy_metrics[proxy_key] = metrics
        
        # Update basic metrics
        metrics.total_requests += 1
        metrics.last_used = datetime.now()
        
        if success:
            metrics.successful_requests += 1
            metrics.last_success = datetime.now()
            metrics.consecutive_failures = 0
            
            # Update average response time
            if metrics.average_response_time == 0:
                metrics.average_response_time = response_time
            else:
                # Exponential moving average
                alpha = 0.3
                metrics.average_response_time = (
                    alpha * response_time + 
                    (1 - alpha) * metrics.average_response_time
                )
        else:
            metrics.failed_requests += 1
            metrics.consecutive_failures += 1
            
            # Check if proxy should be banned
            if metrics.consecutive_failures >= self.max_consecutive_failures:
                await self._ban_proxy(proxy, error_type)
        
        # Update success rate
        metrics.success_rate = metrics.successful_requests / metrics.total_requests
    
    async def _ban_proxy(self, proxy: ProxyInfo, error_type: Optional[str] = None) -> None:
        """Ban a proxy temporarily."""        proxy_key = self._get_proxy_key(proxy)
        metrics = self.proxy_metrics.get(proxy_key)
        
        if metrics:
            metrics.is_banned = True
            metrics.ban_expires = datetime.now() + timedelta(seconds=self.ban_duration)
            
            logger.warning(
                f"Banned proxy {proxy.host}:{proxy.port} for {self.ban_duration}s "
                f"(failures: {metrics.consecutive_failures}, error: {error_type})"
            )
    
    async def validate_proxy(self, proxy: ProxyInfo) -> bool:
        """Validate if proxy is working."""        try:
            proxy_url = self._build_proxy_url(proxy)
            
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector()
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            ) as session:
                start_time = time.time()
                
                async with session.get(
                    self.test_url,
                    proxy=proxy_url
                ) as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Record successful validation
                        await self.record_proxy_usage(proxy, True, response_time)
                        
                        logger.debug(f"Proxy {proxy.host}:{proxy.port} validated successfully")
                        return True
                    else:
                        await self.record_proxy_usage(proxy, False, response_time, f"HTTP_{response.status}")
                        return False
                        
        except Exception as e:
            await self.record_proxy_usage(proxy, False, 10.0, str(type(e).__name__))
            logger.debug(f"Proxy validation failed for {proxy.host}:{proxy.port}: {e}")
            return False
    
    def _build_proxy_url(self, proxy: ProxyInfo) -> str:
        """Build proxy URL for aiohttp."""        if proxy.username and proxy.password:
            return f"{proxy.protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"
        else:
            return f"{proxy.protocol}://{proxy.host}:{proxy.port}"
    
    async def _health_monitor(self) -> None:
        """Background task to monitor proxy health."""        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Validate all proxies
                validation_tasks = []
                for proxy in self.proxies:
                    task = asyncio.create_task(self.validate_proxy(proxy))
                    validation_tasks.append(task)
                
                if validation_tasks:
                    await asyncio.gather(*validation_tasks, return_exceptions=True)
                
                # Log health status
                self._log_health_status()
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
    
    def _log_health_status(self) -> None:
        """Log current proxy health status."""        total_proxies = len(self.proxies)
        available_proxies = len(self._get_available_proxies())
        banned_proxies = total_proxies - available_proxies
        
        logger.info(
            f"Proxy health: {available_proxies}/{total_proxies} available, "
            f"{banned_proxies} banned"
        )
    
    def get_proxy_statistics(self) -> Dict:
        """Get comprehensive proxy statistics."""        stats = {
            'total_proxies': len(self.proxies),
            'available_proxies': len(self._get_available_proxies()),
            'proxy_details': []
        }
        
        for proxy in self.proxies:
            proxy_key = self._get_proxy_key(proxy)
            metrics = self.proxy_metrics.get(proxy_key, ProxyMetrics())
            
            proxy_stats = {
                'host': proxy.host,
                'port': proxy.port,
                'country': proxy.country,
                'success_rate': metrics.success_rate,
                'avg_response_time': metrics.average_response_time,
                'total_requests': metrics.total_requests,
                'consecutive_failures': metrics.consecutive_failures,
                'is_banned': metrics.is_banned,
                'last_used': metrics.last_used.isoformat() if metrics.last_used else None
            }
            stats['proxy_details'].append(proxy_stats)
        
        return stats
    
    def set_rotation_strategy(self, strategy: str) -> None:
        """Set proxy rotation strategy."""        valid_strategies = ['round_robin', 'random', 'performance_based']
        if strategy in valid_strategies:
            self.rotation_strategy = strategy
            logger.info(f"Proxy rotation strategy set to: {strategy}")
        else:
            logger.warning(f"Invalid rotation strategy: {strategy}")
    
    async def refresh_proxy_pool(self, new_proxies: List[ProxyInfo]) -> None:
        """Refresh the entire proxy pool."""        old_count = len(self.proxies)
        
        # Clear existing proxies
        self.proxies.clear()
        self.proxy_metrics.clear()
        
        # Add new proxies
        for proxy in new_proxies:
            self.add_proxy(proxy)
        
        logger.info(f"Refreshed proxy pool: {old_count} -> {len(self.proxies)} proxies")
    
    def get_geographic_distribution(self) -> Dict[str, int]:
        """Get geographic distribution of proxies."""        distribution = {}
        
        for proxy in self.proxies:
            country = proxy.country or 'Unknown'
            distribution[country] = distribution.get(country, 0) + 1
        
        return distribution
