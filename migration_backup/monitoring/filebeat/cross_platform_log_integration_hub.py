#!/usr/bin/env python3
"""
Cross-Platform Log Integration Hub - Creator Economy Enterprise
=============================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Set, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from pathlib import Path
import redis.asyncio as redis
import aiohttp
from urllib.parse import urlparse
import hashlib


class PlatformType(Enum):
    """Supported platform types"""
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    TWITCH = "twitch"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    PINTEREST = "pinterest"
    SNAPCHAT = "snapchat"
    IA CHÉRIES = "ainflue"
    CUSTOM = "custom"


class LogEventType(Enum):
    """Types of cross-platform log events"""
    CONTENT_UPLOAD = "content_upload"
    ENGAGEMENT_UPDATE = "engagement_update"
    ANALYTICS_SYNC = "analytics_sync"
    MONETIZATION_EVENT = "monetization_event"
    COLLABORATION_EVENT = "collaboration_event"
    AUDIENCE_UPDATE = "audience_update"
    PERFORMANCE_METRICS = "performance_metrics"
    API_CALL = "api_call"
    ERROR_EVENT = "error_event"
    SYNC_STATUS = "sync_status"


@dataclass
class PlatformConfig:
    """Configuration for platform integration"""
    platform: PlatformType
    api_endpoint: str
    auth_type: str = "bearer"
    rate_limit: int = 100  # requests per minute
    timeout: int = 30
    retry_attempts: int = 3
    batch_size: int = 50
    sync_interval: int = 300  # seconds
    enabled: bool = True
    webhook_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "platform": self.platform.value,
            "api_endpoint": self.api_endpoint,
            "auth_type": self.auth_type,
            "rate_limit": self.rate_limit,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "batch_size": self.batch_size,
            "sync_interval": self.sync_interval,
            "enabled": self.enabled,
            "webhook_url": self.webhook_url,
            "headers": self.headers
        }


@dataclass
class CrossPlatformLogEvent:
    """Cross-platform log event data structure"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    platform: PlatformType = PlatformType.IA CHÉRIES
    event_type: LogEventType = LogEventType.ANALYTICS_SYNC
    timestamp: datetime = field(default_factory=datetime.utcnow)
    content_id: Optional[str] = None
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Event data
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Processing info
    processed: bool = False
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "event_id": self.event_id,
            "creator_id": self.creator_id,
            "platform": self.platform.value,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "content_id": self.content_id,
            "correlation_id": self.correlation_id,
            "session_id": self.session_id,
            "data": self.data,
            "metadata": self.metadata,
            "processed": self.processed,
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }


class PlatformAdapter:
    """Base adapter for platform integration"""
    
    def __init__(self, config: PlatformConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{config.platform.value}")
        self._session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_remaining = config.rate_limit
        self._last_request_time = datetime.utcnow()
        
    async def initialize(self) -> bool:
        """Initialize platform adapter"""
        try:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                headers=self.config.headers
            )
            return await self.test_connection()
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize {self.config.platform.value}: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test platform connection"""
        try:
            if not self._session:
                return False
                
            async with self._session.get(self.config.api_endpoint) as response:
                return response.status < 500
        except Exception as e:
            self.logger.warning(f"⚠️ Connection test failed for {self.config.platform.value}: {e}")
            return False
    
    async def send_log_data(self, events: List[CrossPlatformLogEvent]) -> bool:
        """Send log data to platform"""
        try:
            if not self.config.enabled or not self._session:
                return False
            
            # Respect rate limits
            await self._check_rate_limit()
            
            # Prepare payload
            payload = {
                "events": [event.to_dict() for event in events],
                "timestamp": datetime.utcnow().isoformat(),
                "platform": self.config.platform.value
            }
            
            # Send data
            async with self._session.post(
                self.config.api_endpoint,
                json=payload,
                headers=self._get_auth_headers()
            ) as response:
                if response.status == 200:
                    self.logger.info(f"✅ Sent {len(events)} events to {self.config.platform.value}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to send events to {self.config.platform.value}: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Error sending log data to {self.config.platform.value}: {e}")
            return False
    
    async def _check_rate_limit(self):
        """Check and enforce rate limits"""
        current_time = datetime.utcnow()
        time_diff = (current_time - self._last_request_time).total_seconds()
        
        if time_diff < 60:  # Within 1 minute
            if self._rate_limit_remaining <= 0:
                sleep_time = 60 - time_diff
                self.logger.info(f"⏳ Rate limit reached for {self.config.platform.value}, sleeping {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
                self._rate_limit_remaining = self.config.rate_limit
        else:
            self._rate_limit_remaining = self.config.rate_limit
        
        self._rate_limit_remaining -= 1
        self._last_request_time = current_time
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {}
        
        if self.config.auth_type == "bearer" and self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        elif self.config.auth_type == "api_key" and self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        
        return headers
    
    async def receive_webhook(self, webhook_data: Dict[str, Any]) -> List[CrossPlatformLogEvent]:
        """Process incoming webhook data"""
        try:
            events = []
            
            # Parse webhook data into events
            if "events" in webhook_data:
                for event_data in webhook_data["events"]:
                    event = self._parse_webhook_event(event_data)
                    if event:
                        events.append(event)
            
            return events
            
        except Exception as e:
            self.logger.error(f"❌ Error processing webhook from {self.config.platform.value}: {e}")
            return []
    
    def _parse_webhook_event(self, event_data: Dict[str, Any]) -> Optional[CrossPlatformLogEvent]:
        """Parse webhook event data"""
        try:
            # Basic event parsing - platform-specific implementations should override
            event_type_str = event_data.get("type", "analytics_sync")
            try:
                event_type = LogEventType(event_type_str)
            except ValueError:
                event_type = LogEventType.ANALYTICS_SYNC
            
            return CrossPlatformLogEvent(
                creator_id=event_data.get("creator_id", ""),
                platform=self.config.platform,
                event_type=event_type,
                content_id=event_data.get("content_id"),
                data=event_data.get("data", {}),
                metadata=event_data.get("metadata", {})
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error parsing webhook event: {e}")
            return None
    
    async def shutdown(self):
        """Shutdown adapter"""
        if self._session:
            await self._session.close()


class CrossPlatformLogIntegrationHub:
    """
    Hub intégration logs cross-platform enterprise
    
    Features:
    - Cross-platform log integration Creator Economy
    - Multi-platform Creator log aggregation
    - Platform-specific Creator log processing
    - Cross-platform Creator log correlation
    - Creator platform log optimization
    - Cross-platform Creator log intelligence
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = self._setup_logging()
        
        # Redis connection for caching
        self._redis_client: Optional[redis.Redis] = None
        
        # Platform adapters
        self._adapters: Dict[PlatformType, PlatformAdapter] = {}
        self._platform_configs: Dict[PlatformType, PlatformConfig] = {}
        
        # Event processing
        self._event_queue: List[CrossPlatformLogEvent] = []
        self._processed_events: Set[str] = set()
        self._correlation_cache: Dict[str, List[str]] = {}
        
        # Integration metrics
        self._integration_metrics = {
            "events_processed": 0,
            "platforms_connected": 0,
            "correlations_found": 0,
            "sync_operations": 0,
            "errors_encountered": 0,
            "webhooks_received": 0,
            "api_calls_made": 0
        }
        
        # Processing rules
        self._processing_rules = {
            "max_queue_size": 10000,
            "batch_processing_size": 100,
            "correlation_window": 3600,  # 1 hour
            "retry_max_attempts": 3,
            "sync_timeout": 300,  # 5 minutes
            "webhook_validation": True
        }
        
        # Initialize components
        self._initialized = False
        self._running = False
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for integration hub"""
        logger = logging.getLogger(f"{__name__}.CrossPlatformLogIntegrationHub")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def initialize(self) -> bool:
        """Initialize cross-platform integration hub"""
        try:
            self.logger.info("🎯 Initializing Cross-Platform Log Integration Hub...")
            
            # Initialize Redis connection
            await self._initialize_redis()
            
            # Load platform configurations
            await self._load_platform_configurations()
            
            # Initialize platform adapters
            await self._initialize_platform_adapters()
            
            # Load cached data
            await self._load_cached_data()
            
            # Validate configuration
            self._validate_configuration()
            
            self._initialized = True
            self.logger.info("✅ Cross-Platform Log Integration Hub initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize integration hub: {e}")
            return False
    
    async def _initialize_redis(self):
        """Initialize Redis connection for caching"""
        try:
            redis_config = self.config.get("redis", {})
            self._redis_client = redis.Redis(
                host=redis_config.get("host", "localhost"),
                port=redis_config.get("port", 6379),
                decode_responses=True
            )
            await self._redis_client.ping()
            self.logger.info("✅ Redis connection established")
        except Exception as e:
            self.logger.warning(f"⚠️ Redis connection failed: {e}")
            self._redis_client = None
    
    async def _load_platform_configurations(self):
        """Load platform configurations"""
        try:
            platforms_config = self.config.get("platforms", {})
            
            # Default platform configurations
            default_configs = {
                PlatformType.YOUTUBE: PlatformConfig(
                    platform=PlatformType.YOUTUBE,
                    api_endpoint="https://www.googleapis.com/youtube/v3",
                    rate_limit=100,
                    timeout=30
                ),
                PlatformType.TIKTOK: PlatformConfig(
                    platform=PlatformType.TIKTOK,
                    api_endpoint="https://open-api.tiktok.com",
                    rate_limit=60,
                    timeout=30
                ),
                PlatformType.INSTAGRAM: PlatformConfig(
                    platform=PlatformType.INSTAGRAM,
                    api_endpoint="https://graph.instagram.com",
                    rate_limit=200,
                    timeout=30
                ),
                PlatformType.TWITCH: PlatformConfig(
                    platform=PlatformType.TWITCH,
                    api_endpoint="https://api.twitch.tv/helix",
                    rate_limit=800,
                    timeout=30
                ),
                PlatformType.IA CHÉRIES: PlatformConfig(
                    platform=PlatformType.IA CHÉRIES,
                    api_endpoint=platforms_config.get("ainflue", {}).get("api_endpoint", "http://localhost:8000/api"),
                    rate_limit=1000,
                    timeout=10
                )
            }
            
            # Override with user configurations
            for platform_str, platform_config in platforms_config.items():
                try:
                    platform_type = PlatformType(platform_str)
                    if platform_type in default_configs:
                        config = default_configs[platform_type]
                        
                        # Update configuration fields
                        for key, value in platform_config.items():
                            if hasattr(config, key):
                                setattr(config, key, value)
                        
                        self._platform_configs[platform_type] = config
                    
                except ValueError:
                    self.logger.warning(f"⚠️ Unknown platform: {platform_str}")
            
            # Use defaults for missing configurations
            for platform_type, config in default_configs.items():
                if platform_type not in self._platform_configs:
                    self._platform_configs[platform_type] = config
            
            self.logger.info(f"📋 Loaded {len(self._platform_configs)} platform configurations")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading platform configurations: {e}")
    
    async def _initialize_platform_adapters(self):
        """Initialize platform adapters"""
        try:
            for platform_type, config in self._platform_configs.items():
                if config.enabled:
                    adapter = PlatformAdapter(config)
                    success = await adapter.initialize()
                    
                    if success:
                        self._adapters[platform_type] = adapter
                        self._integration_metrics["platforms_connected"] += 1
                        self.logger.info(f"✅ {platform_type.value} adapter initialized")
                    else:
                        self.logger.warning(f"⚠️ Failed to initialize {platform_type.value} adapter")
            
            self.logger.info(f"🔗 Connected to {len(self._adapters)} platforms")
            
        except Exception as e:
            self.logger.error(f"❌ Error initializing platform adapters: {e}")
    
    async def _load_cached_data(self):
        """Load cached integration data"""
        if not self._redis_client:
            return
            
        try:
            # Load processed events cache
            cached_events = await self._redis_client.smembers("crossplatform:processed_events")
            self._processed_events.update(cached_events)
            
            # Load correlation cache
            correlation_keys = await self._redis_client.keys("crossplatform:correlation:*")
            for key in correlation_keys:
                correlation_id = key.split(":")[-1]
                event_ids = await self._redis_client.lrange(key, 0, -1)
                self._correlation_cache[correlation_id] = event_ids
            
            self.logger.info(f"📊 Loaded {len(self._processed_events)} cached events")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to load cached data: {e}")
    
    def _validate_configuration(self):
        """Validate integration configuration"""
        required_config = ["output_path", "sync_interval"]
        for key in required_config:
            if key not in self.config:
                self.logger.warning(f"⚠️ Missing configuration key: {key}")
    
    async def process_event(self, event: CrossPlatformLogEvent) -> bool:
        """Process a cross-platform log event"""
        try:
            if not self._initialized:
                await self.initialize()
            
            # Check if already processed
            if event.event_id in self._processed_events:
                self._integration_metrics["events_processed"] += 1
                return True
            
            # Add to queue
            self._event_queue.append(event)
            
            # Process queue if it's getting full
            if len(self._event_queue) >= self._processing_rules["batch_processing_size"]:
                await self._process_event_queue()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error processing cross-platform event: {e}")
            self._integration_metrics["errors_encountered"] += 1
            return False
    
    async def _process_event_queue(self):
        """Process queued events"""
        if not self._event_queue:
            return
        
        try:
            batch = self._event_queue[:self._processing_rules["batch_processing_size"]]
            self._event_queue = self._event_queue[self._processing_rules["batch_processing_size"]:]
            
            # Group events by platform
            platform_events: Dict[PlatformType, List[CrossPlatformLogEvent]] = {}
            for event in batch:
                if event.platform not in platform_events:
                    platform_events[event.platform] = []
                platform_events[event.platform].append(event)
            
            # Process events for each platform
            tasks = []
            for platform, events in platform_events.items():
                tasks.append(self._process_platform_events(platform, events))
            
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Find correlations
            await self._find_event_correlations(batch)
            
            # Cache processed events
            for event in batch:
                await self._cache_processed_event(event)
                self._processed_events.add(event.event_id)
            
            self._integration_metrics["events_processed"] += len(batch)
            self.logger.info(f"✅ Processed batch of {len(batch)} cross-platform events")
            
        except Exception as e:
            self.logger.error(f"❌ Error processing event queue: {e}")
    
    async def _process_platform_events(self, platform: PlatformType, events: List[CrossPlatformLogEvent]):
        """Process events for specific platform"""
        try:
            if platform not in self._adapters:
                self.logger.warning(f"⚠️ No adapter available for platform: {platform.value}")
                return
            
            adapter = self._adapters[platform]
            
            # Send events to platform
            success = await adapter.send_log_data(events)
            
            if success:
                for event in events:
                    event.processed = True
                self.logger.info(f"✅ Sent {len(events)} events to {platform.value}")
            else:
                for event in events:
                    event.retry_count += 1
                    if event.retry_count < self._processing_rules["retry_max_attempts"]:
                        self._event_queue.append(event)  # Re-queue for retry
                    else:
                        event.error_message = f"Max retry attempts reached for {platform.value}"
                        self.logger.error(f"❌ Failed to process event {event.event_id} after {event.retry_count} attempts")
            
            self._integration_metrics["api_calls_made"] += 1
            
        except Exception as e:
            self.logger.error(f"❌ Error processing events for {platform.value}: {e}")
    
    async def _find_event_correlations(self, events: List[CrossPlatformLogEvent]):
        """Find correlations between cross-platform events"""
        try:
            correlation_window = self._processing_rules["correlation_window"]
            current_time = datetime.utcnow()
            
            for event in events:
                if not event.correlation_id:
                    continue
                
                correlation_id = event.correlation_id
                
                # Find related events within correlation window
                related_events = []
                for other_event in events:
                    if (other_event.correlation_id == correlation_id and 
                        other_event.event_id != event.event_id and
                        abs((other_event.timestamp - event.timestamp).total_seconds()) <= correlation_window):
                        related_events.append(other_event.event_id)
                
                if related_events:
                    # Store correlation
                    if correlation_id not in self._correlation_cache:
                        self._correlation_cache[correlation_id] = []
                    
                    self._correlation_cache[correlation_id].extend(related_events)
                    self._correlation_cache[correlation_id].append(event.event_id)
                    
                    # Remove duplicates
                    self._correlation_cache[correlation_id] = list(set(self._correlation_cache[correlation_id]))
                    
                    # Cache correlation
                    await self._cache_correlation(correlation_id, self._correlation_cache[correlation_id])
                    
                    self._integration_metrics["correlations_found"] += 1
                    
                    self.logger.info(f"🔗 Found correlation: {correlation_id} with {len(related_events)} related events")
            
        except Exception as e:
            self.logger.error(f"❌ Error finding event correlations: {e}")
    
    async def receive_webhook(self, platform: str, webhook_data: Dict[str, Any]) -> bool:
        """Receive webhook from platform"""
        try:
            platform_type = PlatformType(platform)
            
            if platform_type not in self._adapters:
                self.logger.warning(f"⚠️ No adapter for webhook from {platform}")
                return False
            
            adapter = self._adapters[platform_type]
            events = await adapter.receive_webhook(webhook_data)
            
            # Process received events
            for event in events:
                await self.process_event(event)
            
            self._integration_metrics["webhooks_received"] += 1
            self.logger.info(f"📥 Received webhook from {platform} with {len(events)} events")
            
            return True
            
        except ValueError:
            self.logger.error(f"❌ Unknown platform in webhook: {platform}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Error processing webhook: {e}")
            return False
    
    async def sync_platform_data(self, platform: Optional[PlatformType] = None) -> Dict[str, Any]:
        """Sync data with platform(s)"""
        try:
            sync_results = {}
            platforms_to_sync = [platform] if platform else list(self._adapters.keys())
            
            for platform_type in platforms_to_sync:
                if platform_type not in self._adapters:
                    continue
                
                adapter = self._adapters[platform_type]
                
                try:
                    # Test connection
                    connection_ok = await adapter.test_connection()
                    
                    if connection_ok:
                        # Process any queued events for this platform
                        platform_events = [e for e in self._event_queue if e.platform == platform_type]
                        if platform_events:
                            await self._process_platform_events(platform_type, platform_events)
                            # Remove processed events from queue
                            self._event_queue = [e for e in self._event_queue if e.platform != platform_type]
                        
                        sync_results[platform_type.value] = {
                            "status": "success",
                            "events_synced": len(platform_events),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        sync_results[platform_type.value] = {
                            "status": "connection_failed",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                
                except Exception as e:
                    sync_results[platform_type.value] = {
                        "status": "error",
                        "error": str(e),
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            self._integration_metrics["sync_operations"] += 1
            return sync_results
            
        except Exception as e:
            self.logger.error(f"❌ Error syncing platform data: {e}")
            return {"error": str(e)}
    
    async def _cache_processed_event(self, event: CrossPlatformLogEvent):
        """Cache processed event"""
        if not self._redis_client:
            return
        
        try:
            # Add to processed events set
            await self._redis_client.sadd("crossplatform:processed_events", event.event_id)
            
            # Cache event data
            event_key = f"crossplatform:event:{event.event_id}"
            await self._redis_client.setex(
                event_key,
                86400 * 7,  # 7 days
                json.dumps(event.to_dict())
            )
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cache processed event: {e}")
    
    async def _cache_correlation(self, correlation_id: str, event_ids: List[str]):
        """Cache event correlation"""
        if not self._redis_client:
            return
        
        try:
            correlation_key = f"crossplatform:correlation:{correlation_id}"
            
            # Clear existing correlation
            await self._redis_client.delete(correlation_key)
            
            # Store correlation
            if event_ids:
                await self._redis_client.lpush(correlation_key, *event_ids)
                await self._redis_client.expire(correlation_key, 86400 * 30)  # 30 days
            
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to cache correlation: {e}")
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all connected platforms"""
        status = {}
        
        for platform_type, adapter in self._adapters.items():
            try:
                connection_ok = await adapter.test_connection()
                config = self._platform_configs[platform_type]
                
                status[platform_type.value] = {
                    "connected": connection_ok,
                    "enabled": config.enabled,
                    "rate_limit_remaining": adapter._rate_limit_remaining,
                    "last_request": adapter._last_request_time.isoformat(),
                    "config": config.to_dict()
                }
                
            except Exception as e:
                status[platform_type.value] = {
                    "connected": False,
                    "error": str(e)
                }
        
        return status
    
    async def get_correlation_data(self, correlation_id: str) -> Optional[Dict[str, Any]]:
        """Get correlation data for specific correlation ID"""
        if correlation_id not in self._correlation_cache:
            return None
        
        event_ids = self._correlation_cache[correlation_id]
        
        # Get event details
        events = []
        for event_id in event_ids:
            if self._redis_client:
                try:
                    event_key = f"crossplatform:event:{event_id}"
                    event_data = await self._redis_client.get(event_key)
                    if event_data:
                        events.append(json.loads(event_data))
                except Exception:
                    pass
        
        return {
            "correlation_id": correlation_id,
            "event_count": len(event_ids),
            "event_ids": event_ids,
            "events": events,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """Get integration metrics"""
        metrics = self._integration_metrics.copy()
        metrics["queue_size"] = len(self._event_queue)
        metrics["cached_events"] = len(self._processed_events)
        metrics["correlations_cached"] = len(self._correlation_cache)
        metrics["platforms_configured"] = len(self._platform_configs)
        metrics["platforms_connected"] = len(self._adapters)
        metrics["uptime"] = "active"
        return metrics
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "redis_connected": self._redis_client is not None,
            "platforms": await self.get_platform_status(),
            "metrics": await self.get_integration_metrics(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check Redis connection
        if self._redis_client:
            try:
                await self._redis_client.ping()
                health["redis_status"] = "connected"
            except:
                health["redis_status"] = "disconnected"
        
        # Check if any platforms are connected
        connected_platforms = sum(1 for status in health["platforms"].values() if status.get("connected", False))
        if connected_platforms == 0:
            health["status"] = "degraded"
            health["warning"] = "No platforms connected"
        
        return health
    
    async def start_background_sync(self):
        """Start background sync process"""
        if self._running:
            return
        
        self._running = True
        self.logger.info("🔄 Starting background sync process...")
        
        while self._running:
            try:
                # Process event queue
                if self._event_queue:
                    await self._process_event_queue()
                
                # Sync with platforms
                await self.sync_platform_data()
                
                # Wait for next sync interval
                sync_interval = self.config.get("sync_interval", 300)
                await asyncio.sleep(sync_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in background sync: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def stop_background_sync(self):
        """Stop background sync process"""
        self._running = False
        self.logger.info("⏹️ Stopping background sync process...")
    
    async def shutdown(self):
        """Shutdown integration hub gracefully"""
        self.logger.info("🔄 Shutting down Cross-Platform Log Integration Hub...")
        
        # Stop background sync
        await self.stop_background_sync()
        
        # Process remaining events
        if self._event_queue:
            await self._process_event_queue()
        
        # Shutdown adapters
        for adapter in self._adapters.values():
            await adapter.shutdown()
        
        # Close Redis connection
        if self._redis_client:
            await self._redis_client.close()
        
        self.logger.info("✅ Integration hub shutdown complete")


# Example usage and testing
async def main():
    """Main function for testing"""
    config = {
        "output_path": "/tmp/crossplatform_logs",
        "sync_interval": 300,
        "redis": {"host": "localhost", "port": 6379},
        "platforms": {
            "youtube": {
                "api_endpoint": "https://www.googleapis.com/youtube/v3",
                "api_key": "test_key",
                "enabled": True
            },
            "ainflue": {
                "api_endpoint": "http://localhost:8000/api",
                "enabled": True
            }
        }
    }
    
    hub = CrossPlatformLogIntegrationHub(config)
    
    # Test event
    test_event = CrossPlatformLogEvent(
        creator_id="creator_123",
        platform=PlatformType.YOUTUBE,
        event_type=LogEventType.CONTENT_UPLOAD,
        content_id="video_456",
        correlation_id="corr_789",
        data={
            "title": "Test Video",
            "views": 1000,
            "likes": 50
        }
    )
    
    success = await hub.process_event(test_event)
    print(f"Event processed: {success}")
    
    # Platform status
    status = await hub.get_platform_status()
    print(f"Platform status: {status}")
    
    # Integration metrics
    metrics = await hub.get_integration_metrics()
    print(f"Integration metrics: {metrics}")
    
    # Health check
    health = await hub.health_check()
    print(f"Health check: {health}")
    
    await hub.shutdown()


if __name__ == "__main__":
    asyncio.run(main())