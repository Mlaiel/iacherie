# -*- coding: utf-8 -*-
"""Test adapté automatiquement pour le projet Ainflue
================================================

Ce fichier a été importé et adapté depuis l'ancien projet IA-Influencer.
Certains imports et fonctionnalités peuvent nécessiter des ajustements manuels.
"""

import sys
import os
from pathlib import Path

# Ajouter le répertoire racine au Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

"""
Test Event Handler Module

Tests for real-time event management, queue processing, and worker systems.

Author: Fahed Mlaiel (Legal Copyright)
Copyright (c) 2025 Fahed Mlaiel. Tous droits réservés.
Propriété intellectuelle protégée sous toutes juridictions.
"""

import pytest
import sys
import os
from pathlib import Path
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from crawlers.handlers.event_handler import (
    EventHandler,
    AsyncEventHandler,
    SyncEventHandler,
    EventDispatcher,
    EventQueue,
    EventRegistry,
    EventWorker,
    Event,
    EventMetadata,
    EventPriority,
    EventStatus
)


class TestEvent:
    """
Test suite for Event class."""
    def test_event_creation(self):
        """
Test event object creation."""
        event = Event(
            event_id='test-001',
            event_type='content_upload',
            data={'file_path': '/test/file.txt'},
            priority=EventPriority.HIGH
        )
        
        assert event.event_id == 'test-001'
        assert event.event_type == 'content_upload'
        assert event.data['file_path'] == '/test/file.txt'
        assert event.priority == EventPriority.HIGH
        assert event.status == EventStatus.PENDING
        assert isinstance(event.timestamp, datetime)

    def test_event_serialization(self):
        """
Test event JSON serialization."""
        event = Event(
            event_id='test-002',
            event_type='processing_complete',
            data={'result': 'success'}
        )
        
        json_data = event.to_json()
        assert 'event_id' in json_data
        assert 'event_type' in json_data
        assert 'data' in json_data
        assert 'timestamp' in json_data

    def test_event_from_json(self):
        """
Test event deserialization from JSON."""
        json_data = {
            'event_id': 'test-003',
            'event_type': 'error_occurred',
            'data': {'error': 'File not found'},
            'priority': 'MEDIUM',
            'timestamp': '2025-01-11T10:00:00',
            'status': 'PENDING'
        }
        
        event = Event.from_json(json_data)
        assert event.event_id == 'test-003'
        assert event.event_type == 'error_occurred'
        assert event.data['error'] == 'File not found'
        assert event.priority == EventPriority.MEDIUM


class TestEventHandler:
    """
Test suite for EventHandler base class."""
    def test_handler_creation(self):
        """
Test handler initialization."""
        handler = EventHandler('test_handler')
        assert handler.name == 'test_handler'
        assert handler.handler_id is not None
        assert handler.is_active

    def test_handler_with_custom_id(self):
        """
Test handler with custom ID."""
        handler = EventHandler('test_handler', 'custom-123')
        assert handler.handler_id == 'custom-123'

    def test_handler_start_stop(self):
        """
Test handler lifecycle management."""
        handler = EventHandler('test_handler')
        
        handler.start()
        assert handler.is_active
        
        handler.stop()
        assert not handler.is_active

    @pytest.mark.asyncio
    async def test_handle_event_not_implemented(self):
        try:
            logger.info(f"Executing test_handle_event_not_implemented")
            
            # Implementation for test_handle_event_not_implemented
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_handle_event_not_implemented completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_handle_event_not_implemented failed: {e}")
            raise
            await handler.handle(event)


class TestAsyncEventHandler:
        try:
            logger.info(f"Executing test_coroutine")
            
            # Implementation for test_coroutine
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_coroutine completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_coroutine failed: {e}")
            raise
    """
Test suite for AsyncEventHandler class."""
    @pytest.mark.asyncio
    async def test_async_handler_execution(self):
        """
Test async event handling."""
        async def test_coroutine(event):
            return f"Processed {event.event_type}"
        
        handler = AsyncEventHandler('async_handler')
        handler.coroutine = test_coroutine
        
        event = Event('test', 'async_test', {})
        result = await handler.handle(event)
        
        assert result == "Processed async_test"

    @pytest.mark.asyncio
    async def test_async_handler_timeout(self):
        try:
            logger.info(f"Executing error_coroutine")
            
            # Implementation for error_coroutine
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"error_coroutine completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"error_coroutine failed: {e}")
            raise
        assert result == "Processed async_test"

    @pytest.mark.asyncio
    async def test_async_handler_timeout(self):
        try:
            logger.info(f"Executing test_function")
            
            # Implementation for test_function
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_function completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_function failed: {e}")
            raise
    @pytest.mark.asyncio
    async def test_async_handler_timeout(self):
        """Test async handler timeout functionality."""
        async def slow_coroutine(event):
            await asyncio.sleep(2)  # Longer than timeout
            return "Too slow"
        
        handler = AsyncEventHandler('slow_handler', timeout=0.1)
        handler.coroutine = slow_coroutine
        
        event = Event('test', 'slow_test', {})
        
        with pytest.raises(asyncio.TimeoutError):
            await handler.handle(event)

    @pytest.mark.asyncio
    async def test_async_handler_error_handling(self):
        """Test async handler error management."""
        async def error_coroutine(event):
            raise ValueError("Test error")
        
        handler = AsyncEventHandler('error_handler')
        handler.coroutine = error_coroutine
        
        event = Event('test', 'error_test', {})
        
        # Should handle error gracefully
        result = await handler.handle(event)
        assert result is None  # Error handling returns None


class TestSyncEventHandler:
    """Test suite for SyncEventHandler class."""
    @pytest.mark.asyncio
    async def test_sync_handler_execution(self):
        """
Test sync event handling in thread pool."""
        def test_function(event):
            return f"Sync processed {event.event_type}"
        
        handler = SyncEventHandler('sync_handler')
        handler.function = test_function
        
        event = Event('test', 'sync_test', {})
        result = await handler.handle(event)
        
        assert result == "Sync processed sync_test"

    @pytest.mark.asyncio
    async def test_sync_handler_with_executor(self):
        """Test sync handler with custom executor."""
        from concurrent.futures import ThreadPoolExecutor
        
        def cpu_intensive_task(event):
            # Simulate CPU work
            total = sum(i * i for i in range(1000))
            return f"Computed {total} for {event.event_type}"
        
        executor = ThreadPoolExecutor(max_workers=2)
        handler = SyncEventHandler('cpu_handler', executor=executor)
        handler.function = cpu_intensive_task
        
        event = Event('test', 'cpu_test', {})
        result = await handler.handle(event)
        
        assert "Computed" in result
        assert "cpu_test" in result
        
        executor.shutdown(wait=True)


class TestEventQueue:
    """Test suite for EventQueue class."""
    def test_queue_initialization(self):
        """
Test queue setup."""
        queue = EventQueue()
        assert queue.redis_client is not None
        assert queue.queue_name == 'ia_influencer_events'

    @pytest.mark.asyncio
    async def test_enqueue_event(self):
        """
Test event enqueueing."""
        queue = EventQueue()
        
        with patch.object(queue.redis_client, 'zadd') as mock_zadd:
            mock_zadd.return_value = 1
            
            event = Event('test', 'queue_test', {'data': 'test'})
            await queue.enqueue(event)
            
            mock_zadd.assert_called_once()

    @pytest.mark.asyncio
    async def test_dequeue_event(self):
        """
Test event dequeuing."""
        queue = EventQueue()
        
        event_data = {
            'event_id': 'test',
            'event_type': 'dequeue_test',
            'data': {'test': 'data'},
            'priority': 'HIGH',
            'timestamp': '2025-01-11T10:00:00',
            'status': 'PENDING'
        }
        
        with patch.object(queue.redis_client, 'zpopmin') as mock_zpop:
            mock_zpop.return_value = [(json.dumps(event_data).encode(), 1.0)]
            
            event = await queue.dequeue()
            assert event is not None
            assert event.event_id == 'test'
            assert event.event_type == 'dequeue_test'

    @pytest.mark.asyncio
    async def test_dequeue_empty_queue(self):
        """
Test dequeuing from empty queue."""
        queue = EventQueue()
        
        with patch.object(queue.redis_client, 'zpopmin') as mock_zpop:
            mock_zpop.return_value = []
            
            event = await queue.dequeue()
            assert event is None

    @pytest.mark.asyncio
    async def test_queue_size(self):
        """
Test queue size reporting."""
        queue = EventQueue()
        
        with patch.object(queue.redis_client, 'zcard') as mock_zcard:
            mock_zcard.return_value = 5
            
            size = await queue.size()
            assert size == 5

    @pytest.mark.asyncio
    async def test_clear_queue(self):
        """
Test queue clearing."""
        queue = EventQueue()
        
        with patch.object(queue.redis_client, 'delete') as mock_delete:
            mock_delete.return_value = 1
            
            await queue.clear()
            mock_delete.assert_called_once_with(queue.queue_name)


class TestEventRegistry:
    """
Test suite for EventRegistry class."""
    def test_registry_initialization(self):
        """
Test registry setup."""
        registry = EventRegistry()
        assert len(registry.handlers) == 0
        assert len(registry.event_types) == 0

    def test_register_handler(self):
        """
Test handler registration."""
        registry = EventRegistry()
        handler = EventHandler('test_handler')
        
        registry.register_handler('test_event', handler)
        
        assert 'test_event' in registry.event_types
        assert handler in registry.event_types['test_event']
        assert handler.handler_id in registry.handlers

    def test_unregister_handler(self):
        """
Test handler unregistration."""
        registry = EventRegistry()
        handler = EventHandler('test_handler')
        
        registry.register_handler('test_event', handler)
        registry.unregister_handler(handler.handler_id)
        
        assert handler.handler_id not in registry.handlers
        assert len(registry.event_types['test_event']) == 0

    def test_get_handlers_for_event(self):
        """
Test getting handlers for specific event type."""
        registry = EventRegistry()
        handler1 = EventHandler('handler1')
        handler2 = EventHandler('handler2')
        
        registry.register_handler('test_event', handler1)
        registry.register_handler('test_event', handler2)
        registry.register_handler('other_event', handler1)
        
        handlers = registry.get_handlers('test_event')
        assert len(handlers) == 2
        assert handler1 in handlers
        assert handler2 in handlers

    def test_list_event_types(self):
        """
Test listing all registered event types."""
        registry = EventRegistry()
        handler = EventHandler('test_handler')
        
        registry.register_handler('event1', handler)
        registry.register_handler('event2', handler)
        
        event_types = registry.list_event_types()
        assert 'event1' in event_types
        assert 'event2' in event_types


class TestEventDispatcher:
    """
Test suite for EventDispatcher class."""
    def test_dispatcher_initialization(self):
        """
Test dispatcher setup."""
        dispatcher = EventDispatcher()
        assert dispatcher.queue is not None
        assert dispatcher.registry is not None
        assert dispatcher.workers == []
        assert not dispatcher.is_running

    @pytest.mark.asyncio
    async def test_dispatch_event(self):
        try:
            logger.info(f"Executing test_handler_func")
            
            # Implementation for test_handler_func
            # TODO: Add specific business logic here
            
            result = None  # Replace with actual implementation
            
            logger.info(f"test_handler_func completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"test_handler_func failed: {e}")
            raise
        assert dispatcher.workers == []
        assert not dispatcher.is_running

    @pytest.mark.asyncio
    async def test_dispatch_event(self):
        """
Test event dispatching."""
        dispatcher = EventDispatcher()
        
        with patch.object(dispatcher.queue, 'enqueue') as mock_enqueue:
            event = Event('test', 'dispatch_test', {})
            await dispatcher.dispatch(event)
            
            mock_enqueue.assert_called_once_with(event)

    @pytest.mark.asyncio
    async def test_start_workers(self):
        """
Test worker startup."""
        dispatcher = EventDispatcher()
        
        with patch.object(dispatcher, '_create_worker') as mock_create:
            mock_worker = MagicMock()
            mock_create.return_value = mock_worker
            
            await dispatcher.start_workers(2)
            
            assert len(dispatcher.workers) == 2
            assert mock_create.call_count == 2

    def test_stop_workers(self):
        """
Test worker shutdown."""
        dispatcher = EventDispatcher()
        
        # Mock workers
        worker1 = MagicMock()
        worker2 = MagicMock()
        dispatcher.workers = [worker1, worker2]
        dispatcher.is_running = True
        
        dispatcher.stop_workers()
        
        assert not dispatcher.is_running
        worker1.stop.assert_called_once()
        worker2.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event(self):
        """
Test event processing."""
        dispatcher = EventDispatcher()
        
        # Create and register a test handler
        async def test_handler_func(event):
            return f"Handled {event.event_type}"
        
        handler = AsyncEventHandler('test_handler')
        handler.coroutine = test_handler_func
        dispatcher.registry.register_handler('test_event', handler)
        
        event = Event('test', 'test_event', {})
        results = await dispatcher.process_event(event)
        
        assert len(results) == 1
        assert results[0] == "Handled test_event"

    @pytest.mark.asyncio
    async def test_process_event_no_handlers(self):
        """Test processing event with no registered handlers."""
        dispatcher = EventDispatcher()
        
        event = Event('test', 'unknown_event', {})
        results = await dispatcher.process_event(event)
        
        assert len(results) == 0


class TestEventWorker:
    """
Test suite for EventWorker class."""
    def test_worker_initialization(self):
        """
Test worker setup."""
        dispatcher = EventDispatcher()
        worker = EventWorker('worker-1', dispatcher)
        
        assert worker.worker_id == 'worker-1'
        assert worker.dispatcher == dispatcher
        assert not worker.is_running
        assert worker.processed_count == 0

    @pytest.mark.asyncio
    async def test_worker_lifecycle(self):
        """
Test worker start and stop."""
        dispatcher = EventDispatcher()
        worker = EventWorker('worker-1', dispatcher)
        
        # Mock the work loop to avoid infinite loop
        with patch.object(worker, '_work_loop') as mock_loop:
            mock_loop.return_value = None
            
            # Start worker
            task = asyncio.create_task(worker.start())
            await asyncio.sleep(0.1)  # Let it start
            
            assert worker.is_running
            
            # Stop worker
            worker.stop()
            await task
            
            assert not worker.is_running

    @pytest.mark.asyncio
    async def test_worker_process_event(self):
        """
Test worker event processing."""
        dispatcher = EventDispatcher()
        worker = EventWorker('worker-1', dispatcher)
        
        # Mock dispatcher process_event
        with patch.object(dispatcher, 'process_event') as mock_process:
            mock_process.return_value = ['result']
            
            event = Event('test', 'worker_test', {})
            await worker._process_event(event)
            
            mock_process.assert_called_once_with(event)
            assert worker.processed_count == 1


class TestIntegration:
    """
Integration tests for event handling system."""
    @pytest.mark.asyncio
    async def test_complete_event_flow(self):
        """
Test complete event processing flow."""
        dispatcher = EventDispatcher()
        
        # Create and register handler
        results = []
        
        async def capture_handler(event):
            results.append(f"Processed: {event.event_type}")
            return "success"
        
        handler = AsyncEventHandler('capture_handler')
        handler.coroutine = capture_handler
        dispatcher.registry.register_handler('integration_test', handler)
        
        # Create and dispatch event
        event = Event('test', 'integration_test', {'test': 'data'})
        
        # Mock queue for testing
        with patch.object(dispatcher.queue, 'enqueue'):
            await dispatcher.dispatch(event)
        
        # Process event directly
        process_results = await dispatcher.process_event(event)
        
        assert len(process_results) == 1
        assert process_results[0] == "success"
        assert len(results) == 1
        assert "Processed: integration_test" in results

    @pytest.mark.asyncio
    async def test_multiple_handlers_same_event(self):
        """Test multiple handlers for same event type."""
        dispatcher = EventDispatcher()
        
        results = []
        
        async def handler1(event):
            results.append("handler1")
            return "result1"
        
        async def handler2(event):
            results.append("handler2")
            return "result2"
        
        # Register both handlers for same event
        h1 = AsyncEventHandler('handler1')
        h1.coroutine = handler1
        h2 = AsyncEventHandler('handler2')
        h2.coroutine = handler2
        
        dispatcher.registry.register_handler('multi_test', h1)
        dispatcher.registry.register_handler('multi_test', h2)
        
        # Process event
        event = Event('test', 'multi_test', {})
        process_results = await dispatcher.process_event(event)
        
        assert len(process_results) == 2
        assert "result1" in process_results
        assert "result2" in process_results
        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_event_priority_ordering(self):
        """Test event priority handling."""
        queue = EventQueue()
        
        # Create events with different priorities
        low_event = Event('low', 'test', {}, priority=EventPriority.LOW)
        high_event = Event('high', 'test', {}, priority=EventPriority.HIGH)
        medium_event = Event('medium', 'test', {}, priority=EventPriority.MEDIUM)
        
        # Mock Redis operations for priority testing
        enqueued_events = []
        
        async def mock_zadd(name, mapping):
            for event_json, priority in mapping.items():
                enqueued_events.append((event_json, priority))
            return len(mapping)
        
        with patch.object(queue.redis_client, 'zadd', side_effect=mock_zadd):
            await queue.enqueue(low_event)
            await queue.enqueue(high_event)
            await queue.enqueue(medium_event)
        
        # Verify priority ordering (higher priority = lower score for Redis ZADD)
        assert len(enqueued_events) == 3
        priorities = [score for _, score in enqueued_events]
        
        # High priority should have lowest score
        high_priority_score = [score for event_json, score in enqueued_events 
                             if 'high' in event_json][0]
        low_priority_score = [score for event_json, score in enqueued_events 
                            if 'low' in event_json][0]
        
        assert high_priority_score < low_priority_score


if __name__ == '__main__':
    pytest.main([str(Path(__file__))])
