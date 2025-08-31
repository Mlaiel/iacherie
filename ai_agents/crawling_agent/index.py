"""
Crawling Agent Index - Central Entry Point & API Interface

Provides centralized access to all crawling agent functionality with standardized interfaces
for content discovery, surveillance, and monitoring operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

  IMPORTANT LEGAL NOTICE:
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
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from .crawling_agent import CrawlingAgent, CrawlingAgentManager
from .web_crawler import WebCrawler, SiteMonitor
from .content_detector import ContentDetector, SimilarityScanner
from .platform_crawler import PlatformCrawler, APIHarvester
from .surveillance_engine import SurveillanceEngine, AlertSystem

logger = logging.getLogger(__name__)


@dataclass
class CrawlingServiceConfig:
    """Comprehensive configuration for crawling services"""
    max_concurrent_agents: int = 10
    default_crawl_depth: int = 3
    default_timeout: int = 30
    enable_surveillance: bool = True
    enable_real_time_monitoring: bool = True
    enable_similarity_detection: bool = True
    storage_backend: str = "redis"
    cache_ttl_hours: int = 24
    rate_limit_requests_per_minute: int = 100
    proxy_rotation_enabled: bool = True
    stealth_mode_default: bool = False
    javascript_rendering_enabled: bool = True


class CrawlingServiceInterface:
    """
    Unified interface for all crawling agent operations
    
    Provides high-level API for content discovery, monitoring, and surveillance
    with intelligent load balancing and resource management.
    """
    
    def __init__(self, config: Optional[CrawlingServiceConfig] = None):
        self.config = config or CrawlingServiceConfig()
        self.agent_manager = CrawlingAgentManager()
        self.web_crawler = WebCrawler()
        self.content_detector = ContentDetector()
        self.platform_crawler = PlatformCrawler()
        self.surveillance_engine = SurveillanceEngine()
        
        self.initialized = False
        self.service_stats = {
            'total_requests': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'content_items_discovered': 0,
            'surveillance_targets_active': 0,
            'violations_detected': 0
        }
    
    async def initialize(self) -> None:
        """Initialize all crawling service components"""
        if self.initialized:
            return
        
        try:
            # Initialize core components
            await self.agent_manager.initialize()
            await self.web_crawler.initialize()
            await self.content_detector.initialize()
            await self.platform_crawler.initialize()
            await self.surveillance_engine.initialize()
            
            # Create default agent pool
            for i in range(self.config.max_concurrent_agents):
                agent_config = {
                    'max_depth': self.config.default_crawl_depth,
                    'timeout': self.config.default_timeout,
                    'stealth_mode': self.config.stealth_mode_default,
                    'javascript_enabled': self.config.javascript_rendering_enabled
                }
                
                await self.agent_manager.create_agent(f"agent_{i}", agent_config)
            
            self.initialized = True
            logger.info("Crawling Service Interface initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Crawling Service Interface: {str(e)}")
            raise

    # Content Discovery Operations
    async def discover_content(self, 
                             urls: List[str], 
                             content_types: List[str] = None,
                             max_depth: int = None) -> Dict[str, Any]:
        """
        Discover and extract content from specified URLs
        
        Args:
            urls: List of URLs to crawl
            content_types: Types of content to extract ['text', 'image', 'video', 'audio']
            max_depth: Maximum crawling depth
            
        Returns:
            Dictionary containing discovered content and analysis
        """
        self._ensure_initialized()
        content_types = content_types or ['text']
        max_depth = max_depth or self.config.default_crawl_depth
        
        try:
            results = await self.agent_manager.distribute_bulk_request({
                'action': 'bulk_crawl',
                'data': {
                    'urls': urls,
                    'content_types': content_types,
                    'max_depth': max_depth
                }
            })
            
            self.service_stats['total_requests'] += 1
            self.service_stats['successful_operations'] += 1
            self.service_stats['content_items_discovered'] += results.get('successful_crawls', 0)
            
            return results
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Content discovery failed: {str(e)}")
            raise

    async def crawl_website(self, 
                           url: str, 
                           strategy: str = 'comprehensive',
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Comprehensive website crawling with advanced strategies
        
        Args:
            url: Target website URL
            strategy: Crawling strategy ('comprehensive', 'focused', 'stealth', 'fast')
            filters: Content filters and extraction rules
            
        Returns:
            Crawled website data and analysis
        """
        self._ensure_initialized()
        filters = filters or {}
        
        crawl_request = {
            'action': 'crawl_website',
            'data': {
                'url': url,
                'strategy': strategy,
                'filters': filters,
                'timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(crawl_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
                self.service_stats['content_items_discovered'] += result.data.get('crawled_pages', 0)
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Website crawling failed for {url}: {str(e)}")
            raise

    # Content Monitoring Operations
    async def monitor_content(self, 
                            content_fingerprint: str, 
                            platforms: List[str],
                            keywords: List[str] = None) -> Dict[str, Any]:
        """
        Monitor specific content across multiple platforms
        
        Args:
            content_fingerprint: Unique content fingerprint
            platforms: List of platforms to monitor
            keywords: Additional search keywords
            
        Returns:
            Monitoring results and potential violations
        """
        self._ensure_initialized()
        keywords = keywords or []
        
        monitoring_request = {
            'action': 'monitor_content',
            'data': {
                'content_fingerprint': content_fingerprint,
                'platforms': platforms,
                'keywords': keywords,
                'monitoring_timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(monitoring_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
                violations = result.data.get('potential_violations', [])
                self.service_stats['violations_detected'] += len(violations)
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Content monitoring failed: {str(e)}")
            raise

    async def search_similar_content(self, 
                                   reference_content: str,
                                   platforms: List[str] = None,
                                   similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        Search for content similar to reference across platforms
        
        Args:
            reference_content: Content to find similarities for
            platforms: Platforms to search on
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            Similar content matches with similarity scores
        """
        self._ensure_initialized()
        platforms = platforms or ['generic']
        
        search_request = {
            'action': 'search_similar',
            'data': {
                'content': reference_content,
                'platforms': platforms,
                'threshold': similarity_threshold,
                'search_timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(search_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Similar content search failed: {str(e)}")
            raise

    # Surveillance Operations
    async def setup_surveillance(self, 
                               user_id: str,
                               content_fingerprint: str,
                               platforms: List[str],
                               alert_settings: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Setup automated content surveillance and monitoring
        
        Args:
            user_id: User identifier for surveillance target
            content_fingerprint: Content to monitor
            platforms: Platforms to monitor on
            alert_settings: Alert configuration and thresholds
            
        Returns:
            Surveillance target configuration and status
        """
        self._ensure_initialized()
        alert_settings = alert_settings or {'threshold': 0.8, 'channels': ['email']}
        
        surveillance_request = {
            'action': 'surveillance_setup',
            'data': {
                'user_id': user_id,
                'content_fingerprint': content_fingerprint,
                'platforms': platforms,
                'alert_settings': alert_settings,
                'setup_timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(surveillance_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
                self.service_stats['surveillance_targets_active'] += 1
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Surveillance setup failed: {str(e)}")
            raise

    async def start_real_time_monitoring(self, 
                                       monitoring_config: Dict[str, Any],
                                       duration_hours: int = 24) -> Dict[str, Any]:
        """
        Start real-time content monitoring with immediate alerts
        
        Args:
            monitoring_config: Configuration for monitoring targets
            duration_hours: Duration to run monitoring
            
        Returns:
            Real-time monitoring session details
        """
        self._ensure_initialized()
        
        monitoring_request = {
            'action': 'real_time_monitor',
            'data': {
                'config': monitoring_config,
                'duration': duration_hours * 3600,  # Convert to seconds
                'start_timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(monitoring_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Real-time monitoring failed: {str(e)}")
            raise

    # Platform-Specific Operations
    async def scan_platform(self, 
                           platform: str,
                           scan_type: str = 'content_discovery',
                           filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform comprehensive platform-specific scanning
        
        Args:
            platform: Target platform name
            scan_type: Type of scan to perform
            filters: Platform-specific filters
            
        Returns:
            Platform scan results and discovered content
        """
        self._ensure_initialized()
        filters = filters or {}
        
        scan_request = {
            'action': 'platform_scan',
            'data': {
                'platforms': [platform],
                'scan_type': scan_type,
                'filters': filters,
                'scan_timestamp': datetime.now().isoformat()
            }
        }
        
        try:
            result = await self.agent_manager.distribute_request(scan_request)
            
            self.service_stats['total_requests'] += 1
            if result.get('success'):
                self.service_stats['successful_operations'] += 1
                scan_results = result.data.get('scan_results', {})
                total_found = sum(len(r.get('results', [])) for r in scan_results.values())
                self.service_stats['content_items_discovered'] += total_found
            else:
                self.service_stats['failed_operations'] += 1
                
            return result.data
            
        except Exception as e:
            self.service_stats['failed_operations'] += 1
            logger.error(f"Platform scanning failed for {platform}: {str(e)}")
            raise

    # Content Analysis Operations
    async def analyze_content_fingerprint(self, content: str, content_type: str = 'text') -> str:
        """
        Generate unique fingerprint for content
        
        Args:
            content: Content to fingerprint
            content_type: Type of content
            
        Returns:
            Unique content fingerprint
        """
        self._ensure_initialized()
        
        try:
            fingerprint = await self.content_detector.create_content_signature(content, content_type)
            return fingerprint
            
        except Exception as e:
            logger.error(f"Content fingerprinting failed: {str(e)}")
            raise

    async def calculate_content_similarity(self, 
                                         fingerprint1: str, 
                                         fingerprint2: str) -> float:
        """
        Calculate similarity between two content fingerprints
        
        Args:
            fingerprint1: First content fingerprint
            fingerprint2: Second content fingerprint
            
        Returns:
            Similarity score (0-1)
        """
        self._ensure_initialized()
        
        try:
            similarity = await self.content_detector.calculate_similarity(fingerprint1, fingerprint2)
            return similarity
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            raise

    # Service Management Operations
    def get_service_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive service statistics and metrics
        
        Returns:
            Service performance and usage statistics
        """



        return {
            'service_stats': self.service_stats,
            'agent_pool_size': len(self.agent_manager.agents),
            'active_surveillance_targets': self.service_stats['surveillance_targets_active'],
            'service_uptime': datetime.now().isoformat(),
            'configuration': {
                'max_concurrent_agents': self.config.max_concurrent_agents,
                'default_crawl_depth': self.config.default_crawl_depth,
                'surveillance_enabled': self.config.enable_surveillance,
                'real_time_monitoring': self.config.enable_real_time_monitoring
            }
        }

    def get_active_agents_status(self) -> Dict[str, Any]:
        """
        Get status of all active crawling agents
        
        Returns:
            Status information for all agents
        """
        agent_statuses = {}
        
        for agent_id, agent in self.agent_manager.agents.items():
            agent_statuses[agent_id] = {
                'status': agent.status.value if hasattr(agent.status, 'value') else str(agent.status),
                'metrics': agent.metrics.__dict__ if hasattr(agent, 'metrics') else {},
                'surveillance_targets': len(agent.surveillance_targets) if hasattr(agent, 'surveillance_targets') else 0,
                'last_activity': datetime.now().isoformat()
            }
        
        return {
            'agent_count': len(agent_statuses),
            'agents': agent_statuses,
            'total_active': len([a for a in agent_statuses.values() if a['status'] == 'active'])
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all components
        
        Returns:
            Health status of all service components
        """
        health_status = {
            'overall_status': 'healthy',
            'components': {},
            'issues': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Check agent manager
            if self.agent_manager and self.agent_manager.agents:
                health_status['components']['agent_manager'] = 'healthy'
            else:
                health_status['components']['agent_manager'] = 'warning'
                health_status['issues'].append('No active agents available')
            
            # Check web crawler
            if self.web_crawler:
                health_status['components']['web_crawler'] = 'healthy'
            else:
                health_status['components']['web_crawler'] = 'error'
                health_status['issues'].append('Web crawler not initialized')
            
            # Check content detector
            if self.content_detector:
                health_status['components']['content_detector'] = 'healthy'
            else:
                health_status['components']['content_detector'] = 'error'
                health_status['issues'].append('Content detector not initialized')
            
            # Check surveillance engine
            if self.surveillance_engine:
                health_status['components']['surveillance_engine'] = 'healthy'
            else:
                health_status['components']['surveillance_engine'] = 'error'
                health_status['issues'].append('Surveillance engine not initialized')
            
            # Determine overall status
            if health_status['issues']:
                if any('error' in status for status in health_status['components'].values()):
                    health_status['overall_status'] = 'unhealthy'
                else:
                    health_status['overall_status'] = 'degraded'
            
        except Exception as e:
            health_status['overall_status'] = 'error'
            health_status['issues'].append(f'Health check failed: {str(e)}')
        
        return health_status

    def _ensure_initialized(self) -> None:
        """Ensure service is properly initialized"""
        if not self.initialized:
            raise RuntimeError("Crawling Service Interface not initialized. Call initialize() first.")

    async def shutdown(self) -> None:
        """Gracefully shutdown all crawling service components"""
        logger.info("Shutting down Crawling Service Interface...")
        
        try:
            # Shutdown all components
            if self.agent_manager:
                await self.agent_manager.shutdown_all()
            
            if self.web_crawler:
                await self.web_crawler.shutdown()
            
            if self.content_detector:
                await self.content_detector.shutdown()
            
            if self.platform_crawler:
                await self.platform_crawler.shutdown()
            
            if self.surveillance_engine:
                await self.surveillance_engine.shutdown()
            
            self.initialized = False
            logger.info("Crawling Service Interface shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
            raise


# Convenience factory functions
def create_crawling_service(config: Optional[Dict[str, Any]] = None) -> CrawlingServiceInterface:
    """
    Factory function to create and configure crawling service
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Configured CrawlingServiceInterface instance
    """
    service_config = CrawlingServiceConfig()
    
    if config:
        for key, value in config.items():
            if hasattr(service_config, key):
                setattr(service_config, key, value)
    
    return CrawlingServiceInterface(service_config)


async def quick_content_discovery(urls: List[str], 
                                content_types: List[str] = None) -> Dict[str, Any]:
    """
    Quick content discovery utility function
    
    Args:
        urls: List of URLs to crawl
        content_types: Types of content to extract
        
    Returns:
        Discovered content results
    """
    service = create_crawling_service()
    await service.initialize()
    
    try:
        results = await service.discover_content(urls, content_types)
        return results
    finally:
        await service.shutdown()


async def quick_similarity_check(reference_content: str, 
                               search_platforms: List[str] = None) -> Dict[str, Any]:
    """
    Quick similarity checking utility function
    
    Args:
        reference_content: Content to find similarities for
        search_platforms: Platforms to search on
        
    Returns:
        Similar content matches
    """
    service = create_crawling_service()
    await service.initialize()
    
    try:
        results = await service.search_similar_content(reference_content, search_platforms)
        return results
    finally:
        await service.shutdown()


# Export main interfaces
__all__ = [
    'CrawlingServiceInterface',
    'CrawlingServiceConfig',
    'create_crawling_service',
    'quick_content_discovery',
    'quick_similarity_check'
]
