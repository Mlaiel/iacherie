"""
📦 Batch Processing AI Agent Template - Enterprise Batch Operations Framework
============================================================================

🎖️ LEAD DEV IA + ML ENGINEER - Advanced Batch Processing AI Agent
- Large-scale content processing and analysis
- Distributed batch job orchestration
- Parallel processing with resource optimization  
- ETL pipelines for AI model training
- Bulk content transformation and migration
- Scheduled analytics and reporting

Author: Expert Team (Lead Dev IA + ML Engineer)
Version: 1.0.0
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Union, Callable, Generator, Iterator
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import os
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from abc import ABC, abstractmethod
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field
import pickle
import hashlib
from pathlib import Path
import uuid
from queue import Queue
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Batch job status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class JobPriority(Enum):
    """Job priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ProcessingMode(Enum):
    """Processing execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL_THREADS = "parallel_threads"
    PARALLEL_PROCESSES = "parallel_processes"
    DISTRIBUTED = "distributed"

@dataclass
class BatchItem:
    """Individual item in a batch"""
    item_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_result: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    retry_count: int = 0

@dataclass
class BatchJob:
    """Batch processing job definition"""
    job_id: str
    job_name: str
    items: List[BatchItem]
    processor_config: Dict[str, Any]
    priority: JobPriority = JobPriority.MEDIUM
    max_retries: int = 3
    retry_delay: float = 5.0
    timeout_minutes: int = 60
    processing_mode: ProcessingMode = ProcessingMode.PARALLEL_THREADS
    checkpoint_interval: int = 100
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    progress: float = 0.0
    error_count: int = 0
    success_count: int = 0

@dataclass
class BatchResult:
    """Batch processing result"""
    job_id: str
    status: JobStatus
    total_items: int
    successful_items: int
    failed_items: int
    processing_time: float
    throughput: float  # items per second
    error_summary: List[Dict[str, Any]]
    checkpoint_data: Optional[Dict[str, Any]] = None

class BatchProcessor(ABC):
    """Abstract batch processor"""
    
    @abstractmethod
    async def process_item(self, item: BatchItem) -> BatchItem:
        """Process a single batch item"""
        pass
    
    @abstractmethod
    def get_processor_name(self) -> str:
        """Get processor name"""
        pass
    
    def validate_item(self, item: BatchItem) -> bool:
        """Validate item before processing"""
        return True
    
    def prepare_batch(self, items: List[BatchItem]) -> List[BatchItem]:
        """Prepare batch before processing"""
        return items

class ContentAnalysisProcessor(BatchProcessor):
    """Batch processor for content analysis"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.analysis_types = self.config.get("analysis_types", ["sentiment", "topics", "entities"])
        self.batch_size = self.config.get("batch_size", 50)
    
    async def process_item(self, item: BatchItem) -> BatchItem:
        """Process content analysis for single item"""
        start_time = time.time()
        
        try:
            content = item.data.get("content", "")
            content_type = item.data.get("content_type", "text")
            
            # Perform various analyses
            analysis_results = {}
            
            if "sentiment" in self.analysis_types:
                analysis_results["sentiment"] = await self._analyze_sentiment(content)
            
            if "topics" in self.analysis_types:
                analysis_results["topics"] = await self._extract_topics(content)
            
            if "entities" in self.analysis_types:
                analysis_results["entities"] = await self._extract_entities(content)
            
            if "quality" in self.analysis_types:
                analysis_results["quality"] = await self._assess_quality(content, content_type)
            
            # Store results
            item.processing_result = analysis_results
            item.processing_time = time.time() - start_time
            
            return item
            
        except Exception as e:
            item.error_message = str(e)
            item.processing_time = time.time() - start_time
            return item
    
    async def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze sentiment of content"""
        # Simplified sentiment analysis
        positive_words = ["good", "great", "awesome", "love", "amazing", "excellent"]
        negative_words = ["bad", "hate", "terrible", "awful", "horrible"]
        
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
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {"positive": positive_score, "negative": negative_score}
        }
    
    async def _extract_topics(self, content: str) -> List[Dict[str, Any]]:
        """Extract topics from content"""
        # Simplified topic extraction
        topic_keywords = {
            "technology": ["ai", "ml", "tech", "digital", "software", "algorithm"],
            "entertainment": ["music", "video", "movie", "show", "performance"],
            "education": ["learn", "teach", "study", "course", "tutorial"],
            "lifestyle": ["life", "style", "fashion", "food", "travel"],
            "business": ["business", "entrepreneur", "startup", "investment"]
        }
        
        content_lower = content.lower()
        topics = []
        
        for topic, keywords in topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > 0:
                topics.append({
                    "topic": topic,
                    "relevance": min(1.0, score / len(keywords)),
                    "keyword_matches": score
                })
        
        return sorted(topics, key=lambda x: x["relevance"], reverse=True)
    
    async def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """Extract named entities from content"""
        # Simplified entity extraction
        entities = []
        words = content.split()
        
        # Look for capitalized words (potential entities)
        for word in words:
            if word.istitle() and len(word) > 2:
                entities.append({
                    "text": word,
                    "type": "PERSON" if word.endswith("'s") else "ORG",
                    "confidence": 0.7
                })
        
        return entities[:10]  # Limit to top 10 entities
    
    async def _assess_quality(self, content: str, content_type: str) -> Dict[str, Any]:
        """Assess content quality"""
        quality_score = 0.5  # Base score
        
        # Length-based scoring
        if content_type == "text":
            if 100 <= len(content) <= 2000:
                quality_score += 0.2
            elif len(content) < 50:
                quality_score -= 0.3
        
        # Grammar and style (simplified)
        if content.count(".") > 0:  # Has sentences
            quality_score += 0.1
        
        if content.count("?") + content.count("!") > 0:  # Engaging
            quality_score += 0.1
        
        return {
            "overall_score": min(1.0, max(0.0, quality_score)),
            "length": len(content),
            "readability": "medium",  # Simplified
            "engagement_indicators": content.count("?") + content.count("!")
        }
    
    def get_processor_name(self) -> str:
        return "ContentAnalysisProcessor"

class ImageProcessingProcessor(BatchProcessor):
    """Batch processor for image processing"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.operations = self.config.get("operations", ["resize", "enhance", "analyze"])
        self.output_formats = self.config.get("output_formats", ["jpg", "webp"])
    
    async def process_item(self, item: BatchItem) -> BatchItem:
        """Process image item"""
        start_time = time.time()
        
        try:
            image_path = item.data.get("image_path")
            image_url = item.data.get("image_url")
            
            if not image_path and not image_url:
                raise ValueError("No image path or URL provided")
            
            # Simulate image processing operations
            processing_results = {}
            
            if "resize" in self.operations:
                processing_results["resize"] = await self._resize_image(image_path or image_url)
            
            if "enhance" in self.operations:
                processing_results["enhance"] = await self._enhance_image(image_path or image_url)
            
            if "analyze" in self.operations:
                processing_results["analysis"] = await self._analyze_image(image_path or image_url)
            
            item.processing_result = processing_results
            item.processing_time = time.time() - start_time
            
            return item
            
        except Exception as e:
            item.error_message = str(e)
            item.processing_time = time.time() - start_time
            return item
    
    async def _resize_image(self, image_source: str) -> Dict[str, Any]:
        """Resize image to multiple dimensions"""
        # Simulate image resizing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "original_size": "1920x1080",
            "resized_variants": [
                {"size": "1080x1080", "format": "jpg", "file_size": "150kb"},
                {"size": "1080x1920", "format": "jpg", "file_size": "200kb"},
                {"size": "500x500", "format": "webp", "file_size": "80kb"}
            ]
        }
    
    async def _enhance_image(self, image_source: str) -> Dict[str, Any]:
        """Enhance image quality"""
        # Simulate image enhancement
        await asyncio.sleep(0.15)  # Simulate processing time
        
        return {
            "enhancements_applied": ["brightness_boost", "contrast_enhancement", "noise_reduction"],
            "quality_improvement": 0.25,
            "processing_time": 0.15
        }
    
    async def _analyze_image(self, image_source: str) -> Dict[str, Any]:
        """Analyze image content"""
        # Simulate image analysis
        await asyncio.sleep(0.2)  # Simulate processing time
        
        return {
            "detected_objects": [
                {"object": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
                {"object": "background", "confidence": 0.87, "bbox": [0, 0, 1920, 1080]}
            ],
            "colors": ["blue", "white", "black"],
            "style": "portrait",
            "quality_score": 0.85
        }
    
    def get_processor_name(self) -> str:
        return "ImageProcessingProcessor"

class ModelTrainingProcessor(BatchProcessor):
    """Batch processor for ML model training tasks"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.model_type = self.config.get("model_type", "classification")
        self.training_params = self.config.get("training_params", {})
    
    async def process_item(self, item: BatchItem) -> BatchItem:
        """Process model training item"""
        start_time = time.time()
        
        try:
            training_data = item.data.get("training_data", [])
            model_config = item.data.get("model_config", {})
            
            if not training_data:
                raise ValueError("No training data provided")
            
            # Simulate model training
            training_result = await self._train_model(training_data, model_config)
            
            item.processing_result = training_result
            item.processing_time = time.time() - start_time
            
            return item
            
        except Exception as e:
            item.error_message = str(e)
            item.processing_time = time.time() - start_time
            return item
    
    async def _train_model(self, training_data: List[Dict], model_config: Dict) -> Dict[str, Any]:
        """Train ML model"""
        # Simulate model training
        training_time = len(training_data) * 0.001  # Scale with data size
        await asyncio.sleep(min(training_time, 2.0))  # Cap at 2 seconds for demo
        
        # Simulate training metrics
        accuracy = np.random.uniform(0.8, 0.95)
        loss = np.random.uniform(0.05, 0.2)
        
        return {
            "model_type": self.model_type,
            "training_samples": len(training_data),
            "epochs": model_config.get("epochs", 10),
            "final_accuracy": accuracy,
            "final_loss": loss,
            "model_size": f"{np.random.randint(10, 100)}MB",
            "training_time": training_time
        }
    
    def get_processor_name(self) -> str:
        return "ModelTrainingProcessor"

class BatchProcessingAgent:
    """📦 Advanced Batch Processing AI Agent for Large-Scale Operations"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize Batch Processing Agent"""
        self.config = config or {}
        self.max_workers = self.config.get("max_workers", multiprocessing.cpu_count())
        self.job_queue = Queue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.processors = self._initialize_processors()
        self.checkpoints_dir = Path(self.config.get("checkpoints_dir", "./checkpoints"))
        self.checkpoints_dir.mkdir(exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_jobs": 0,
            "completed_jobs": 0,
            "failed_jobs": 0,
            "total_items_processed": 0,
            "average_job_time": 0.0,
            "throughput_items_per_second": 0.0
        }
        
        logger.info("📦 Batch Processing Agent initialized successfully")
    
    def _initialize_processors(self) -> Dict[str, BatchProcessor]:
        """Initialize available processors"""
        return {
            "content_analysis": ContentAnalysisProcessor(),
            "image_processing": ImageProcessingProcessor(),
            "model_training": ModelTrainingProcessor()
        }
    
    async def submit_job(self, job: BatchJob) -> str:
        """Submit a batch job for processing"""
        job.status = JobStatus.QUEUED
        self.job_queue.put(job)
        self.active_jobs[job.job_id] = job
        self.stats["total_jobs"] += 1
        
        logger.info(f"Job {job.job_id} submitted with {len(job.items)} items")
        return job.job_id
    
    async def process_job(self, job: BatchJob) -> BatchResult:
        """Process a batch job"""
        logger.info(f"Starting job {job.job_id}: {job.job_name}")
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()
        start_time = time.time()
        
        try:
            # Get processor
            processor_name = job.processor_config.get("processor", "content_analysis")
            processor = self.processors.get(processor_name)
            
            if not processor:
                raise ValueError(f"Unknown processor: {processor_name}")
            
            # Prepare batch
            items = processor.prepare_batch(job.items)
            
            # Load checkpoint if exists
            checkpoint_data = await self._load_checkpoint(job.job_id)
            if checkpoint_data:
                processed_items = checkpoint_data.get("processed_items", [])
                items = [item for item in items if item.item_id not in processed_items]
                logger.info(f"Resumed job {job.job_id} from checkpoint, {len(items)} items remaining")
            
            # Process items based on mode
            if job.processing_mode == ProcessingMode.SEQUENTIAL:
                processed_items = await self._process_sequential(processor, items, job)
            elif job.processing_mode == ProcessingMode.PARALLEL_THREADS:
                processed_items = await self._process_parallel_threads(processor, items, job)
            elif job.processing_mode == ProcessingMode.PARALLEL_PROCESSES:
                processed_items = await self._process_parallel_processes(processor, items, job)
            else:
                # Default to parallel threads
                processed_items = await self._process_parallel_threads(processor, items, job)
            
            # Calculate results
            processing_time = time.time() - start_time
            successful_items = sum(1 for item in processed_items if item.processing_result is not None)
            failed_items = len(processed_items) - successful_items
            
            # Update job status
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.success_count = successful_items
            job.error_count = failed_items
            job.progress = 100.0
            
            # Create result
            result = BatchResult(
                job_id=job.job_id,
                status=job.status,
                total_items=len(job.items),
                successful_items=successful_items,
                failed_items=failed_items,
                processing_time=processing_time,
                throughput=len(processed_items) / processing_time if processing_time > 0 else 0,
                error_summary=self._create_error_summary(processed_items)
            )
            
            # Update statistics
            self._update_stats(result)
            
            # Clean up checkpoint
            await self._cleanup_checkpoint(job.job_id)
            
            self.completed_jobs[job.job_id] = result
            logger.info(f"Job {job.job_id} completed: {successful_items}/{len(processed_items)} successful")
            
            return result
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            
            processing_time = time.time() - start_time
            result = BatchResult(
                job_id=job.job_id,
                status=JobStatus.FAILED,
                total_items=len(job.items),
                successful_items=0,
                failed_items=len(job.items),
                processing_time=processing_time,
                throughput=0,
                error_summary=[{"error": str(e), "count": len(job.items)}]
            )
            
            self.stats["failed_jobs"] += 1
            self.completed_jobs[job.job_id] = result
            
            logger.error(f"Job {job.job_id} failed: {str(e)}")
            raise
    
    async def _process_sequential(self, processor: BatchProcessor, items: List[BatchItem], job: BatchJob) -> List[BatchItem]:
        """Process items sequentially"""
        processed_items = []
        
        for i, item in enumerate(items):
            try:
                processed_item = await processor.process_item(item)
                processed_items.append(processed_item)
                
                # Update progress
                job.progress = (i + 1) / len(items) * 100
                
                # Checkpoint if needed
                if (i + 1) % job.checkpoint_interval == 0:
                    await self._save_checkpoint(job.job_id, processed_items)
                
            except Exception as e:
                item.error_message = str(e)
                processed_items.append(item)
        
        return processed_items
    
    async def _process_parallel_threads(self, processor: BatchProcessor, items: List[BatchItem], job: BatchJob) -> List[BatchItem]:
        """Process items using thread pool"""
        processed_items = []
        
        async def process_batch_chunk(chunk: List[BatchItem]) -> List[BatchItem]:
            chunk_results = []
            for item in chunk:
                try:
                    result = await processor.process_item(item)
                    chunk_results.append(result)
                except Exception as e:
                    item.error_message = str(e)
                    chunk_results.append(item)
            return chunk_results
        
        # Split into chunks for parallel processing
        chunk_size = max(1, len(items) // self.max_workers)
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
        
        # Process chunks concurrently
        tasks = [process_batch_chunk(chunk) for chunk in chunks]
        chunk_results = await asyncio.gather(*tasks)
        
        # Flatten results
        for chunk_result in chunk_results:
            processed_items.extend(chunk_result)
        
        job.progress = 100.0
        return processed_items
    
    async def _process_parallel_processes(self, processor: BatchProcessor, items: List[BatchItem], job: BatchJob) -> List[BatchItem]:
        """Process items using process pool"""
        # Note: This is a simplified version. In production, you'd need to handle
        # serialization and communication between processes properly.
        
        def process_item_sync(item_data):
            """Synchronous wrapper for process pool"""
            # This would need proper implementation for real process-based parallelism
            return item_data
        
        processed_items = []
        
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all items for processing
            future_to_item = {
                executor.submit(process_item_sync, item): item 
                for item in items
            }
            
            # Collect results
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    result = future.result()
                    processed_items.append(item)  # Simplified
                except Exception as e:
                    item.error_message = str(e)
                    processed_items.append(item)
        
        job.progress = 100.0
        return processed_items
    
    async def _save_checkpoint(self, job_id: str, processed_items: List[BatchItem]):
        """Save job checkpoint"""
        checkpoint_file = self.checkpoints_dir / f"{job_id}.checkpoint"
        
        checkpoint_data = {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "processed_items": [item.item_id for item in processed_items if item.processing_result is not None],
            "item_count": len(processed_items)
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f)
    
    async def _load_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Load job checkpoint"""
        checkpoint_file = self.checkpoints_dir / f"{job_id}.checkpoint"
        
        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                return json.load(f)
        
        return None
    
    async def _cleanup_checkpoint(self, job_id: str):
        """Clean up job checkpoint"""
        checkpoint_file = self.checkpoints_dir / f"{job_id}.checkpoint"
        
        if checkpoint_file.exists():
            checkpoint_file.unlink()
    
    def _create_error_summary(self, items: List[BatchItem]) -> List[Dict[str, Any]]:
        """Create error summary from processed items"""
        error_counts = {}
        
        for item in items:
            if item.error_message:
                error = item.error_message
                if error in error_counts:
                    error_counts[error] += 1
                else:
                    error_counts[error] = 1
        
        return [
            {"error": error, "count": count}
            for error, count in error_counts.items()
        ]
    
    def _update_stats(self, result: BatchResult):
        """Update processing statistics"""
        if result.status == JobStatus.COMPLETED:
            self.stats["completed_jobs"] += 1
        else:
            self.stats["failed_jobs"] += 1
        
        self.stats["total_items_processed"] += result.total_items
        
        # Update average job time
        total_completed = self.stats["completed_jobs"]
        if total_completed > 0:
            current_avg = self.stats["average_job_time"]
            new_avg = ((current_avg * (total_completed - 1)) + result.processing_time) / total_completed
            self.stats["average_job_time"] = new_avg
        
        # Update throughput
        if result.processing_time > 0:
            self.stats["throughput_items_per_second"] = result.throughput
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            return {
                "job_id": job.job_id,
                "status": job.status.value,
                "progress": job.progress,
                "total_items": len(job.items),
                "success_count": job.success_count,
                "error_count": job.error_count,
                "started_at": job.started_at.isoformat() if job.started_at else None,
                "estimated_completion": self._estimate_completion_time(job)
            }
        elif job_id in self.completed_jobs:
            result = self.completed_jobs[job_id]
            return {
                "job_id": result.job_id,
                "status": result.status.value,
                "total_items": result.total_items,
                "successful_items": result.successful_items,
                "failed_items": result.failed_items,
                "processing_time": result.processing_time,
                "throughput": result.throughput
            }
        
        return None
    
    def _estimate_completion_time(self, job: BatchJob) -> Optional[str]:
        """Estimate job completion time"""
        if job.progress > 0 and job.started_at:
            elapsed = (datetime.now() - job.started_at).total_seconds()
            estimated_total = elapsed / (job.progress / 100)
            remaining = estimated_total - elapsed
            
            completion_time = datetime.now() + timedelta(seconds=remaining)
            return completion_time.isoformat()
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            "active_jobs": len(self.active_jobs),
            "queue_size": self.job_queue.qsize(),
            "max_workers": self.max_workers
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        if job_id in self.active_jobs:
            job = self.active_jobs[job_id]
            if job.status in [JobStatus.QUEUED, JobStatus.RUNNING]:
                job.status = JobStatus.CANCELLED
                logger.info(f"Job {job_id} cancelled")
                return True
        
        return False

# Utility functions for creating batch jobs
def create_content_analysis_job(content_items: List[Dict[str, Any]], 
                               analysis_types: List[str] = None) -> BatchJob:
    """Create a content analysis batch job"""
    job_id = str(uuid.uuid4())
    
    items = []
    for i, content_item in enumerate(content_items):
        item = BatchItem(
            item_id=f"{job_id}_item_{i}",
            data=content_item
        )
        items.append(item)
    
    return BatchJob(
        job_id=job_id,
        job_name="Content Analysis Batch",
        items=items,
        processor_config={
            "processor": "content_analysis",
            "analysis_types": analysis_types or ["sentiment", "topics", "entities"]
        },
        processing_mode=ProcessingMode.PARALLEL_THREADS
    )

def create_image_processing_job(image_items: List[Dict[str, Any]], 
                               operations: List[str] = None) -> BatchJob:
    """Create an image processing batch job"""
    job_id = str(uuid.uuid4())
    
    items = []
    for i, image_item in enumerate(image_items):
        item = BatchItem(
            item_id=f"{job_id}_item_{i}",
            data=image_item
        )
        items.append(item)
    
    return BatchJob(
        job_id=job_id,
        job_name="Image Processing Batch",
        items=items,
        processor_config={
            "processor": "image_processing",
            "operations": operations or ["resize", "enhance", "analyze"]
        },
        processing_mode=ProcessingMode.PARALLEL_THREADS
    )

# Usage Example and Template Testing
async def main():
    """Example usage of Batch Processing Agent Template"""
    
    # Initialize the agent
    agent = BatchProcessingAgent(config={"max_workers": 4})
    
    # Create sample content for analysis
    content_items = [
        {
            "content": "This is an amazing AI-powered content creation tool that helps creators make awesome videos!",
            "content_type": "text",
            "source": "video_description"
        },
        {
            "content": "I hate this terrible product. It's the worst thing ever created.",
            "content_type": "text",
            "source": "review"
        },
        {
            "content": "The weather today is okay, nothing special but fine for a walk.",
            "content_type": "text",
            "source": "social_media"
        },
        {
            "content": "Learn how to create amazing AI agents with this comprehensive tutorial on machine learning and content processing.",
            "content_type": "text",
            "source": "tutorial"
        }
    ]
    
    # Create sample images for processing
    image_items = [
        {
            "image_path": "/path/to/image1.jpg",
            "image_type": "profile_picture"
        },
        {
            "image_url": "https://example.com/image2.jpg",
            "image_type": "content_thumbnail"
        }
    ]
    
    try:
        # Create and submit content analysis job
        content_job = create_content_analysis_job(
            content_items, 
            analysis_types=["sentiment", "topics", "entities", "quality"]
        )
        
        content_job_id = await agent.submit_job(content_job)
        print(f"✅ Content analysis job submitted: {content_job_id}")
        
        # Create and submit image processing job
        image_job = create_image_processing_job(
            image_items,
            operations=["resize", "enhance", "analyze"]
        )
        
        image_job_id = await agent.submit_job(image_job)
        print(f"✅ Image processing job submitted: {image_job_id}")
        
        # Process the jobs
        print("\n🔄 Processing jobs...")
        
        content_result = await agent.process_job(content_job)
        print(f"✅ Content analysis completed: {content_result.successful_items}/{content_result.total_items} successful")
        
        image_result = await agent.process_job(image_job)
        print(f"✅ Image processing completed: {image_result.successful_items}/{image_result.total_items} successful")
        
        # Display results
        print(f"\n📊 Content Analysis Results:")
        for item in content_job.items:
            if item.processing_result:
                print(f"  Item {item.item_id}:")
                print(f"    Sentiment: {item.processing_result.get('sentiment', {}).get('sentiment', 'N/A')}")
                print(f"    Topics: {len(item.processing_result.get('topics', []))} found")
                print(f"    Quality Score: {item.processing_result.get('quality', {}).get('overall_score', 'N/A')}")
        
        print(f"\n📊 Image Processing Results:")
        for item in image_job.items:
            if item.processing_result:
                print(f"  Item {item.item_id}:")
                if 'resize' in item.processing_result:
                    variants = item.processing_result['resize']['resized_variants']
                    print(f"    Resized to {len(variants)} variants")
                if 'analysis' in item.processing_result:
                    objects = item.processing_result['analysis']['detected_objects']
                    print(f"    Detected {len(objects)} objects")
        
        # Get overall statistics
        stats = agent.get_stats()
        print(f"\n📈 Processing Statistics:")
        print(f"  Total Jobs: {stats['total_jobs']}")
        print(f"  Completed Jobs: {stats['completed_jobs']}")
        print(f"  Total Items Processed: {stats['total_items_processed']}")
        print(f"  Average Job Time: {stats['average_job_time']:.2f}s")
        print(f"  Throughput: {stats['throughput_items_per_second']:.1f} items/second")
        
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
    print("📦 Batch Processing Agent Template demonstration completed!")