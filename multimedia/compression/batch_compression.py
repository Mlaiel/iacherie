"""Batch Compression Processor
High-performance batch processing for multimedia compression.

Created by: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import time

logger = logging.getLogger(__name__)

@dataclass
class BatchJob:
    """Batch compression job definition."""
    input_files: List[Path]
    output_directory: Path
    profile: str
    priority: int = 5  # 1-10, 10 being highest
    metadata: Dict[str, Any] = None

@dataclass
class BatchProgress:
    """Batch processing progress information."""
    total_files: int
    completed_files: int
    failed_files: int
    current_file: Optional[str]
    estimated_remaining_time: float
    average_processing_time: float

class BatchCompressionProcessor:
    """Enterprise batch compression processor with queue management."""
    
    def __init__(self, max_workers: int = 4, max_memory_gb: float = 8.0):
        """Initialize the batch processor."""
        self.max_workers = max_workers
        self.max_memory_gb = max_memory_gb
        self.job_queue = asyncio.Queue()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.processing_stats = {
            "total_processed": 0,
            "total_failures": 0,
            "total_savings": 0,
            "processing_time": 0.0
        }
        
    async def submit_batch_job(
        self,
        input_files: List[Union[str, Path]],
        output_directory: Union[str, Path],
        profile: str,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Submit a batch compression job to the queue.
        
        Args:
            input_files: List of input file paths
            output_directory: Output directory path
            profile: Compression profile name
            priority: Job priority (1-10, 10 highest)
            metadata: Additional job metadata
            
        Returns:
            Job ID for tracking
        """
        job_id = f"batch_{int(time.time())}_{len(self.active_jobs)}"
        
        job = BatchJob(
            input_files=[Path(f) for f in input_files],
            output_directory=Path(output_directory),
            profile=profile,
            priority=priority,
            metadata=metadata or {}
        )
        
        await self.job_queue.put((priority, job_id, job))
        logger.info(f"Submitted batch job {job_id} with {len(input_files)} files")
        
        return job_id
    
    async def process_batch_queue(
        self,
        progress_callback: Optional[Callable[[str, BatchProgress], None]] = None
    ):
        """Process jobs from the batch queue."""
        while True:
            try:
                # Get highest priority job
                priority, job_id, job = await self.job_queue.get()
                
                logger.info(f"Starting batch job {job_id}")
                self.active_jobs[job_id] = {
                    "job": job,
                    "start_time": time.time(),
                    "progress": BatchProgress(
                        total_files=len(job.input_files),
                        completed_files=0,
                        failed_files=0,
                        current_file=None,
                        estimated_remaining_time=0.0,
                        average_processing_time=0.0
                    )
                }
                
                # Process the job
                result = await self._process_batch_job(
                    job_id, job, progress_callback
                )
                
                # Move to completed jobs
                self.completed_jobs[job_id] = {
                    **self.active_jobs[job_id],
                    "result": result,
                    "end_time": time.time()
                }
                
                del self.active_jobs[job_id]
                self.job_queue.task_done()
                
                logger.info(f"Completed batch job {job_id}")
                
            except Exception as e:
                logger.error(f"Batch processing error: {e}")
                await asyncio.sleep(1)
    
    async def _process_batch_job(
        self,
        job_id: str,
        job: BatchJob,
        progress_callback: Optional[Callable[[str, BatchProgress], None]] = None
    ) -> Dict[str, Any]:
        """Process a single batch job."""
        job.output_directory.mkdir(parents=True, exist_ok=True)
        
        results = []
        processing_times = []
        total_original_size = 0
        total_compressed_size = 0
        
        # Create semaphore for concurrent processing
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def process_single_file(file_path: Path) -> Dict[str, Any]:
            async with semaphore:
                start_time = time.time()
                
                # Update progress
                progress = self.active_jobs[job_id]["progress"]
                progress.current_file = file_path.name
                
                if progress_callback:
                    progress_callback(job_id, progress)
                
                try:
                    # Simulate compression (replace with actual compression logic)
                    await asyncio.sleep(0.1)  # Simulate processing time
                    
                    original_size = file_path.stat().st_size
                    compressed_size = int(original_size * 0.7)  # Simulated compression
                    
                    processing_time = time.time() - start_time
                    processing_times.append(processing_time)
                    
                    # Update progress
                    progress.completed_files += 1
                    progress.average_processing_time = sum(processing_times) / len(processing_times)
                    remaining_files = progress.total_files - progress.completed_files
                    progress.estimated_remaining_time = remaining_files * progress.average_processing_time
                    
                    return {
                        "file": str(file_path),
                        "success": True,
                        "original_size": original_size,
                        "compressed_size": compressed_size,
                        "compression_ratio": original_size / compressed_size,
                        "processing_time": processing_time
                    }
                    
                except Exception as e:
                    progress.failed_files += 1
                    logger.error(f"Failed to process {file_path}: {e}")
                    
                    return {
                        "file": str(file_path),
                        "success": False,
                        "error": str(e)
                    }
        
        # Process all files concurrently
        tasks = [process_single_file(file_path) for file_path in job.input_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate summary statistics
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        total_original_size = sum(r["original_size"] for r in successful_results)
        total_compressed_size = sum(r["compressed_size"] for r in successful_results)
        
        # Update global stats
        self.processing_stats["total_processed"] += len(successful_results)
        self.processing_stats["total_failures"] += len(results) - len(successful_results)
        self.processing_stats["total_savings"] += total_original_size - total_compressed_size
        self.processing_stats["processing_time"] += sum(processing_times)
        
        return {
            "job_id": job_id,
            "profile": job.profile,
            "total_files": len(job.input_files),
            "successful_files": len(successful_results),
            "failed_files": len(results) - len(successful_results),
            "total_original_size": total_original_size,
            "total_compressed_size": total_compressed_size,
            "total_space_saved": total_original_size - total_compressed_size,
            "average_compression_ratio": total_original_size / total_compressed_size if total_compressed_size > 0 else 0,
            "total_processing_time": sum(processing_times),
            "average_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
            "results": results
        }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        if job_id in self.active_jobs:
            job_info = self.active_jobs[job_id]
            return {
                "status": "processing",
                "progress": job_info["progress"],
                "start_time": job_info["start_time"],
                "elapsed_time": time.time() - job_info["start_time"]
            }
        elif job_id in self.completed_jobs:
            job_info = self.completed_jobs[job_id]
            return {
                "status": "completed",
                "result": job_info["result"],
                "start_time": job_info["start_time"],
                "end_time": job_info["end_time"],
                "total_time": job_info["end_time"] - job_info["start_time"]
            }
        else:
            return None
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status."""
        return {
            "queue_size": self.job_queue.qsize(),
            "active_jobs": len(self.active_jobs),
            "completed_jobs": len(self.completed_jobs),
            "max_workers": self.max_workers,
            "processing_stats": self.processing_stats.copy()
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job (if still in queue or processing)."""
        if job_id in self.active_jobs:
            # In a real implementation, this would cancel the active processing
            logger.warning(f"Cannot cancel active job {job_id} - not implemented")
            return False
        
        # For queued jobs, we'd need to implement queue manipulation
        logger.warning("Cancel queued job not implemented")
        return False
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        total_time = self.processing_stats["processing_time"]
        total_files = self.processing_stats["total_processed"]
        
        return {
            "throughput": {
                "files_per_hour": (total_files / (total_time / 3600)) if total_time > 0 else 0,
                "average_file_time": total_time / total_files if total_files > 0 else 0
            },
            "compression": {
                "total_space_saved_gb": self.processing_stats["total_savings"] / (1024**3),
                "success_rate": (
                    self.processing_stats["total_processed"] / 
                    (self.processing_stats["total_processed"] + self.processing_stats["total_failures"])
                ) if (self.processing_stats["total_processed"] + self.processing_stats["total_failures"]) > 0 else 0
            },
            "system": {
                "max_workers": self.max_workers,
                "max_memory_gb": self.max_memory_gb,
                "active_jobs": len(self.active_jobs),
                "queue_size": self.job_queue.qsize()
            }
        }