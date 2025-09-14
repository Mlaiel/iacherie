"""
🌐 Distributed AI Agent Template - Enterprise Distributed Computing Framework
============================================================================

🎖️ LEAD DEV IA + ML ENGINEER - Advanced Distributed AI Processing Agent
- Distributed computing across multiple nodes/clusters
- Fault-tolerant distributed task execution
- Load balancing and resource optimization
- Distributed ML model training and inference
- Inter-node communication and coordination
- Elastic scaling and auto-discovery

Author: Expert Team (Lead Dev IA + ML Engineer)
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import threading
import hashlib
from collections import defaultdict, deque
from abc import ABC, abstractmethod
import numpy as np
from pydantic import BaseModel, Field
import uuid
import socket
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import multiprocessing
import pickle
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    """Node status in distributed system"""
    ACTIVE = "active"
    BUSY = "busy"
    IDLE = "idle"
    OFFLINE = "offline"
    FAILED = "failed"
    MAINTENANCE = "maintenance"

class TaskStatus(Enum):
    """Distributed task status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"
    RESOURCE_AWARE = "resource_aware"

@dataclass
class NodeInfo:
    """Information about a distributed node"""
    node_id: str
    hostname: str
    ip_address: str
    port: int
    capabilities: List[str]
    resources: Dict[str, Any]  # CPU, memory, GPU info
    status: NodeStatus = NodeStatus.OFFLINE
    last_heartbeat: datetime = field(default_factory=datetime.now)
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_task_time: float = 0.0
    load_score: float = 0.0

@dataclass
class DistributedTask:
    """Distributed task definition"""
    task_id: str
    task_type: str
    data: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    max_retries: int = 3
    timeout_seconds: int = 300
    required_capabilities: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    assigned_node: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    execution_time: Optional[float] = None

@dataclass
class ClusterStats:
    """Cluster-wide statistics"""
    total_nodes: int = 0
    active_nodes: int = 0
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_task_time: float = 0.0
    total_throughput: float = 0.0
    cluster_utilization: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class DistributedTaskProcessor(ABC):
    """Abstract distributed task processor"""
    
    @abstractmethod
    async def process_task(self, task: DistributedTask) -> Any:
        """Process a distributed task"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get processor capabilities"""
        pass
    
    @abstractmethod
    def get_resource_requirements(self, task: DistributedTask) -> Dict[str, Any]:
        """Get resource requirements for task"""
        pass

class MLModelTrainingProcessor(DistributedTaskProcessor):
    """Distributed ML model training processor"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
        self.model_cache = {}
    
    async def process_task(self, task: DistributedTask) -> Any:
        """Process ML training task"""
        try:
            training_data = task.data.get("training_data", [])
            model_config = task.data.get("model_config", {})
            model_type = task.data.get("model_type", "classification")
            
            logger.info(f"Training {model_type} model with {len(training_data)} samples")
            
            # Simulate model training
            training_result = await self._train_model(training_data, model_config, model_type)
            
            return training_result
            
        except Exception as e:
            logger.error(f"ML training error: {str(e)}")
            raise
    
    async def _train_model(self, training_data: List, model_config: Dict, model_type: str) -> Dict[str, Any]:
        """Train ML model"""
        # Simulate training time based on data size
        training_time = len(training_data) * 0.01  # Scale with data
        await asyncio.sleep(min(training_time, 5.0))  # Cap at 5 seconds for demo
        
        # Simulate training metrics
        accuracy = np.random.uniform(0.75, 0.95)
        loss = np.random.uniform(0.05, 0.25)
        
        # Generate model artifact (simplified)
        model_artifact = {
            "model_id": str(uuid.uuid4()),
            "model_type": model_type,
            "parameters": {"weights": "base64_encoded_weights"},
            "metadata": {
                "training_samples": len(training_data),
                "accuracy": accuracy,
                "loss": loss,
                "training_time": training_time
            }
        }
        
        return {
            "model_artifact": model_artifact,
            "metrics": {
                "accuracy": accuracy,
                "loss": loss,
                "training_time": training_time
            },
            "status": "completed"
        }
    
    def get_capabilities(self) -> List[str]:
        return ["ml_training", "deep_learning", "classification", "regression"]
    
    def get_resource_requirements(self, task: DistributedTask) -> Dict[str, Any]:
        data_size = len(task.data.get("training_data", []))
        return {
            "cpu_cores": min(8, max(2, data_size // 1000)),
            "memory_gb": min(16, max(4, data_size // 500)),
            "gpu_required": data_size > 10000,
            "estimated_time_minutes": data_size * 0.001
        }

class ContentAnalysisProcessor(DistributedTaskProcessor):
    """Distributed content analysis processor"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
    
    async def process_task(self, task: DistributedTask) -> Any:
        """Process content analysis task"""
        try:
            content_items = task.data.get("content_items", [])
            analysis_types = task.data.get("analysis_types", ["sentiment", "topics"])
            
            logger.info(f"Analyzing {len(content_items)} content items")
            
            results = []
            for item in content_items:
                analysis_result = await self._analyze_content(item, analysis_types)
                results.append(analysis_result)
            
            return {
                "results": results,
                "total_analyzed": len(content_items),
                "analysis_types": analysis_types,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Content analysis error: {str(e)}")
            raise
    
    async def _analyze_content(self, content_item: Dict[str, Any], analysis_types: List[str]) -> Dict[str, Any]:
        """Analyze single content item"""
        content = content_item.get("content", "")
        result = {"content_id": content_item.get("id", "unknown")}
        
        if "sentiment" in analysis_types:
            result["sentiment"] = await self._analyze_sentiment(content)
        
        if "topics" in analysis_types:
            result["topics"] = await self._extract_topics(content)
        
        if "entities" in analysis_types:
            result["entities"] = await self._extract_entities(content)
        
        return result
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment"""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "awesome", "love", "amazing"]
        negative_words = ["bad", "hate", "terrible", "awful"]
        
        words = content.lower().split()
        positive_score = sum(1 for word in words if word in positive_words)
        negative_score = sum(1 for word in words if word in negative_words)
        
        if positive_score > negative_score:
            sentiment = "positive"
            confidence = min(0.95, positive_score / max(1, len(words)) * 10)
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = min(0.95, negative_score / max(1, len(words)) * 10)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {"sentiment": sentiment, "confidence": confidence}
    
    async def _extract_topics(self, content: str) -> List[Dict[str, Any]]:
        """Extract topics"""
        topics = []
        if "technology" in content.lower():
            topics.append({"topic": "technology", "relevance": 0.8})
        if "entertainment" in content.lower():
            topics.append({"topic": "entertainment", "relevance": 0.7})
        return topics
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract entities"""
        entities = []
        words = content.split()
        for word in words:
            if word.istitle() and len(word) > 2:
                entities.append({"text": word, "type": "PERSON", "confidence": 0.7})
        return entities[:5]  # Limit to 5 entities
    
    def get_capabilities(self) -> List[str]:
        return ["content_analysis", "nlp", "sentiment_analysis", "topic_extraction"]
    
    def get_resource_requirements(self, task: DistributedTask) -> Dict[str, Any]:
        content_count = len(task.data.get("content_items", []))
        return {
            "cpu_cores": min(4, max(1, content_count // 100)),
            "memory_gb": min(8, max(2, content_count // 50)),
            "gpu_required": False,
            "estimated_time_minutes": content_count * 0.05
        }

class ImageProcessingProcessor(DistributedTaskProcessor):
    """Distributed image processing processor"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        self.config = config or {}
    
    async def process_task(self, task: DistributedTask) -> Any:
        """Process image processing task"""
        try:
            image_items = task.data.get("image_items", [])
            operations = task.data.get("operations", ["resize", "enhance"])
            
            logger.info(f"Processing {len(image_items)} images")
            
            results = []
            for item in image_items:
                processing_result = await self._process_image(item, operations)
                results.append(processing_result)
            
            return {
                "results": results,
                "total_processed": len(image_items),
                "operations": operations,
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Image processing error: {str(e)}")
            raise
    
    async def _process_image(self, image_item: Dict[str, Any], operations: List[str]) -> Dict[str, Any]:
        """Process single image"""
        # Simulate image processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        result = {"image_id": image_item.get("id", "unknown")}
        
        if "resize" in operations:
            result["resized_variants"] = [
                {"size": "1080x1080", "format": "jpg"},
                {"size": "500x500", "format": "webp"}
            ]
        
        if "enhance" in operations:
            result["enhancements"] = ["brightness_boost", "contrast_enhancement"]
        
        if "analyze" in operations:
            result["analysis"] = {
                "objects": ["person", "background"],
                "colors": ["blue", "white"],
                "quality_score": 0.85
            }
        
        return result
    
    def get_capabilities(self) -> List[str]:
        return ["image_processing", "computer_vision", "image_enhancement"]
    
    def get_resource_requirements(self, task: DistributedTask) -> Dict[str, Any]:
        image_count = len(task.data.get("image_items", []))
        return {
            "cpu_cores": min(6, max(2, image_count // 50)),
            "memory_gb": min(12, max(4, image_count // 25)),
            "gpu_required": image_count > 100,
            "estimated_time_minutes": image_count * 0.1
        }

class DistributedAgent:
    """🌐 Advanced Distributed AI Agent for Multi-Node Processing"""
    
    def __init__(self, config -> None: Dict[str, Any] = None) -> None:
        """Initialize Distributed Agent"""
        self.config = config or {}
        self.node_id = self.config.get("node_id", str(uuid.uuid4()))
        self.is_coordinator = self.config.get("is_coordinator", True)
        
        # Network configuration
        self.hostname = socket.gethostname()
        self.ip_address = self._get_local_ip()
        self.port = self.config.get("port", 8080)
        
        # Node management
        self.nodes = {}  # node_id -> NodeInfo
        self.local_node = self._create_local_node()
        self.processors = {}
        
        # Task management
        self.task_queue = asyncio.Queue()
        self.active_tasks = {}
        self.completed_tasks = {}
        self.load_balancer_strategy = LoadBalancingStrategy.RESOURCE_AWARE
        
        # Cluster coordination
        self.is_running = False
        self.heartbeat_interval = 30  # seconds
        self.coordination_tasks = []
        
        # Statistics
        self.cluster_stats = ClusterStats()
        
        logger.info(f"🌐 Distributed Agent initialized - Node ID: {self.node_id}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def _create_local_node(self) -> NodeInfo:
        """Create local node information"""
        return NodeInfo(
            node_id=self.node_id,
            hostname=self.hostname,
            ip_address=self.ip_address,
            port=self.port,
            capabilities=[],
            resources={
                "cpu_cores": multiprocessing.cpu_count(),
                "memory_gb": 16,  # Simplified
                "gpu_count": 0,
                "disk_gb": 500
            },
            status=NodeStatus.ACTIVE
        )
    
    def register_processor(self, processor_name -> None: str, processor -> None: DistributedTaskProcessor) -> None:
        """Register a task processor"""
        self.processors[processor_name] = processor
        
        # Update local node capabilities
        capabilities = processor.get_capabilities()
        for capability in capabilities:
            if capability not in self.local_node.capabilities:
                self.local_node.capabilities.append(capability)
        
        logger.info(f"Registered processor: {processor_name} with capabilities: {capabilities}")
    
    async def start(self, cluster_nodes -> None: List[Dict[str, Any]] = None) -> None:
        """Start the distributed agent"""
        logger.info(f"Starting Distributed Agent on {self.hostname}:{self.port}")
        
        self.is_running = True
        
        # Register with cluster
        if cluster_nodes:
            await self._join_cluster(cluster_nodes)
        
        # Start coordination tasks
        if self.is_coordinator:
            coordinator_task = asyncio.create_task(self._coordinator_loop())
            self.coordination_tasks.append(coordinator_task)
        
        # Start worker tasks
        worker_task = asyncio.create_task(self._worker_loop())
        self.coordination_tasks.append(worker_task)
        
        # Start heartbeat
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self.coordination_tasks.append(heartbeat_task)
        
        # Start HTTP server for inter-node communication
        server_task = asyncio.create_task(self._start_http_server())
        self.coordination_tasks.append(server_task)
        
        logger.info("✅ Distributed Agent started successfully")
    
    async def stop(self) -> None:
        """Stop the distributed agent"""
        logger.info("Stopping Distributed Agent")
        
        self.is_running = False
        
        # Cancel all coordination tasks
        for task in self.coordination_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.coordination_tasks, return_exceptions=True)
        
        logger.info("✅ Distributed Agent stopped")
    
    async def _join_cluster(self, cluster_nodes -> None: List[Dict[str, Any]]) -> None:
        """Join existing cluster"""
        logger.info(f"Joining cluster with {len(cluster_nodes)} known nodes")
        
        for node_config in cluster_nodes:
            node_id = node_config.get("node_id")
            if node_id and node_id != self.node_id:
                node_info = NodeInfo(
                    node_id=node_id,
                    hostname=node_config.get("hostname", "unknown"),
                    ip_address=node_config.get("ip_address", "127.0.0.1"),
                    port=node_config.get("port", 8080),
                    capabilities=node_config.get("capabilities", []),
                    resources=node_config.get("resources", {}),
                    status=NodeStatus.ACTIVE
                )
                self.nodes[node_id] = node_info
        
        # Register local node with cluster
        self.nodes[self.node_id] = self.local_node
    
    async def _coordinator_loop(self) -> None:
        """Main coordinator loop for task distribution"""
        logger.info("Started coordinator loop")
        
        while self.is_running:
            try:
                # Process pending tasks
                await self._distribute_tasks()
                
                # Update cluster statistics
                await self._update_cluster_stats()
                
                # Perform health checks
                await self._health_check_nodes()
                
                # Rebalance load if needed
                await self._rebalance_load()
                
                await asyncio.sleep(5.0)  # Coordinator cycle
                
            except Exception as e:
                logger.error(f"Coordinator loop error: {str(e)}")
    
    async def _worker_loop(self) -> None:
        """Main worker loop for task execution"""
        logger.info("Started worker loop")
        
        while self.is_running:
            try:
                # Get task from local queue
                try:
                    task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    await self._execute_task(task)
                except asyncio.TimeoutError:
                    continue  # No tasks available
                
            except Exception as e:
                logger.error(f"Worker loop error: {str(e)}")
    
    async def _heartbeat_loop(self) -> None:
        """Send periodic heartbeats to cluster"""
        while self.is_running:
            try:
                # Update local node status
                self.local_node.last_heartbeat = datetime.now()
                self.local_node.load_score = await self._calculate_load_score()
                
                # Send heartbeat to other nodes
                await self._send_heartbeat()
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"Heartbeat error: {str(e)}")
    
    async def _start_http_server(self) -> None:
        """Start HTTP server for inter-node communication"""
        from aiohttp import web, web_runner
        
        app = web.Application()
        app.router.add_post('/tasks', self._handle_task_request)
        app.router.add_post('/heartbeat', self._handle_heartbeat)
        app.router.add_get('/status', self._handle_status_request)
        
        runner = web_runner.AppRunner(app)
        await runner.setup()
        
        site = web_runner.TCPSite(runner, self.ip_address, self.port)
        await site.start()
        
        logger.info(f"HTTP server started on {self.ip_address}:{self.port}")
    
    async def _handle_task_request(self, request) -> None:
        """Handle incoming task request"""
        from aiohttp import web
        
        try:
            task_data = await request.json()
            
            # Create distributed task
            task = DistributedTask(
                task_id=task_data.get("task_id", str(uuid.uuid4())),
                task_type=task_data.get("task_type"),
                data=task_data.get("data", {}),
                priority=TaskPriority(task_data.get("priority", "medium")),
                required_capabilities=task_data.get("required_capabilities", []),
                resource_requirements=task_data.get("resource_requirements", {})
            )
            
            # Add to local queue
            await self.task_queue.put(task)
            
            return web.json_response({
                "status": "accepted",
                "task_id": task.task_id,
                "node_id": self.node_id
            })
            
        except Exception as e:
            return web.json_response({
                "error": str(e)
            }, status=400)
    
    async def _handle_heartbeat(self, request) -> None:
        """Handle heartbeat from other nodes"""
        from aiohttp import web
        
        try:
            heartbeat_data = await request.json()
            node_id = heartbeat_data.get("node_id")
            
            if node_id and node_id in self.nodes:
                node = self.nodes[node_id]
                node.last_heartbeat = datetime.now()
                node.status = NodeStatus(heartbeat_data.get("status", "active"))
                node.load_score = heartbeat_data.get("load_score", 0.0)
                node.active_tasks = heartbeat_data.get("active_tasks", 0)
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
    
    async def _handle_status_request(self, request) -> None:
        """Handle status request"""
        from aiohttp import web
        
        status = {
            "node_id": self.node_id,
            "status": self.local_node.status.value,
            "capabilities": self.local_node.capabilities,
            "resources": self.local_node.resources,
            "active_tasks": self.local_node.active_tasks,
            "completed_tasks": self.local_node.completed_tasks,
            "load_score": self.local_node.load_score,
            "is_coordinator": self.is_coordinator
        }
        
        return web.json_response(status)
    
    async def _distribute_tasks(self) -> None:
        """Distribute tasks to available nodes"""
        if not self.is_coordinator:
            return
        
        # This is a simplified task distribution logic
        # In production, this would be more sophisticated
        pass
    
    async def _execute_task(self, task -> None: DistributedTask) -> None:
        """Execute a task locally"""
        logger.info(f"Executing task {task.task_id} of type {task.task_type}")
        
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        task.assigned_node = self.node_id
        self.active_tasks[task.task_id] = task
        
        # Update local node stats
        self.local_node.active_tasks += 1
        
        start_time = time.time()
        
        try:
            # Find appropriate processor
            processor = self.processors.get(task.task_type)
            if not processor:
                raise ValueError(f"No processor available for task type: {task.task_type}")
            
            # Execute task
            result = await processor.process_task(task)
            
            # Update task with result
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.execution_time = time.time() - start_time
            
            logger.info(f"Task {task.task_id} completed in {task.execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {str(e)}")
            task.error_message = str(e)
            task.status = TaskStatus.FAILED
            task.execution_time = time.time() - start_time
            
            # Handle retry logic
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRYING
                # Re-queue task with delay
                await asyncio.sleep(2.0 ** task.retry_count)  # Exponential backoff
                await self.task_queue.put(task)
                return
        
        finally:
            task.completed_at = datetime.now()
            
            # Update local node stats
            self.local_node.active_tasks -= 1
            if task.status == TaskStatus.COMPLETED:
                self.local_node.completed_tasks += 1
            else:
                self.local_node.failed_tasks += 1
            
            # Move to completed tasks
            self.completed_tasks[task.task_id] = task
            self.active_tasks.pop(task.task_id, None)
    
    async def _calculate_load_score(self) -> float:
        """Calculate current load score for the node"""
        # Simplified load calculation
        cpu_usage = self.local_node.active_tasks / max(1, self.local_node.resources.get("cpu_cores", 1))
        memory_usage = 0.5  # Simplified
        
        return min(1.0, (cpu_usage * 0.7) + (memory_usage * 0.3))
    
    async def _send_heartbeat(self) -> None:
        """Send heartbeat to other nodes"""
        heartbeat_data = {
            "node_id": self.node_id,
            "status": self.local_node.status.value,
            "load_score": self.local_node.load_score,
            "active_tasks": self.local_node.active_tasks,
            "capabilities": self.local_node.capabilities,
            "timestamp": datetime.now().isoformat()
        }
        
        # Send to all known nodes (simplified)
        for node_id, node in self.nodes.items():
            if node_id != self.node_id and node.status == NodeStatus.ACTIVE:
                try:
                    # In production, you'd use proper HTTP client
                    # This is simplified for demonstration
                    pass
                except Exception as e:
                    logger.warning(f"Failed to send heartbeat to {node_id}: {str(e)}")
    
    async def _update_cluster_stats(self) -> None:
        """Update cluster-wide statistics"""
        if not self.is_coordinator:
            return
        
        active_nodes = sum(1 for node in self.nodes.values() if node.status == NodeStatus.ACTIVE)
        total_completed = sum(node.completed_tasks for node in self.nodes.values())
        total_failed = sum(node.failed_tasks for node in self.nodes.values())
        
        self.cluster_stats.total_nodes = len(self.nodes)
        self.cluster_stats.active_nodes = active_nodes
        self.cluster_stats.completed_tasks = total_completed
        self.cluster_stats.failed_tasks = total_failed
        self.cluster_stats.total_tasks = total_completed + total_failed
        self.cluster_stats.last_updated = datetime.now()
        
        # Calculate cluster utilization
        if self.cluster_stats.total_nodes > 0:
            total_load = sum(node.load_score for node in self.nodes.values())
            self.cluster_stats.cluster_utilization = total_load / self.cluster_stats.total_nodes
    
    async def _health_check_nodes(self) -> None:
        """Perform health checks on cluster nodes"""
        current_time = datetime.now()
        
        for node_id, node in self.nodes.items():
            if node_id == self.node_id:
                continue
            
            # Check if node is still alive
            time_since_heartbeat = (current_time - node.last_heartbeat).total_seconds()
            
            if time_since_heartbeat > self.heartbeat_interval * 3:  # 3x heartbeat interval
                if node.status == NodeStatus.ACTIVE:
                    logger.warning(f"Node {node_id} appears to be offline")
                    node.status = NodeStatus.OFFLINE
    
    async def _rebalance_load(self) -> None:
        """Rebalance load across cluster nodes"""
        if not self.is_coordinator:
            return
        
        # Simplified load balancing logic
        # In production, this would redistribute tasks based on load
        overloaded_nodes = [
            node for node in self.nodes.values()
            if node.load_score > 0.8 and node.status == NodeStatus.ACTIVE
        ]
        
        underloaded_nodes = [
            node for node in self.nodes.values()
            if node.load_score < 0.3 and node.status == NodeStatus.ACTIVE
        ]
        
        if overloaded_nodes and underloaded_nodes:
            logger.info(f"Load balancing: {len(overloaded_nodes)} overloaded, {len(underloaded_nodes)} underloaded")
    
    async def submit_task(self, task: DistributedTask) -> str:
        """Submit a task to the distributed system"""
        if self.is_coordinator:
            # Find best node for task
            best_node = await self._find_best_node(task)
            
            if best_node and best_node.node_id != self.node_id:
                # Send task to remote node
                await self._send_task_to_node(task, best_node)
            else:
                # Execute locally
                await self.task_queue.put(task)
        else:
            # Send to coordinator or execute locally
            await self.task_queue.put(task)
        
        return task.task_id
    
    async def _find_best_node(self, task: DistributedTask) -> Optional[NodeInfo]:
        """Find the best node to execute a task"""
        suitable_nodes = []
        
        for node in self.nodes.values():
            if (node.status == NodeStatus.ACTIVE and
                all(cap in node.capabilities for cap in task.required_capabilities)):
                suitable_nodes.append(node)
        
        if not suitable_nodes:
            return None
        
        # Use load balancing strategy
        if self.load_balancer_strategy == LoadBalancingStrategy.LEAST_LOADED:
            return min(suitable_nodes, key=lambda n: n.load_score)
        elif self.load_balancer_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            # Simplified round robin
            return suitable_nodes[len(self.completed_tasks) % len(suitable_nodes)]
        else:
            # Resource aware (default)
            return min(suitable_nodes, key=lambda n: n.load_score)
    
    async def _send_task_to_node(self, task -> None: DistributedTask, node -> None: NodeInfo) -> None:
        """Send task to a specific node"""
        try:
            task_data = {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "data": task.data,
                "priority": task.priority.name.lower(),
                "required_capabilities": task.required_capabilities,
                "resource_requirements": task.resource_requirements
            }
            
            # In production, use proper HTTP client
            # async with aiohttp.ClientSession() as session:
            #     url = f"http://{node.ip_address}:{node.port}/tasks"
            #     async with session.post(url, json=task_data) as response:
            #         if response.status == 200:
            #             logger.info(f"Task {task.task_id} sent to node {node.node_id}")
            
            logger.info(f"Would send task {task.task_id} to node {node.node_id}")
            
        except Exception as e:
            logger.error(f"Failed to send task to node {node.node_id}: {str(e)}")
            # Fallback to local execution
            await self.task_queue.put(task)
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get cluster status and statistics"""
        node_statuses = {}
        for node_id, node in self.nodes.items():
            node_statuses[node_id] = {
                "hostname": node.hostname,
                "status": node.status.value,
                "capabilities": node.capabilities,
                "active_tasks": node.active_tasks,
                "completed_tasks": node.completed_tasks,
                "failed_tasks": node.failed_tasks,
                "load_score": node.load_score,
                "last_heartbeat": node.last_heartbeat.isoformat()
            }
        
        return {
            "cluster_stats": {
                "total_nodes": self.cluster_stats.total_nodes,
                "active_nodes": self.cluster_stats.active_nodes,
                "total_tasks": self.cluster_stats.total_tasks,
                "completed_tasks": self.cluster_stats.completed_tasks,
                "failed_tasks": self.cluster_stats.failed_tasks,
                "cluster_utilization": self.cluster_stats.cluster_utilization
            },
            "local_node": {
                "node_id": self.node_id,
                "status": self.local_node.status.value,
                "is_coordinator": self.is_coordinator,
                "active_tasks": len(self.active_tasks),
                "queue_size": self.task_queue.qsize()
            },
            "nodes": node_statuses
        }

# Utility functions
def create_ml_training_task(training_data: List[Dict], model_config: Dict = None) -> DistributedTask:
    """Create ML training distributed task"""
    return DistributedTask(
        task_id=str(uuid.uuid4()),
        task_type="ml_training",
        data={
            "training_data": training_data,
            "model_config": model_config or {},
            "model_type": "classification"
        },
        priority=TaskPriority.HIGH,
        required_capabilities=["ml_training"],
        resource_requirements={"cpu_cores": 4, "memory_gb": 8}
    )

def create_content_analysis_task(content_items: List[Dict]) -> DistributedTask:
    """Create content analysis distributed task"""
    return DistributedTask(
        task_id=str(uuid.uuid4()),
        task_type="content_analysis",
        data={
            "content_items": content_items,
            "analysis_types": ["sentiment", "topics", "entities"]
        },
        priority=TaskPriority.MEDIUM,
        required_capabilities=["content_analysis"],
        resource_requirements={"cpu_cores": 2, "memory_gb": 4}
    )

# Usage Example and Template Testing
async def main() -> None:
    """Example usage of Distributed Agent Template"""
    
    # Initialize the distributed agent
    agent = DistributedAgent(config={
        "node_id": "node_001",
        "is_coordinator": True,
        "port": 8080
    })
    
    # Register processors
    ml_processor = MLModelTrainingProcessor()
    content_processor = ContentAnalysisProcessor()
    image_processor = ImageProcessingProcessor()
    
    agent.register_processor("ml_training", ml_processor)
    agent.register_processor("content_analysis", content_processor)
    agent.register_processor("image_processing", image_processor)
    
    try:
        # For demo purposes, we'll simulate the distributed system
        print("🌐 Distributed Agent Demo")
        print(f"✅ Node initialized: {agent.node_id}")
        print(f"✅ Local capabilities: {agent.local_node.capabilities}")
        
        # Create sample tasks
        training_task = create_ml_training_task([
            {"features": [1, 2, 3], "label": "positive"},
            {"features": [4, 5, 6], "label": "negative"}
        ])
        
        content_task = create_content_analysis_task([
            {"id": "content_001", "content": "This is amazing AI technology!"},
            {"id": "content_002", "content": "I hate this terrible product."}
        ])
        
        print(f"\n🔄 Submitting tasks...")
        
        # Submit tasks (simulation)
        training_task_id = await agent.submit_task(training_task)
        content_task_id = await agent.submit_task(content_task)
        
        print(f"✅ ML training task submitted: {training_task_id}")
        print(f"✅ Content analysis task submitted: {content_task_id}")
        
        # Simulate task execution
        await agent._execute_task(training_task)
        await agent._execute_task(content_task)
        
        # Get cluster status
        status = agent.get_cluster_status()
        
        print(f"\n📊 Cluster Status:")
        print(f"  Total Nodes: {status['cluster_stats']['total_nodes']}")
        print(f"  Active Nodes: {status['cluster_stats']['active_nodes']}")
        print(f"  Completed Tasks: {status['cluster_stats']['completed_tasks']}")
        print(f"  Local Queue Size: {status['local_node']['queue_size']}")
        print(f"  Is Coordinator: {status['local_node']['is_coordinator']}")
        
        print(f"\n📈 Task Results:")
        for task_id, task in agent.completed_tasks.items():
            print(f"  Task {task_id[:8]}...")
            print(f"    Type: {task.task_type}")
            print(f"    Status: {task.status.value}")
            print(f"    Execution Time: {task.execution_time:.2f}s")
            if task.result:
                print(f"    Result Keys: {list(task.result.keys())}")
        
        print("\n✅ Distributed Agent demonstration completed!")
        
    except Exception as e:
        logger.error(f"Error in distributed demo: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("🌐 Distributed Agent Template demonstration completed!")