"""Edge Telemetry Collector
========================

Advanced telemetry collection system for edge computing infrastructure,
providing comprehensive data gathering, processing, and forwarding.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid
import json
import gzip
import base64

logger = logging.getLogger(__name__)


class TelemetryType(str, Enum):
    """Types of telemetry data."""
    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"
    EVENTS = "events"
    DIAGNOSTICS = "diagnostics"


class DataFormat(str, Enum):
    """Telemetry data formats."""
    JSON = "json"
    PROTOBUF = "protobuf"
    AVRO = "avro"
    MSGPACK = "msgpack"


@dataclass
class TelemetrySource:
    """Telemetry data source configuration."""
    source_id: str
    name: str
    telemetry_type: TelemetryType
    endpoint: str
    interval: int = 60  # seconds
    enabled: bool = True
    format: DataFormat = DataFormat.JSON
    compression: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TelemetryData:
    """Telemetry data point."""
    data_id: str
    source_id: str
    telemetry_type: TelemetryType
    timestamp: datetime
    data: Any
    format: DataFormat
    compressed: bool = False
    size: int = 0
    tags: Dict[str, str] = field(default_factory=dict)


class EdgeTelemetryCollector:
    """Advanced telemetry collection system for edge computing."""
    
    def __init__(self,
                 max_buffer_size: int = 10000,
                 batch_size: int = 100,
                 flush_interval: int = 30,
                 compression_threshold: int = 1024):
        
        self.max_buffer_size = max_buffer_size
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.compression_threshold = compression_threshold
        
        # Data collection and storage
        self.telemetry_sources: Dict[str, TelemetrySource] = {}
        self.data_buffer: List[TelemetryData] = []
        self.collection_stats = {
            'total_collected': 0,
            'total_forwarded': 0,
            'collection_errors': 0,
            'forwarding_errors': 0
        }
        
        # Data processors and forwarders
        self.data_processors: List[Callable] = []
        self.data_forwarders: List[Callable] = []
        
        # Background tasks
        self.collection_task: Optional[asyncio.Task] = None
        self.forwarding_task: Optional[asyncio.Task] = None
        
        # Control flags
        self.running = False
        
        logger.info("EdgeTelemetryCollector initialized")
    
    async def start(self):
        """Start the telemetry collection system."""
        if self.running:
            logger.warning("Telemetry collector already running")
            return
        
        self.running = True
        
        # Start background tasks
        self.collection_task = asyncio.create_task(self._collection_loop())
        self.forwarding_task = asyncio.create_task(self._forwarding_loop())
        
        logger.info("Edge telemetry collection started")
    
    async def stop(self):
        """Stop the telemetry collection system."""
        self.running = False
        
        # Cancel background tasks
        tasks = [self.collection_task, self.forwarding_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Wait for tasks to complete and flush remaining data
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Final flush
        await self._flush_data()
        
        logger.info("Edge telemetry collection stopped")
    
    async def add_telemetry_source(self, source: TelemetrySource) -> bool:
        """Add a telemetry data source."""
        try:
            self.telemetry_sources[source.source_id] = source
            logger.info(f"Added telemetry source: {source.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add telemetry source {source.name}: {e}")
            return False
    
    async def remove_telemetry_source(self, source_id: str) -> bool:
        """Remove a telemetry data source."""
        try:
            if source_id in self.telemetry_sources:
                del self.telemetry_sources[source_id]
                logger.info(f"Removed telemetry source: {source_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove telemetry source {source_id}: {e}")
            return False
    
    async def collect_data(self, data: TelemetryData):
        """Collect a single telemetry data point."""
        try:
            # Process data through processors
            processed_data = data
            for processor in self.data_processors:
                try:
                    processed_data = await processor(processed_data) if asyncio.iscoroutinefunction(processor) else processor(processed_data)
                    if processed_data is None:
                        return  # Data was filtered out
                except Exception as e:
                    logger.error(f"Error in data processor: {e}")
                    continue
            
            # Compress if needed
            if processed_data.size > self.compression_threshold and not processed_data.compressed:
                processed_data = await self._compress_data(processed_data)
            
            # Add to buffer
            self.data_buffer.append(processed_data)
            self.collection_stats['total_collected'] += 1
            
            # Check buffer size and flush if needed
            if len(self.data_buffer) >= self.max_buffer_size:
                await self._flush_data()
                
        except Exception as e:
            logger.error(f"Failed to collect telemetry data: {e}")
            self.collection_stats['collection_errors'] += 1
    
    def add_data_processor(self, processor: Callable):
        """Add a data processor function."""
        self.data_processors.append(processor)
    
    def add_data_forwarder(self, forwarder: Callable):
        """Add a data forwarder function."""
        self.data_forwarders.append(forwarder)
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get telemetry collection statistics."""
        return {
            **self.collection_stats,
            'buffer_size': len(self.data_buffer),
            'active_sources': len([s for s in self.telemetry_sources.values() if s.enabled]),
            'total_sources': len(self.telemetry_sources)
        }
    
    async def export_telemetry_data(self, 
                                   telemetry_type: Optional[TelemetryType] = None,
                                   since: Optional[datetime] = None,
                                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Export telemetry data in JSON format."""
        
        data_to_export = []
        
        for data in self.data_buffer:
            # Apply filters
            if telemetry_type and data.telemetry_type != telemetry_type:
                continue
            if since and data.timestamp < since:
                continue
            
            # Convert to exportable format
            exported_data = {
                'data_id': data.data_id,
                'source_id': data.source_id,
                'telemetry_type': data.telemetry_type.value,
                'timestamp': data.timestamp.isoformat(),
                'format': data.format.value,
                'compressed': data.compressed,
                'size': data.size,
                'tags': data.tags,
                'data': await self._serialize_data(data)
            }
            
            data_to_export.append(exported_data)
        
        # Apply limit
        if limit:
            data_to_export = data_to_export[:limit]
        
        return data_to_export
    
    # Private methods
    
    async def _collection_loop(self):
        """Main collection loop."""
        last_collection_times = {}
        
        while self.running:
            try:
                current_time = datetime.now()
                
                for source_id, source in self.telemetry_sources.items():
                    if not source.enabled:
                        continue
                    
                    # Check if it's time to collect from this source
                    last_collection = last_collection_times.get(source_id)
                    
                    if (last_collection is None or 
                        (current_time - last_collection).seconds >= source.interval):
                        
                        try:
                            data = await self._collect_from_source(source)
                            if data:
                                await self.collect_data(data)
                            last_collection_times[source_id] = current_time
                            
                        except Exception as e:
                            logger.error(f"Failed to collect from source {source.name}: {e}")
                            self.collection_stats['collection_errors'] += 1
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {e}")
                await asyncio.sleep(5)
    
    async def _forwarding_loop(self):
        """Background forwarding loop."""
        while self.running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_data()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in forwarding loop: {e}")
                await asyncio.sleep(self.flush_interval)
    
    async def _collect_from_source(self, source: TelemetrySource) -> Optional[TelemetryData]:
        """Collect data from a specific source."""
        
        try:
            # This is where we would implement actual data collection
            # For now, we'll create sample data based on source type
            
            sample_data = await self._generate_sample_data(source)
            
            data = TelemetryData(
                data_id=str(uuid.uuid4()),
                source_id=source.source_id,
                telemetry_type=source.telemetry_type,
                timestamp=datetime.now(),
                data=sample_data,
                format=source.format,
                compressed=False,
                size=len(json.dumps(sample_data)),
                tags={'source_name': source.name}
            )
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to collect from source {source.name}: {e}")
            return None
    
    async def _generate_sample_data(self, source: TelemetrySource) -> Any:
        """Generate sample data based on source type."""
        
        if source.telemetry_type == TelemetryType.METRICS:
            return {
                'cpu_usage': 45.2,
                'memory_usage': 67.8,
                'disk_usage': 34.1,
                'network_io': 1024
            }
        elif source.telemetry_type == TelemetryType.LOGS:
            return {
                'level': 'INFO',
                'message': 'Sample log message',
                'logger': 'edge.system',
                'thread': 'main'
            }
        elif source.telemetry_type == TelemetryType.TRACES:
            return {
                'trace_id': str(uuid.uuid4()),
                'span_id': str(uuid.uuid4()),
                'operation': 'edge.process',
                'duration': 125.5
            }
        elif source.telemetry_type == TelemetryType.EVENTS:
            return {
                'event_type': 'system.startup',
                'source': source.name,
                'description': 'System component started'
            }
        elif source.telemetry_type == TelemetryType.DIAGNOSTICS:
            return {
                'component': 'edge.cache',
                'status': 'healthy',
                'performance': {
                    'hit_ratio': 0.85,
                    'response_time': 2.3
                }
            }
        else:
            return {'type': 'unknown', 'value': 'sample'}
    
    async def _compress_data(self, data: TelemetryData) -> TelemetryData:
        """Compress telemetry data."""
        
        try:
            # Serialize data to JSON
            serialized = json.dumps(data.data).encode('utf-8')
            
            # Compress using gzip
            compressed = gzip.compress(serialized)
            
            # Encode as base64 for storage
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            # Create new data object with compressed data
            compressed_data = TelemetryData(
                data_id=data.data_id,
                source_id=data.source_id,
                telemetry_type=data.telemetry_type,
                timestamp=data.timestamp,
                data=encoded,
                format=data.format,
                compressed=True,
                size=len(encoded),
                tags=data.tags
            )
            
            logger.debug(f"Compressed data from {data.size} to {compressed_data.size} bytes")
            return compressed_data
            
        except Exception as e:
            logger.error(f"Failed to compress data: {e}")
            return data
    
    async def _decompress_data(self, data: TelemetryData) -> TelemetryData:
        """Decompress telemetry data."""
        
        try:
            if not data.compressed:
                return data
            
            # Decode from base64
            compressed = base64.b64decode(data.data.encode('utf-8'))
            
            # Decompress
            decompressed = gzip.decompress(compressed)
            
            # Parse JSON
            parsed_data = json.loads(decompressed.decode('utf-8'))
            
            # Create new data object with decompressed data
            decompressed_data = TelemetryData(
                data_id=data.data_id,
                source_id=data.source_id,
                telemetry_type=data.telemetry_type,
                timestamp=data.timestamp,
                data=parsed_data,
                format=data.format,
                compressed=False,
                size=len(decompressed),
                tags=data.tags
            )
            
            return decompressed_data
            
        except Exception as e:
            logger.error(f"Failed to decompress data: {e}")
            return data
    
    async def _serialize_data(self, data: TelemetryData) -> Any:
        """Serialize telemetry data for export."""
        
        if data.compressed:
            # Decompress first
            decompressed = await self._decompress_data(data)
            return decompressed.data
        else:
            return data.data
    
    async def _flush_data(self):
        """Flush buffered data to forwarders."""
        
        if not self.data_buffer:
            return
        
        # Create batch
        batch = self.data_buffer[:self.batch_size]
        self.data_buffer = self.data_buffer[self.batch_size:]
        
        # Forward to all configured forwarders
        for forwarder in self.data_forwarders:
            try:
                if asyncio.iscoroutinefunction(forwarder):
                    await forwarder(batch)
                else:
                    forwarder(batch)
                
                self.collection_stats['total_forwarded'] += len(batch)
                
            except Exception as e:
                logger.error(f"Error in data forwarder: {e}")
                self.collection_stats['forwarding_errors'] += 1
        
        logger.debug(f"Flushed {len(batch)} telemetry data points")


def create_telemetry_collector(
    max_buffer_size: int = 10000,
    batch_size: int = 100,
    flush_interval: int = 30,
    compression_threshold: int = 1024
) -> EdgeTelemetryCollector:
    """Create and configure a telemetry collector instance."""
    return EdgeTelemetryCollector(
        max_buffer_size=max_buffer_size,
        batch_size=batch_size,
        flush_interval=flush_interval,
        compression_threshold=compression_threshold
    )


# Example usage and testing
if __name__ == "__main__":
    async def test_telemetry_collector():
        """Test the telemetry collector."""
        collector = create_telemetry_collector(batch_size=5, flush_interval=10)
        
        # Add sample forwarder
        async def sample_forwarder(batch: List[TelemetryData]):
            print(f"Forwarding batch of {len(batch)} telemetry points")
            for data in batch:
                print(f"  - {data.telemetry_type.value}: {data.source_id}")
        
        collector.add_data_forwarder(sample_forwarder)
        
        # Start collector
        await collector.start()
        
        # Add telemetry sources
        metrics_source = TelemetrySource(
            source_id="system_metrics",
            name="System Metrics",
            telemetry_type=TelemetryType.METRICS,
            endpoint="localhost:9090",
            interval=5
        )
        await collector.add_telemetry_source(metrics_source)
        
        logs_source = TelemetrySource(
            source_id="application_logs",
            name="Application Logs",
            telemetry_type=TelemetryType.LOGS,
            endpoint="localhost:514",
            interval=10
        )
        await collector.add_telemetry_source(logs_source)
        
        # Let it collect some data
        await asyncio.sleep(20)
        
        # Get statistics
        stats = await collector.get_collection_stats()
        print(f"Collection stats: {stats}")
        
        # Export data
        exported = await collector.export_telemetry_data(limit=10)
        print(f"Exported {len(exported)} telemetry data points")
        
        # Stop collector
        await collector.stop()
    
    # Run test
    asyncio.run(test_telemetry_collector())