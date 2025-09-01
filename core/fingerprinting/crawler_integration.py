"""Crawler Integration for Content Protection
==========================================

Integrates the ML fingerprinting pipeline with existing crawler infrastructure
to provide comprehensive content protection across 35+ platforms.

Features:
- Seamless integration with existing crawlers
- Real-time content processing
- Automated violation detection and response
- Performance monitoring and optimization
- Scalable batch processing

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import importlib
import sys
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

# Import our new ML production modules
from .ml_production import MLFingerprintingPipeline, FingerprintResult
from .realtime_monitoring import RealTimeMonitoringSystem, ViolationAlert

logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
    """Configuration for crawler integration."""
    name: str
    module_path: str
    enabled: bool = True
    batch_size: int = 10
    processing_interval: float = 60.0
    priority: int = 1  # 1=high, 2=medium, 3=low
    fingerprint_types: List[str] = field(default_factory=lambda: ["audio", "video", "image"])

@dataclass
class ProcessingTask:
    """Content processing task."""
    task_id: str
    platform: str
    content_type: str
    content_data: Any
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class CrawlerIntegrationManager:
    """Manages integration between crawlers and fingerprinting."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.crawler_configs = self._load_crawler_configs()
        self.fingerprint_pipeline = None
        self.monitoring_system = None
        self.active_crawlers = {}
        self.task_queue = asyncio.Queue()
        self.processing_pool = None
        self.is_running = False
        self.stats = {
            "total_processed": 0,
            "successful_fingerprints": 0,
            "violations_detected": 0,
            "crawlers_active": 0,
            "average_processing_time": 0.0
        }
        
    def _load_crawler_configs(self) -> List[CrawlerConfig]:
        """Load crawler configurations."""
        configs = []
        
        # Define crawler modules (based on existing crawler files)
        crawler_definitions = [
            {"name": "youtube", "module_path": "crawlers.youtube_crawler", "priority": 1},
            {"name": "instagram", "module_path": "crawlers.instagram_crawler", "priority": 1},
            {"name": "tiktok", "module_path": "crawlers.tiktok_crawler", "priority": 1},
            {"name": "facebook", "module_path": "crawlers.facebook_crawler", "priority": 1},
            {"name": "twitter", "module_path": "crawlers.twitter_crawler", "priority": 1},
            {"name": "spotify", "module_path": "crawlers.spotify_crawler", "priority": 2},
            {"name": "soundcloud", "module_path": "crawlers.soundcloud_crawler", "priority": 2},
            {"name": "apple_music", "module_path": "crawlers.apple_music_crawler", "priority": 2},
            {"name": "youtube_music", "module_path": "crawlers.youtube_music_crawler", "priority": 2},
            {"name": "discord", "module_path": "crawlers.discord_crawler", "priority": 2},
            {"name": "reddit", "module_path": "crawlers.reddit_crawler", "priority": 2},
            {"name": "linkedin", "module_path": "crawlers.linkedin_crawler", "priority": 2},
            {"name": "pinterest", "module_path": "crawlers.pinterest_crawler", "priority": 2},
            {"name": "snapchat", "module_path": "crawlers.snapchat_crawler", "priority": 3},
            {"name": "twitch", "module_path": "crawlers.twitch_crawler", "priority": 2},
            {"name": "vimeo", "module_path": "crawlers.vimeo_crawler", "priority": 3},
            {"name": "dailymotion", "module_path": "crawlers.dailymotion_crawler", "priority": 3},
            {"name": "rumble", "module_path": "crawlers.rumble_crawler", "priority": 3},
            {"name": "kick", "module_path": "crawlers.kick_crawler", "priority": 3},
            {"name": "telegram", "module_path": "crawlers.telegram_crawler", "priority": 2},
            {"name": "whatsapp", "module_path": "crawlers.whatsapp_crawler", "priority": 3},
            {"name": "threads", "module_path": "crawlers.threads_crawler", "priority": 2},
            {"name": "mastodon", "module_path": "crawlers.mastodon_crawler", "priority": 3},
            {"name": "patreon", "module_path": "crawlers.patreon_crawler", "priority": 2},
            {"name": "onlyfans", "module_path": "crawlers.onlyfans_crawler", "priority": 3},
            {"name": "substack", "module_path": "crawlers.substack_crawler", "priority": 3},
            {"name": "medium", "module_path": "crawlers.medium_crawler", "priority": 3},
            {"name": "bandcamp", "module_path": "crawlers.bandcamp_crawler", "priority": 3},
            {"name": "mixcloud", "module_path": "crawlers.mixcloud_crawler", "priority": 3},
            {"name": "deezer", "module_path": "crawlers.deezer_crawler", "priority": 3},
            {"name": "amazon_music", "module_path": "crawlers.amazon_music_crawler", "priority": 3},
            {"name": "clubhouse", "module_path": "crawlers.clubhouse_crawler", "priority": 3},
            {"name": "bereal", "module_path": "crawlers.bereal_crawler", "priority": 3},
            {"name": "twine", "module_path": "crawlers.twine_crawler", "priority": 3},
        ]
        
        # Create configurations
        for crawler_def in crawler_definitions:
            config = CrawlerConfig(
                name=crawler_def["name"],
                module_path=crawler_def["module_path"],
                enabled=self.config.get("enabled_platforms", {}).get(crawler_def["name"], True),
                priority=crawler_def["priority"],
                batch_size=self.config.get("batch_size", 10),
                processing_interval=self.config.get("processing_interval", 60.0)
            )
            configs.append(config)
        
        logger.info(f"Loaded {len(configs)} crawler configurations")
        return configs
    
    async def initialize(self):
        """Initialize the integration system."""
        logger.info("Initializing crawler integration system...")
        
        # Initialize ML fingerprinting pipeline
        pipeline_config = self.config.get("fingerprinting", {})
        self.fingerprint_pipeline = MLFingerprintingPipeline(pipeline_config)
        
        # Initialize monitoring system
        monitoring_config = self.config.get("monitoring", {})
        monitoring_config["platforms"] = [
            {"name": cfg.name, "scan_interval": cfg.processing_interval}
            for cfg in self.crawler_configs if cfg.enabled
        ]
        
        self.monitoring_system = RealTimeMonitoringSystem(monitoring_config)
        await self.monitoring_system.initialize(self.fingerprint_pipeline)
        
        # Initialize processing pool
        max_workers = self.config.get("max_workers", multiprocessing.cpu_count())
        self.processing_pool = ThreadPoolExecutor(max_workers=max_workers)
        
        # Load and initialize crawlers
        await self._initialize_crawlers()
        
        logger.info("Crawler integration system initialized successfully")
    
    async def _initialize_crawlers(self):
        """Initialize active crawlers."""
        for crawler_config in self.crawler_configs:
            if not crawler_config.enabled:
                continue
                
            try:
                crawler_instance = await self._load_crawler(crawler_config)
                if crawler_instance:
                    self.active_crawlers[crawler_config.name] = {
                        "instance": crawler_instance,
                        "config": crawler_config,
                        "last_run": None,
                        "content_processed": 0
                    }
                    logger.info(f"Initialized crawler: {crawler_config.name}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize crawler {crawler_config.name}: {e}")
    
    async def _load_crawler(self, config: CrawlerConfig):
        """Load individual crawler module."""
        try:
            # Dynamically import crawler module
            module = importlib.import_module(config.module_path)
            
            # Look for common crawler class names
            crawler_class_names = [
                f"{config.name.title()}Crawler",
                f"{config.name.upper()}Crawler", 
                f"{config.name.capitalize()}Crawler",
                "Crawler"
            ]
            
            crawler_class = None
            for class_name in crawler_class_names:
                if hasattr(module, class_name):
                    crawler_class = getattr(module, class_name)
                    break
            
            if crawler_class:
                # Initialize crawler with appropriate config
                crawler_instance = crawler_class(self.config.get("crawler_settings", {}))
                return crawler_instance
            else:
                logger.warning(f"No suitable crawler class found in {config.module_path}")
                return None
                
        except ImportError as e:
            logger.error(f"Could not import crawler module {config.module_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading crawler {config.name}: {e}")
            return None
    
    async def start_integration(self):
        """Start the integrated system."""
        if self.is_running:
            logger.warning("Integration already running")
            return
        
        self.is_running = True
        logger.info("🚀 Starting integrated content protection system...")
        
        # Start monitoring system
        monitoring_task = asyncio.create_task(self.monitoring_system.start_monitoring())
        
        # Start crawler coordination
        crawler_task = asyncio.create_task(self._crawler_coordination_loop())
        
        # Start content processing
        processing_task = asyncio.create_task(self._content_processing_loop())
        
        # Start metrics collection
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        
        # Wait for all tasks
        await asyncio.gather(
            monitoring_task,
            crawler_task, 
            processing_task,
            metrics_task,
            return_exceptions=True
        )
    
    async def stop_integration(self):
        """Stop the integrated system."""
        self.is_running = False
        logger.info("Stopping integrated content protection system...")
        
        # Stop monitoring
        if self.monitoring_system:
            await self.monitoring_system.stop_monitoring()
        
        # Shutdown processing pool
        if self.processing_pool:
            self.processing_pool.shutdown(wait=True)
    
    async def _crawler_coordination_loop(self):
        """Coordinate crawler activities."""
        while self.is_running:
            try:
                # Process crawlers by priority
                priority_groups = {}
                for name, crawler_info in self.active_crawlers.items():
                    priority = crawler_info["config"].priority
                    if priority not in priority_groups:
                        priority_groups[priority] = []
                    priority_groups[priority].append((name, crawler_info))
                
                # Execute by priority (1=highest)
                for priority in sorted(priority_groups.keys()):
                    tasks = []
                    for name, crawler_info in priority_groups[priority]:
                        task = asyncio.create_task(
                            self._run_crawler_cycle(name, crawler_info)
                        )
                        tasks.append(task)
                    
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next coordination cycle
                await asyncio.sleep(30)  # 30 second coordination cycle
                
            except Exception as e:
                logger.error(f"Error in crawler coordination loop: {e}")
                await asyncio.sleep(60)
    
    async def _run_crawler_cycle(self, name: str, crawler_info: Dict[str, Any]):
        """Run single crawler cycle."""
        try:
            config = crawler_info["config"]
            instance = crawler_info["instance"]
            
            # Check if it's time to run this crawler
            last_run = crawler_info["last_run"]
            if last_run and (datetime.now() - last_run).total_seconds() < config.processing_interval:
                return
            
            # Fetch content from crawler
            content_batch = await self._fetch_crawler_content(instance, config.batch_size)
            
            # Queue content for processing
            for content in content_batch:
                task = ProcessingTask(
                    task_id=f"{name}_{datetime.now().timestamp()}",
                    platform=name,
                    content_type=content.get("type", "unknown"),
                    content_data=content,
                    priority=config.priority,
                    metadata={"crawler": name}
                )
                await self.task_queue.put(task)
            
            # Update crawler info
            crawler_info["last_run"] = datetime.now()
            crawler_info["content_processed"] += len(content_batch)
            
            if content_batch:
                logger.debug(f"Crawler {name} queued {len(content_batch)} items for processing")
            
        except Exception as e:
            logger.error(f"Error in crawler cycle for {name}: {e}")
    
    async def _fetch_crawler_content(self, crawler_instance, batch_size: int) -> List[Dict[str, Any]]:
        """Fetch content from crawler instance."""
        try:
            # Mock content fetching (in production would call actual crawler methods)
            # This simulates the interface that crawlers should implement
            
            if hasattr(crawler_instance, 'fetch_recent_content'):
                content = await crawler_instance.fetch_recent_content(limit=batch_size)
            elif hasattr(crawler_instance, 'get_content_batch'):
                content = await crawler_instance.get_content_batch(size=batch_size)
            else:
                # Fallback: simulate content
                content = []
                for i in range(min(3, batch_size)):  # Max 3 items for simulation
                    content.append({
                        "id": f"mock_content_{datetime.now().timestamp()}_{i}",
                        "type": ["audio", "video", "image"][i % 3],
                        "url": f"https://example.com/content/{i}",
                        "metadata": {"simulated": True}
                    })
            
            return content or []
            
        except Exception as e:
            logger.error(f"Error fetching content from crawler: {e}")
            return []
    
    async def _content_processing_loop(self):
        """Main content processing loop."""
        while self.is_running:
            try:
                # Get tasks from queue (with timeout to allow checking is_running)
                tasks_to_process = []
                
                # Collect batch of tasks
                batch_size = self.config.get("processing_batch_size", 5)
                for _ in range(batch_size):
                    try:
                        task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                        tasks_to_process.append(task)
                    except asyncio.TimeoutError:
                        break
                
                if tasks_to_process:
                    await self._process_task_batch(tasks_to_process)
                
            except Exception as e:
                logger.error(f"Error in content processing loop: {e}")
                await asyncio.sleep(5)
    
    async def _process_task_batch(self, tasks: List[ProcessingTask]):
        """Process batch of content tasks."""
        processing_results = []
        
        for task in tasks:
            try:
                start_time = datetime.now()
                
                # Convert task to content format expected by fingerprinting pipeline
                content = {
                    "id": task.task_id,
                    "type": task.content_type,
                    "data": task.content_data,
                    "platform": task.platform,
                    "metadata": task.metadata
                }
                
                # Process through fingerprinting pipeline
                result = await self.fingerprint_pipeline._process_single_content(content)
                
                if result:
                    processing_time = (datetime.now() - start_time).total_seconds()
                    result["processing_time"] = processing_time
                    processing_results.append(result)
                    
                    # Update stats
                    self.stats["total_processed"] += 1
                    self.stats["successful_fingerprints"] += 1
                    
                    # Update average processing time
                    total_time = self.stats["average_processing_time"] * (self.stats["total_processed"] - 1)
                    self.stats["average_processing_time"] = (total_time + processing_time) / self.stats["total_processed"]
                
            except Exception as e:
                logger.error(f"Error processing task {task.task_id}: {e}")
        
        if processing_results:
            logger.debug(f"Successfully processed {len(processing_results)} content items")
    
    async def _metrics_collection_loop(self):
        """Collect and update system metrics."""
        while self.is_running:
            try:
                # Update active crawlers count
                self.stats["crawlers_active"] = len([
                    c for c in self.active_crawlers.values() 
                    if c["last_run"] and (datetime.now() - c["last_run"]).total_seconds() < 300  # Active in last 5 min
                ])
                
                # Get monitoring metrics
                if self.monitoring_system:
                    monitoring_status = self.monitoring_system.get_monitoring_status()
                    self.stats["violations_detected"] = monitoring_status["metrics"]["violations_detected"]
                
                # Get fingerprinting metrics
                if self.fingerprint_pipeline:
                    pipeline_metrics = self.fingerprint_pipeline.get_production_metrics()
                    # Merge relevant metrics
                    
                await asyncio.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status."""
        return {
            "system_status": {
                "is_running": self.is_running,
                "crawlers_configured": len(self.crawler_configs),
                "crawlers_active": len(self.active_crawlers),
                "crawlers_enabled": len([c for c in self.crawler_configs if c.enabled])
            },
            "processing_stats": self.stats,
            "crawler_details": {
                name: {
                    "enabled": info["config"].enabled,
                    "priority": info["config"].priority,
                    "last_run": info["last_run"].isoformat() if info["last_run"] else None,
                    "content_processed": info["content_processed"]
                }
                for name, info in self.active_crawlers.items()
            },
            "monitoring_status": (
                self.monitoring_system.get_monitoring_status() 
                if self.monitoring_system else None
            ),
            "fingerprinting_metrics": (
                self.fingerprint_pipeline.get_production_metrics()
                if self.fingerprint_pipeline else None
            )
        }

# Main integration orchestrator
class ContentProtectionOrchestrator:
    """Main orchestrator for complete content protection system."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.integration_manager = None
        self.performance_monitor = None
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load system configuration."""
        default_config = {
            "fingerprinting": {
                "enable_audio": True,
                "enable_video": True,
                "enable_image": True,
                "batch_size": 10
            },
            "monitoring": {
                "similarity_threshold": 0.85,
                "auto_takedown": True,
                "redis_host": "localhost",
                "redis_port": 6379
            },
            "crawler_settings": {
                "rate_limit": 10,
                "timeout": 30,
                "retry_attempts": 3
            },
            "enabled_platforms": {
                # Enable high-priority platforms by default
                "youtube": True,
                "instagram": True, 
                "tiktok": True,
                "facebook": True,
                "twitter": True,
                "spotify": True,
                "soundcloud": True
            },
            "processing_batch_size": 5,
            "max_workers": multiprocessing.cpu_count()
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.error(f"Error loading config from {config_path}: {e}")
        
        return default_config
    
    async def start_protection_system(self):
        """Start the complete content protection system."""
        logger.info("🛡️  Starting Ainflue Content Protection System")
        logger.info("================================================")
        
        # Initialize integration manager
        self.integration_manager = CrawlerIntegrationManager(self.config)
        await self.integration_manager.initialize()
        
        logger.info(f"✅ Initialized {len(self.integration_manager.active_crawlers)} active crawlers")
        logger.info(f"🔍 Monitoring enabled for {len(self.integration_manager.crawler_configs)} platforms")
        logger.info(f"🤖 ML fingerprinting pipeline ready")
        logger.info(f"⚡ Real-time violation detection active")
        
        # Start the integrated system
        await self.integration_manager.start_integration()
    
    async def stop_protection_system(self):
        """Stop the content protection system."""
        logger.info("Stopping content protection system...")
        
        if self.integration_manager:
            await self.integration_manager.stop_integration()
        
        logger.info("✅ Content protection system stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status."""
        if not self.integration_manager:
            return {"status": "not_initialized"}
        
        return self.integration_manager.get_integration_status()

# Demo function
async def demo_complete_system():
    """Demonstrate the complete integrated system."""
    print("🚀 Ainflue - Complete Content Protection System Demo")
    print("====================================================")
    
    # Initialize orchestrator
    orchestrator = ContentProtectionOrchestrator()
    
    try:
        # Start the system (run for limited time in demo)
        system_task = asyncio.create_task(orchestrator.start_protection_system())
        
        # Let it run for demo period
        await asyncio.wait_for(system_task, timeout=45)  # 45 second demo
        
    except asyncio.TimeoutError:
        print("\n⏰ Demo completed - stopping system...")
        await orchestrator.stop_protection_system()
    
    # Show final status
    status = orchestrator.get_system_status()
    print(f"\n📊 Final System Status:")
    print(f"   Crawlers Active: {status['system_status']['crawlers_active']}")
    print(f"   Content Processed: {status['processing_stats']['total_processed']}")
    print(f"   Fingerprints Generated: {status['processing_stats']['successful_fingerprints']}")
    print(f"   Violations Detected: {status['processing_stats']['violations_detected']}")
    print(f"   Average Processing Time: {status['processing_stats']['average_processing_time']:.2f}s")

if __name__ == "__main__":
    asyncio.run(demo_complete_system())