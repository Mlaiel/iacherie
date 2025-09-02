"""Real-time Scraper - IA-Influencer-Agent
=======================================

Real-time content monitoring and streaming scraper.
Designed for continuous surveillance and instant alerts.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.

⚠️ CRITICAL LEGAL WARNING ⚠️
UNAUTHORIZED USE, COPYING, OR DISTRIBUTION IS STRICTLY PROHIBITED AND WILL RESULT IN IMMEDIATE LEGAL ACTION.
This technology is EXCLUSIVE property of Fahed Mlaiel. Contact: mlaiel@live.de for licensing.
"""

import asyncio
import aiohttp
import websockets
import logging
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
from urllib.parse import urlparse
import hashlib
import time
from collections import defaultdict

@dataclass
class MonitorTarget:
    """
Real-time monitoring target definition."""
    target_id: str
    url: str
    platform: str
    monitor_type: str  # content, profile, hashtag, keyword
    check_interval: int = 60  # seconds
    keywords: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)
    webhook_url: Optional[str] = None
    email_alerts: List[str] = field(default_factory=list)
    active: bool = True
    last_check: Optional[datetime] = None
    last_content_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RealtimeEvent:
    """
Real-time event data structure."""
    event_id: str
    target_id: str
    event_type: str  # new_content, content_change, engagement_spike, etc.
    timestamp: datetime
    data: Dict[str, Any]
    priority: int = 1  # 1=low, 2=medium, 3=high, 4=critical
    processed: bool = False

class RealtimeScraper:
    """
    Real-time content monitoring and streaming scraper.
    
    Features:
    - Continuous monitoring
    - Change detection
    - Real-time alerts
    - WebSocket streaming
    - Event-driven architecture
    - Multi-target monitoring
    - Adaptive intervals
    - Content fingerprinting
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Monitoring state
        self.targets: Dict[str, MonitorTarget] = {}
        self.active_monitors: Dict[str, asyncio.Task] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.event_handlers: Dict[str, List[Callable]] = defaultdict(list)
        
        # WebSocket connections
        self.websocket_clients: List[websockets.WebSocketServerProtocol] = []
        self.websocket_server: Optional[websockets.WebSocketServer] = None
        
        # Statistics
        self.stats = {
            'active_targets': 0,
            'total_checks': 0,
            'changes_detected': 0,
            'events_generated': 0,
            'uptime_start': datetime.now(),
            'last_activity': datetime.now()
        }
        
        self.running = False
        
    async def __aenter__(self):
        """
Async context manager entry."""
        await self.start()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
Async context manager exit."""
        await self.stop()
        
    async def start(self):
        """
Start real-time monitoring."""
        if self.running:
            return
            
        self.logger.info("Starting real-time scraper")
        self.running = True
        
        # Initialize HTTP session
        connector = aiohttp.TCPConnector(
            limit=50,
            limit_per_host=10,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        # Start event processor
        asyncio.create_task(self._event_processor())
        
        # Start WebSocket server
        await self._start_websocket_server()
        
        self.stats['uptime_start'] = datetime.now()
        
    async def stop(self):
        """Stop real-time monitoring."""
        if not self.running:
            return
            
        self.logger.info("Stopping real-time scraper")
        self.running = False
        
        # Stop all monitors
        for task in self.active_monitors.values():
            task.cancel()
            
        await asyncio.gather(*self.active_monitors.values(), return_exceptions=True)
        self.active_monitors.clear()
        
        # Close WebSocket server
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
            
        # Close HTTP session
        if self.session:
            await self.session.close()
            
    async def add_target(self, target: MonitorTarget):
        """Add monitoring target."""
        self.targets[target.target_id] = target
        
        if target.active and self.running:
            await self._start_monitor(target)
            
        self.stats['active_targets'] = len([t for t in self.targets.values() if t.active])
        self.logger.info(f"Added monitoring target: {target.target_id}")
        
    async def remove_target(self, target_id: str):
        """Remove monitoring target."""
        if target_id in self.targets:
            await self._stop_monitor(target_id)
            del self.targets[target_id]
            
        self.stats['active_targets'] = len([t for t in self.targets.values() if t.active])
        self.logger.info(f"Removed monitoring target: {target_id}")
        
    async def _start_monitor(self, target: MonitorTarget):
        """Start monitoring specific target."""
        if target.target_id in self.active_monitors:
            await self._stop_monitor(target.target_id)
            
        task = asyncio.create_task(self._monitor_target(target))
        self.active_monitors[target.target_id] = task
        
    async def _stop_monitor(self, target_id: str):
        """
Stop monitoring specific target."""
        if target_id in self.active_monitors:
            self.active_monitors[target_id].cancel()
            try:
                await self.active_monitors[target_id]
            except asyncio.CancelledError:
                pass
            del self.active_monitors[target_id]
            
    async def _monitor_target(self, target: MonitorTarget):
        """
Monitor single target continuously."""
        self.logger.info(f"Started monitoring {target.target_id}")
        
        while self.running and target.active:
            try:
                await self._check_target(target)
                await asyncio.sleep(target.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error monitoring {target.target_id}: {e}")
                await asyncio.sleep(min(target.check_interval, 60))  # Fallback delay
                
        self.logger.info(f"Stopped monitoring {target.target_id}")
        
    async def _check_target(self, target: MonitorTarget):
        """Check single target for changes."""
        self.stats['total_checks'] += 1
        self.stats['last_activity'] = datetime.now()
        
        try:
            # Fetch current content
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with self.session.get(target.url, headers=headers) as response:
                if response.status != 200:
                    self.logger.warning(f"Target {target.target_id} returned status {response.status}")
                    return
                    
                content = await response.text()
                
            # Generate content fingerprint
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Check for changes
            if target.last_content_hash and target.last_content_hash != content_hash:
                await self._handle_content_change(target, content, content_hash)
                
            target.last_content_hash = content_hash
            target.last_check = datetime.now()
            
            # Check for keyword matches
            if target.keywords:
                await self._check_keywords(target, content)
                
        except Exception as e:
            self.logger.error(f"Error checking target {target.target_id}: {e}")
            
    async def _handle_content_change(self, target: MonitorTarget, 
                                   content: str, content_hash: str):
        """Handle detected content change."""
        self.stats['changes_detected'] += 1
        
        event = RealtimeEvent(
            event_id=self._generate_event_id(),
            target_id=target.target_id,
            event_type='content_change',
            timestamp=datetime.now(),
            data={
                'url': target.url,
                'platform': target.platform,
                'content_hash': content_hash,
                'content_length': len(content),
                'change_detected_at': datetime.now().isoformat()
            },
            priority=2
        )
        
        await self.event_queue.put(event)
        self.logger.info(f"Content change detected for {target.target_id}")
        
    async def _check_keywords(self, target: MonitorTarget, content: str):
        """Check content for keyword matches."""
        content_lower = content.lower()
        matched_keywords = [kw for kw in target.keywords if kw.lower() in content_lower]
        
        if matched_keywords:
            event = RealtimeEvent(
                event_id=self._generate_event_id(),
                target_id=target.target_id,
                event_type='keyword_match',
                timestamp=datetime.now(),
                data={
                    'url': target.url,
                    'platform': target.platform,
                    'matched_keywords': matched_keywords,
                    'total_keywords': len(target.keywords)
                },
                priority=3
            )
            
            await self.event_queue.put(event)
            
    def _generate_event_id(self) -> str:
        """
Generate unique event ID."""
        timestamp = str(int(time.time() * 1000))
        return f"event_{timestamp}_{hashlib.md5(f'{timestamp}{time.time()}'.encode()).hexdigest()[:8]}"
        
    async def _event_processor(self):
        """Process events from queue."""
        while self.running:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)
                
                await self._process_event(event)
                self.stats['events_generated'] += 1
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                
    async def _process_event(self, event: RealtimeEvent):
        """Process single event."""
        # Call registered handlers
        for handler in self.event_handlers.get(event.event_type, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                self.logger.error(f"Event handler error: {e}")
                
        # Send to WebSocket clients
        await self._broadcast_event(event)
        
        # Send webhook notifications
        target = self.targets.get(event.target_id)
        if target and target.webhook_url:
            await self._send_webhook(target.webhook_url, event)
            
        event.processed = True
        
    async def _broadcast_event(self, event: RealtimeEvent):
        """Broadcast event to WebSocket clients."""
        if not self.websocket_clients:
            return
            
        message = json.dumps({
            'event_id': event.event_id,
            'target_id': event.target_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'data': event.data,
            'priority': event.priority
        })
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
            except Exception as e:
                self.logger.error(f"WebSocket send error: {e}")
                disconnected_clients.append(client)
                
        # Remove disconnected clients
        for client in disconnected_clients:
            self.websocket_clients.remove(client)
            
    async def _send_webhook(self, webhook_url: str, event: RealtimeEvent):
        """Send webhook notification."""
        try:
            payload = {
                'event_id': event.event_id,
                'target_id': event.target_id,
                'event_type': event.event_type,
                'timestamp': event.timestamp.isoformat(),
                'data': event.data,
                'priority': event.priority
            }
            
            async with self.session.post(
                webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            ) as response:
                if response.status != 200:
                    self.logger.warning(f"Webhook failed with status {response.status}")
                    
        except Exception as e:
            self.logger.error(f"Webhook error: {e}")
            
    async def _start_websocket_server(self, host: str = 'localhost', port: int = 8765):
        """Start WebSocket server for real-time updates."""
        async def handle_client(websocket, path):
            self.websocket_clients.append(websocket)
            self.logger.info(f"WebSocket client connected: {websocket.remote_address}")
            
            try:
                await websocket.wait_closed()
            except Exception as e:
                self.logger.error(f"WebSocket client error: {e}")
            finally:
                if websocket in self.websocket_clients:
                    self.websocket_clients.remove(websocket)
                self.logger.info(f"WebSocket client disconnected: {websocket.remote_address}")
                
        try:
            self.websocket_server = await websockets.serve(handle_client, host, port)
            self.logger.info(f"WebSocket server started on ws://{host}:{port}")
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
            
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler for specific event type."""
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Registered handler for event type: {event_type}")
        
    def unregister_event_handler(self, event_type: str, handler: Callable):
        """Unregister event handler."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            
    async def get_target_status(self, target_id: str) -> Optional[Dict[str, Any]]:
        """
Get status of monitoring target."""
        if target_id not in self.targets:
            return None
            
        target = self.targets[target_id]
        
        return {
            'target_id': target.target_id,
            'url': target.url,
            'platform': target.platform,
            'monitor_type': target.monitor_type,
            'active': target.active,
            'check_interval': target.check_interval,
            'last_check': target.last_check.isoformat() if target.last_check else None,
            'is_monitoring': target_id in self.active_monitors,
            'keywords_count': len(target.keywords),
            'has_webhook': bool(target.webhook_url)
        }
        
    async def get_all_targets(self) -> List[Dict[str, Any]]:
        """
Get status of all monitoring targets."""
        statuses = []
        for target_id in self.targets:
            status = await self.get_target_status(target_id)
            if status:
                statuses.append(status)
        return statuses
        
    def get_stats(self) -> Dict[str, Any]:
        """
Get real-time scraper statistics."""
        uptime = (datetime.now() - self.stats['uptime_start']).total_seconds()
        
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'websocket_clients': len(self.websocket_clients),
            'event_queue_size': self.event_queue.qsize(),
            'running': self.running,
            'checks_per_minute': self.stats['total_checks'] / (uptime / 60) if uptime > 0 else 0
        }
        
    async def stream_events(self) -> AsyncGenerator[RealtimeEvent, None]:
        """
Stream events as they occur."""
        temp_queue = asyncio.Queue()
        
        # Register temporary handler
        def temp_handler(event: RealtimeEvent):
        try:
            logger.info(f"Executing temp_handler")
            
            # Implementation for temp_handler
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"temp_handler completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"temp_handler failed: {e}")
            raise
        for event_type in self.event_handlers:
            self.register_event_handler(event_type, temp_handler)
            
        try:
            while self.running:
                try:
                    event = await asyncio.wait_for(temp_queue.get(), timeout=1.0)
                    yield event
                except asyncio.TimeoutError:
                    continue
        finally:
            # Cleanup
            for event_type in self.event_handlers:
                self.unregister_event_handler(event_type, temp_handler)
