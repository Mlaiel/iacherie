"""MongoDB Change Stream Manager
=============================

Advanced MongoDB change streams handler for real-time data synchronization
in the Ainflue platform enterprise infrastructure.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime
import threading
from queue import Queue
import json

try:
    import pymongo
    from pymongo import MongoClient
    from pymongo.errors import OperationFailure, NetworkTimeout
    import bson
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

from . import SyncEvent, SyncConfiguration

logger = logging.getLogger(__name__)

class ChangeStreamManager:
    """Enterprise-grade MongoDB change streams management system."""
    
    def __init__(self, connection_string: str, database_name: Optional[str] = None):
        """Initialize change stream manager."""
        if not MONGODB_AVAILABLE:
            raise ImportError("PyMongo is required for change stream management")
            
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.change_streams = {}
        self.event_handlers: List[Callable] = []
        self.running_streams = set()
        
        # Configuration
        self.batch_size = 100
        self.max_await_time_ms = 1000
        self.full_document = "updateLookup"
        
        # Event queue for processing
        self.event_queue = Queue(maxsize=10000)
        self.processing_threads = []
        self.shutdown_event = threading.Event()
        
    def add_event_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add event handler for change stream events."""
        self.event_handlers.append(handler)
        logger.info(f"Added event handler: {handler.__name__}")
    
    async def start_collection_stream(self, 
                                    collection_name: str,
                                    pipeline: Optional[List[Dict[str, Any]]] = None,
                                    resume_token: Optional[Dict[str, Any]] = None) -> str:
        """Start change stream for a specific collection."""
        try:
            if not self.client:
                self.client = MongoClient(self.connection_string)
            
            # Get collection reference
            if self.database_name:
                collection = self.client[self.database_name][collection_name]
            else:
                # Use first database if none specified
                db_names = self.client.list_database_names()
                db_names = [db for db in db_names if db not in ['admin', 'config', 'local']]
                if not db_names:
                    raise ValueError("No suitable database found")
                collection = self.client[db_names[0]][collection_name]
            
            # Configure change stream options
            options = {
                'full_document': self.full_document,
                'batch_size': self.batch_size,
                'max_await_time_ms': self.max_await_time_ms
            }
            
            if resume_token:
                options['resume_after'] = resume_token
            
            # Create change stream
            if pipeline:
                change_stream = collection.watch(pipeline, **options)
            else:
                change_stream = collection.watch(**options)
            
            stream_id = f"{collection.database.name}.{collection_name}"
            self.change_streams[stream_id] = {
                'stream': change_stream,
                'collection': collection_name,
                'database': collection.database.name,
                'started_at': datetime.now(),
                'resume_token': None
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id,),
                daemon=True
            )
            monitor_thread.start()
            self.running_streams.add(stream_id)
            
            logger.info(f"Started change stream for: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to start change stream for {collection_name}: {e}")
            raise
    
    async def start_database_stream(self, 
                                  pipeline: Optional[List[Dict[str, Any]]] = None,
                                  resume_token: Optional[Dict[str, Any]] = None) -> str:
        """Start change stream for entire database."""
        try:
            if not self.client:
                self.client = MongoClient(self.connection_string)
            
            # Get database reference
            if self.database_name:
                database = self.client[self.database_name]
            else:
                db_names = self.client.list_database_names()
                db_names = [db for db in db_names if db not in ['admin', 'config', 'local']]
                if not db_names:
                    raise ValueError("No suitable database found")
                database = self.client[db_names[0]]
            
            # Configure change stream options
            options = {
                'full_document': self.full_document,
                'batch_size': self.batch_size,
                'max_await_time_ms': self.max_await_time_ms
            }
            
            if resume_token:
                options['resume_after'] = resume_token
            
            # Create change stream
            if pipeline:
                change_stream = database.watch(pipeline, **options)
            else:
                change_stream = database.watch(**options)
            
            stream_id = f"db.{database.name}"
            self.change_streams[stream_id] = {
                'stream': change_stream,
                'collection': None,  # Database-level stream
                'database': database.name,
                'started_at': datetime.now(),
                'resume_token': None
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id,),
                daemon=True
            )
            monitor_thread.start()
            self.running_streams.add(stream_id)
            
            logger.info(f"Started database change stream: {stream_id}")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to start database change stream: {e}")
            raise
    
    async def start_cluster_stream(self, 
                                 pipeline: Optional[List[Dict[str, Any]]] = None,
                                 resume_token: Optional[Dict[str, Any]] = None) -> str:
        """Start change stream for entire cluster."""
        try:
            if not self.client:
                self.client = MongoClient(self.connection_string)
            
            # Configure change stream options
            options = {
                'full_document': self.full_document,
                'batch_size': self.batch_size,
                'max_await_time_ms': self.max_await_time_ms
            }
            
            if resume_token:
                options['resume_after'] = resume_token
            
            # Create cluster-wide change stream
            if pipeline:
                change_stream = self.client.watch(pipeline, **options)
            else:
                change_stream = self.client.watch(**options)
            
            stream_id = "cluster"
            self.change_streams[stream_id] = {
                'stream': change_stream,
                'collection': None,
                'database': None,
                'started_at': datetime.now(),
                'resume_token': None
            }
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                args=(stream_id,),
                daemon=True
            )
            monitor_thread.start()
            self.running_streams.add(stream_id)
            
            logger.info("Started cluster-wide change stream")
            return stream_id
            
        except Exception as e:
            logger.error(f"Failed to start cluster change stream: {e}")
            raise
    
    def _monitor_stream(self, stream_id: str):
        """Monitor a change stream and process events."""
        logger.info(f"Starting stream monitor for: {stream_id}")
        
        stream_info = self.change_streams[stream_id]
        change_stream = stream_info['stream']
        
        try:
            while stream_id in self.running_streams and not self.shutdown_event.is_set():
                try:
                    # Get next change with timeout
                    change = change_stream.try_next()
                    
                    if change is not None:
                        # Store resume token
                        stream_info['resume_token'] = change_stream.resume_token
                        
                        # Create sync event
                        event = self._create_sync_event(change, stream_id)
                        
                        # Queue event for processing
                        try:
                            self.event_queue.put(event, timeout=1)
                        except:
                            logger.warning(f"Event queue full, dropping event for {stream_id}")
                        
                        # Process event immediately for real-time handlers
                        self._process_event_immediate(event)
                    
                    # Small delay to prevent excessive CPU usage
                    threading.Event().wait(0.001)
                    
                except OperationFailure as e:
                    if e.code == 40573:  # InvalidResumeToken
                        logger.warning(f"Invalid resume token for {stream_id}, restarting stream")
                        # Restart stream without resume token
                        break
                    else:
                        logger.error(f"Operation failed for stream {stream_id}: {e}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error monitoring stream {stream_id}: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Fatal error in stream monitor {stream_id}: {e}")
        finally:
            # Clean up
            try:
                change_stream.close()
            except:
                pass
            
            if stream_id in self.running_streams:
                self.running_streams.remove(stream_id)
            
            logger.info(f"Stream monitor stopped: {stream_id}")
    
    def _create_sync_event(self, change: Dict[str, Any], stream_id: str) -> SyncEvent:
        """Create a sync event from a change stream event."""
        operation_type = change.get('operationType', 'unknown')
        
        # Extract document information
        namespace = change.get('ns', {})
        database = namespace.get('db', 'unknown')
        collection = namespace.get('coll', 'unknown')
        
        # Extract document ID
        document_id = None
        if 'documentKey' in change:
            document_id = change['documentKey'].get('_id')
        
        # Extract document data
        document_data = {}
        if operation_type in ['insert', 'replace']:
            document_data = change.get('fullDocument', {})
        elif operation_type == 'update':
            document_data = {
                'updateDescription': change.get('updateDescription', {}),
                'fullDocument': change.get('fullDocument', {})
            }
        elif operation_type == 'delete':
            document_data = change.get('fullDocumentBeforeChange', {})
        
        event = SyncEvent(
            event_id=f"evt_{int(datetime.now().timestamp() * 1000000)}",
            sync_id=stream_id,
            operation_type=operation_type,
            collection=f"{database}.{collection}",
            document_id=document_id,
            timestamp=datetime.now(),
            data={
                'change': change,
                'document': document_data,
                'cluster_time': change.get('clusterTime'),
                'resume_token': change.get('_id')
            },
            status='pending'
        )
        
        return event
    
    def _process_event_immediate(self, event: SyncEvent):
        """Process event immediately for real-time handlers."""
        for handler in self.event_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Event handler failed: {e}")
    
    def start_event_processors(self, num_threads: int = 3):
        """Start background event processing threads."""
        for i in range(num_threads):
            processor_thread = threading.Thread(
                target=self._process_events,
                args=(f"processor_{i}",),
                daemon=True
            )
            processor_thread.start()
            self.processing_threads.append(processor_thread)
        
        logger.info(f"Started {num_threads} event processing threads")
    
    def _process_events(self, processor_name: str):
        """Process events from the event queue."""
        logger.info(f"Event processor started: {processor_name}")
        
        while not self.shutdown_event.is_set():
            try:
                # Get event from queue with timeout
                event = self.event_queue.get(timeout=1)
                
                # Process the event
                self._process_single_event(event)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except:
                # Timeout or shutdown
                continue
        
        logger.info(f"Event processor stopped: {processor_name}")
    
    def _process_single_event(self, event: SyncEvent):
        """Process a single sync event."""
        try:
            # Apply any transformations
            transformed_event = self._apply_transformations(event)
            
            # Apply filters
            if self._passes_filters(transformed_event):
                # Process through handlers
                for handler in self.event_handlers:
                    try:
                        handler(transformed_event)
                    except Exception as e:
                        logger.error(f"Handler failed for event {event.event_id}: {e}")
                
                # Update event status
                transformed_event.status = 'processed'
            else:
                transformed_event.status = 'filtered'
                
        except Exception as e:
            logger.error(f"Failed to process event {event.event_id}: {e}")
            event.status = 'error'
            event.error_message = str(e)
    
    def _apply_transformations(self, event: SyncEvent) -> SyncEvent:
        """Apply transformations to the event."""
        # Implement event transformations
        # This could include data format changes, field mappings, etc.
        return event
    
    def _passes_filters(self, event: SyncEvent) -> bool:
        """Check if event passes configured filters."""
        # Implement filtering logic
        # This could filter by collection, operation type, field values, etc.
        return True
    
    def stop_stream(self, stream_id: str):
        """Stop a specific change stream."""
        if stream_id in self.running_streams:
            self.running_streams.remove(stream_id)
            
            if stream_id in self.change_streams:
                try:
                    self.change_streams[stream_id]['stream'].close()
                except:
                    pass
                del self.change_streams[stream_id]
            
            logger.info(f"Stopped change stream: {stream_id}")
    
    def stop_all_streams(self):
        """Stop all change streams."""
        for stream_id in list(self.running_streams):
            self.stop_stream(stream_id)
    
    def get_stream_status(self) -> Dict[str, Any]:
        """Get status of all change streams."""
        status = {
            'active_streams': len(self.running_streams),
            'total_streams': len(self.change_streams),
            'event_queue_size': self.event_queue.qsize(),
            'processing_threads': len(self.processing_threads),
            'streams': {}
        }
        
        for stream_id, stream_info in self.change_streams.items():
            status['streams'][stream_id] = {
                'collection': stream_info['collection'],
                'database': stream_info['database'],
                'started_at': stream_info['started_at'],
                'running': stream_id in self.running_streams,
                'has_resume_token': stream_info['resume_token'] is not None
            }
        
        return status
    
    def get_resume_tokens(self) -> Dict[str, Any]:
        """Get resume tokens for all streams."""
        tokens = {}
        for stream_id, stream_info in self.change_streams.items():
            if stream_info['resume_token']:
                tokens[stream_id] = stream_info['resume_token']
        return tokens
    
    def shutdown(self):
        """Shutdown change stream manager."""
        logger.info("Shutting down change stream manager")
        
        # Signal shutdown
        self.shutdown_event.set()
        
        # Stop all streams
        self.stop_all_streams()
        
        # Wait for processing threads
        for thread in self.processing_threads:
            thread.join(timeout=5)
        
        # Close client connection
        if self.client:
            self.client.close()
        
        logger.info("Change stream manager shutdown complete")

# Export the main class
__all__ = ['ChangeStreamManager']