"""Proxy Scraper - IA-Influencer-Agent
===================================

Advanced proxy management and rotation scraper.
Handles proxy pools, rotation, and failover mechanisms.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import time
from urllib.parse import urlparse

@dataclass
class ProxyInfo:
    """
Proxy server information."""
    host: str
    port: int
    protocol: str = 'http'  # http, https, socks4, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    provider: Optional[str] = None
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    response_time: float = 0.0
    is_working: bool = True
    consecutive_failures: int = 0

class ProxyScraper:
    """
    Advanced proxy management scraper.
    
    Features:
    - Proxy pool management
    - Automatic rotation
    - Health monitoring
    - Performance tracking
    - Failover mechanisms
    - Geographic distribution
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.proxy_pool: List[ProxyInfo] = []
        self.current_proxy_index = 0
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Statistics
        self.stats = {
            'total_proxies': 0,
            'working_proxies': 0,
            'requests_made': 0,
            'proxy_rotations': 0,
            'failures': 0
        }
        
    async def __aenter__(self):
        """
Async context manager entry."""
        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        if self.session:
            await self.session.close()
            
    async def _initialize_session(self):
        """
Initialize HTTP session."""
        connector = aiohttp.TCPConnector(
            limit=50,
            limit_per_host=10,
            ttl_dns_cache=300
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
    def add_proxy(self, proxy: ProxyInfo):
        """
Add proxy to pool."""
        self.proxy_pool.append(proxy)
        self.stats['total_proxies'] = len(self.proxy_pool)
        self.logger.info(f"Added proxy: {proxy.host}:{proxy.port}")
        
    def add_proxies_from_list(self, proxy_list: List[str]):
        """Add proxies from string list (host:port format)."""
        for proxy_str in proxy_list:
            try:
                if ':' in proxy_str:
                    host, port = proxy_str.split(':')
                    proxy = ProxyInfo(
                        host=host.strip(),
                        port=int(port.strip())
                    )
                    self.add_proxy(proxy)
            except Exception as e:
                self.logger.error(f"Failed to parse proxy {proxy_str}: {e}")
                
    async def test_proxy(self, proxy: ProxyInfo) -> bool:
        """Test if proxy is working."""
        proxy_url = self._format_proxy_url(proxy)
        test_url = "http://httpbin.org/ip"
        
        try:
            start_time = time.time()
            
            async with self.session.get(
                test_url,
                proxy=proxy_url,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    proxy.response_time = response_time
                    proxy.is_working = True
                    proxy.consecutive_failures = 0
                    proxy.last_used = datetime.now()
                    
                    # Update success rate
                    proxy.success_rate = min(1.0, proxy.success_rate + 0.1)
                    
                    self.logger.debug(f"Proxy {proxy.host}:{proxy.port} is working")
                    return True
                    
        except Exception as e:
            self.logger.debug(f"Proxy {proxy.host}:{proxy.port} failed: {e}")
            
        proxy.is_working = False
        proxy.consecutive_failures += 1
        proxy.success_rate = max(0.0, proxy.success_rate - 0.2)
        
        return False
        
    async def test_all_proxies(self):
        """Test all proxies in pool."""
        self.logger.info("Testing all proxies...")
        
        tasks = [self.test_proxy(proxy) for proxy in self.proxy_pool]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        working_count = sum(1 for result in results if result is True)
        self.stats['working_proxies'] = working_count
        
        self.logger.info(f"Tested {len(self.proxy_pool)} proxies, {working_count} are working")
        
    def get_next_proxy(self) -> Optional[ProxyInfo]:
        """Get next proxy using rotation strategy."""
        if not self.proxy_pool:
            return None
            
        # Filter working proxies
        working_proxies = [p for p in self.proxy_pool if p.is_working]
        
        if not working_proxies:
            self.logger.warning("No working proxies available")
            return None
            
        # Round-robin rotation
        proxy = working_proxies[self.current_proxy_index % len(working_proxies)]
        self.current_proxy_index += 1
        self.stats['proxy_rotations'] += 1
        
        return proxy
        
    def get_best_proxy(self) -> Optional[ProxyInfo]:
        """Get proxy with best performance."""
        working_proxies = [p for p in self.proxy_pool if p.is_working]
        
        if not working_proxies:
            return None
            
        # Sort by success rate and response time
        best_proxy = min(
            working_proxies,
            key=lambda p: (1 - p.success_rate, p.response_time)
        )
        
        return best_proxy
        
    def get_random_proxy(self) -> Optional[ProxyInfo]:
        """
Get random working proxy."""
        working_proxies = [p for p in self.proxy_pool if p.is_working]
        
        if not working_proxies:
            return None
            
        return random.choice(working_proxies)
        
    def _format_proxy_url(self, proxy: ProxyInfo) -> str:
        """
Format proxy URL for aiohttp."""
        url = f"{proxy.protocol}://"
        
        if proxy.username and proxy.password:
            url += f"{proxy.username}:{proxy.password}@"
            
        url += f"{proxy.host}:{proxy.port}"
        return url
        
    async def make_request_with_proxy(self, url: str, proxy: Optional[ProxyInfo] = None,
                                    **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request using proxy."""
        if not proxy:
            proxy = self.get_next_proxy()
            
        if not proxy:
            raise Exception("No working proxies available")
            
        proxy_url = self._format_proxy_url(proxy)
        
        try:
            self.stats['requests_made'] += 1
            
            async with self.session.get(url, proxy=proxy_url, **kwargs) as response:
                # Update proxy statistics
                proxy.last_used = datetime.now()
                proxy.success_rate = min(1.0, proxy.success_rate + 0.05)
                
                return response
                
        except Exception as e:
            self.stats['failures'] += 1
            proxy.consecutive_failures += 1
            proxy.success_rate = max(0.0, proxy.success_rate - 0.1)
            
            # Mark proxy as not working if too many consecutive failures
            if proxy.consecutive_failures >= 3:
                proxy.is_working = False
                self.logger.warning(f"Marking proxy {proxy.host}:{proxy.port} as not working")
                
            raise
            
    def remove_dead_proxies(self):
        """Remove proxies that are consistently failing."""
        initial_count = len(self.proxy_pool)
        
        self.proxy_pool = [
            proxy for proxy in self.proxy_pool
            if proxy.success_rate > 0.1 or proxy.consecutive_failures < 5
        ]
        
        removed_count = initial_count - len(self.proxy_pool)
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} dead proxies")
            self.stats['total_proxies'] = len(self.proxy_pool)
            
    def get_proxy_stats(self) -> Dict[str, Any]:
        """Get proxy pool statistics."""
        if not self.proxy_pool:
            return {}
            
        working_proxies = [p for p in self.proxy_pool if p.is_working]
        
        return {
            'total_proxies': len(self.proxy_pool),
            'working_proxies': len(working_proxies),
            'success_rate': sum(p.success_rate for p in self.proxy_pool) / len(self.proxy_pool),
            'average_response_time': sum(p.response_time for p in working_proxies) / len(working_proxies) if working_proxies else 0,
            'countries': list(set(p.country for p in self.proxy_pool if p.country)),
            'providers': list(set(p.provider for p in self.proxy_pool if p.provider)),
            **self.stats
        }
        
    def export_working_proxies(self) -> List[str]:
        """
Export working proxies as string list."""
        working_proxies = [p for p in self.proxy_pool if p.is_working]
        return [f"{p.host}:{p.port}" for p in working_proxies]
