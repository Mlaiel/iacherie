"""
Source Separation Monitoring Module - Ainflue Platform
======================================================

Monitor DEMUCS and Spleeter source separation performance, quality metrics,
and processing efficiency for professional audio source separation workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class SeparationModel(Enum):
    """Supported source separation models."""
    DEMUCS_HTDEMUCS = "htdemucs"
    DEMUCS_HTDEMUCS_FT = "htdemucs_ft"
    DEMUCS_MDXNET = "mdx_extra"
    SPLEETER_2_STEMS = "spleeter:2stems-16kHz"
    SPLEETER_4_STEMS = "spleeter:4stems-16kHz"
    SPLEETER_5_STEMS = "spleeter:5stems-16kHz"

class SeparationQuality(Enum):
    """Quality levels for source separation."""
    BROADCAST = "broadcast"  # > 0.95 quality score
    PROFESSIONAL = "professional"  # > 0.90 quality score
    STANDARD = "standard"  # > 0.80 quality score
    PREVIEW = "preview"  # > 0.70 quality score

@dataclass
class SeparationJob:
    """Represents a source separation job."""
    job_id: str
    input_file: str
    model: SeparationModel
    stems: List[str]  # ['vocals', 'drums', 'bass', 'other']
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    quality_score: Optional[float] = None
    processing_time_ms: Optional[int] = None
    output_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SeparationMetrics:
    """Metrics for source separation monitoring."""
    total_jobs: int = 0
    successful_jobs: int = 0
    failed_jobs: int = 0
    average_quality: float = 0.0
    average_processing_time_ms: float = 0.0
    throughput_jobs_per_hour: float = 0.0
    model_performance: Dict[str, Dict[str, float]] = field(default_factory=dict)
    quality_distribution: Dict[str, int] = field(default_factory=dict)

class SourceSeparationMonitor:
    """
    Monitor source separation performance for DEMUCS and Spleeter models.
    
    Tracks processing time, quality metrics, model performance comparisons,
    and provides insights for optimization and capacity planning.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize source separation monitor."""
        self.config = config or self._default_config()
        self.jobs: Dict[str, SeparationJob] = {}
        self.metrics = SeparationMetrics()
        self.start_time = datetime.now()
        
        # Performance tracking
        self.model_benchmarks: Dict[str, List[float]] = {}
        self.quality_history: List[Tuple[datetime, float]] = []
        self.processing_queue = asyncio.Queue()
        
        logger.info("Source Separation Monitor initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for source separation monitoring."""
        return {
            "enabled_models": [
                SeparationModel.DEMUCS_HTDEMUCS_FT,
                SeparationModel.SPLEETER_5_STEMS
            ],
            "quality_threshold": 0.90,
            "processing_timeout_minutes": 30,
            "benchmark_interval_hours": 24,
            "metrics_retention_days": 30,
            "parallel_jobs": 4,
            "gpu_acceleration": True,
            "output_format": "wav",
            "sample_rate": 44100
        }
    
    async def start_separation_job(
        self, 
        job_id: str,
        input_file: str,
        model: SeparationModel,
        stems: List[str]
    ) -> str:
        """Start a new source separation job."""
        job = SeparationJob(
            job_id=job_id,
            input_file=input_file,
            model=model,
            stems=stems,
            start_time=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        # Add to processing queue
        await self.processing_queue.put(job)
        
        logger.info(f"Started separation job {job_id} with model {model.value}")
        return job_id
    
    async def process_separation_jobs(self) -> None:
        """Process separation jobs from queue."""
        while True:
            try:
                job = await self.processing_queue.get()
                await self._process_job(job)
                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing separation job: {e}")
                await asyncio.sleep(1)
    
    async def _process_job(self, job -> None: SeparationJob) -> None:
        """Process individual separation job."""
        try:
            job.status = "processing"
            
            # Simulate processing time based on model
            processing_time = self._estimate_processing_time(job.model, job.input_file)
            await asyncio.sleep(processing_time / 1000)  # Convert to seconds for simulation
            
            # Simulate quality score calculation
            quality_score = self._calculate_quality_score(job.model, job.stems)
            
            # Update job completion
            job.end_time = datetime.now()
            job.processing_time_ms = processing_time
            job.quality_score = quality_score
            job.status = "completed" if quality_score >= self.config["quality_threshold"] else "quality_failed"
            job.output_files = self._generate_output_files(job)
            
            # Update metrics
            self._update_metrics(job)
            
            logger.info(f"Completed job {job.job_id}: quality={quality_score:.3f}, time={processing_time}ms")
            
        except Exception as e:
            job.status = "failed"
            job.end_time = datetime.now()
            logger.error(f"Failed to process job {job.job_id}: {e}")
    
    def _estimate_processing_time(self, model: SeparationModel, input_file: str) -> int:
        """Estimate processing time based on model and file size."""
        # Base processing times (milliseconds)
        base_times = {
            SeparationModel.DEMUCS_HTDEMUCS_FT: 5000,
            SeparationModel.DEMUCS_HTDEMUCS: 4500,
            SeparationModel.DEMUCS_MDXNET: 6000,
            SeparationModel.SPLEETER_5_STEMS: 3000,
            SeparationModel.SPLEETER_4_STEMS: 2500,
            SeparationModel.SPLEETER_2_STEMS: 2000
        }
        
        base_time = base_times.get(model, 4000)
        
        # Add random variation (10-20%)
        import random
        variation = random.uniform(0.9, 1.2)
        
        return int(base_time * variation)
    
    def _calculate_quality_score(self, model: SeparationModel, stems: List[str]) -> float:
        """Calculate quality score for separation."""
        # Model quality baselines
        model_quality = {
            SeparationModel.DEMUCS_HTDEMUCS_FT: 0.96,
            SeparationModel.DEMUCS_HTDEMUCS: 0.94,
            SeparationModel.DEMUCS_MDXNET: 0.95,
            SeparationModel.SPLEETER_5_STEMS: 0.92,
            SeparationModel.SPLEETER_4_STEMS: 0.90,
            SeparationModel.SPLEETER_2_STEMS: 0.88
        }
        
        base_quality = model_quality.get(model, 0.85)
        
        # Adjust for number of stems (more stems = slightly lower quality)
        stem_penalty = (len(stems) - 2) * 0.01
        
        # Add random variation
        import random
        variation = random.uniform(-0.03, 0.02)
        
        return max(0.0, min(1.0, base_quality - stem_penalty + variation))
    
    def _generate_output_files(self, job: SeparationJob) -> List[str]:
        """Generate output file paths for separated stems."""
        base_name = Path(job.input_file).stem
        output_dir = f"output/{job.job_id}"
        
        output_files = []
        for stem in job.stems:
            output_file = f"{output_dir}/{base_name}_{stem}.{self.config['output_format']}"
            output_files.append(output_file)
        
        return output_files
    
    def _update_metrics(self, job -> None: SeparationJob) -> None:
        """Update separation metrics based on completed job."""
        self.metrics.total_jobs += 1
        
        if job.status == "completed":
            self.metrics.successful_jobs += 1
        else:
            self.metrics.failed_jobs += 1
        
        if job.quality_score is not None:
            # Update average quality
            total_quality = (self.metrics.average_quality * (self.metrics.total_jobs - 1) + 
                           job.quality_score)
            self.metrics.average_quality = total_quality / self.metrics.total_jobs
            
            # Update quality distribution
            quality_level = self._get_quality_level(job.quality_score)
            self.metrics.quality_distribution[quality_level] = (
                self.metrics.quality_distribution.get(quality_level, 0) + 1
            )
            
            # Track quality history
            self.quality_history.append((job.end_time, job.quality_score))
        
        if job.processing_time_ms is not None:
            # Update average processing time
            total_time = (self.metrics.average_processing_time_ms * (self.metrics.total_jobs - 1) + 
                         job.processing_time_ms)
            self.metrics.average_processing_time_ms = total_time / self.metrics.total_jobs
        
        # Update model performance
        model_name = job.model.value
        if model_name not in self.metrics.model_performance:
            self.metrics.model_performance[model_name] = {
                "jobs": 0, "avg_quality": 0.0, "avg_time_ms": 0.0
            }
        
        model_metrics = self.metrics.model_performance[model_name]
        model_metrics["jobs"] += 1
        
        if job.quality_score is not None and job.processing_time_ms is not None:
            total_quality = (model_metrics["avg_quality"] * (model_metrics["jobs"] - 1) + 
                           job.quality_score)
            model_metrics["avg_quality"] = total_quality / model_metrics["jobs"]
            
            total_time = (model_metrics["avg_time_ms"] * (model_metrics["jobs"] - 1) + 
                         job.processing_time_ms)
            model_metrics["avg_time_ms"] = total_time / model_metrics["jobs"]
        
        # Update throughput
        hours_running = (datetime.now() - self.start_time).total_seconds() / 3600
        if hours_running > 0:
            self.metrics.throughput_jobs_per_hour = self.metrics.total_jobs / hours_running
    
    def _get_quality_level(self, quality_score: float) -> str:
        """Determine quality level based on score."""
        if quality_score >= 0.95:
            return SeparationQuality.BROADCAST.value
        elif quality_score >= 0.90:
            return SeparationQuality.PROFESSIONAL.value
        elif quality_score >= 0.80:
            return SeparationQuality.STANDARD.value
        else:
            return SeparationQuality.PREVIEW.value
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific separation job."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            "job_id": job.job_id,
            "status": job.status,
            "model": job.model.value,
            "stems": job.stems,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "processing_time_ms": job.processing_time_ms,
            "quality_score": job.quality_score,
            "output_files": job.output_files
        }
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            "overview": {
                "total_jobs": self.metrics.total_jobs,
                "successful_jobs": self.metrics.successful_jobs,
                "failed_jobs": self.metrics.failed_jobs,
                "success_rate": (self.metrics.successful_jobs / max(1, self.metrics.total_jobs)),
                "average_quality": round(self.metrics.average_quality, 3),
                "average_processing_time_ms": round(self.metrics.average_processing_time_ms, 1),
                "throughput_jobs_per_hour": round(self.metrics.throughput_jobs_per_hour, 1)
            },
            "model_performance": self.metrics.model_performance,
            "quality_distribution": self.metrics.quality_distribution,
            "active_jobs": len([j for j in self.jobs.values() if j.status == "processing"]),
            "pending_jobs": self.processing_queue.qsize(),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_model_comparison(self) -> Dict[str, Any]:
        """Get detailed model performance comparison."""
        comparison = {}
        
        for model_name, metrics in self.metrics.model_performance.items():
            if metrics["jobs"] > 0:
                comparison[model_name] = {
                    "jobs_processed": metrics["jobs"],
                    "average_quality": round(metrics["avg_quality"], 3),
                    "average_time_ms": round(metrics["avg_time_ms"], 1),
                    "efficiency_score": round(metrics["avg_quality"] / (metrics["avg_time_ms"] / 1000), 3),
                    "recommendation": self._get_model_recommendation(metrics)
                }
        
        return comparison
    
    def _get_model_recommendation(self, metrics: Dict[str, float]) -> str:
        """Get recommendation for model based on performance."""
        quality = metrics["avg_quality"]
        time_ms = metrics["avg_time_ms"]
        
        if quality >= 0.95 and time_ms <= 4000:
            return "excellent"
        elif quality >= 0.90 and time_ms <= 6000:
            return "good"
        elif quality >= 0.85:
            return "acceptable"
        else:
            return "needs_optimization"

# Create default instance
source_separation_monitor = SourceSeparationMonitor()

__all__ = [
    'SourceSeparationMonitor',
    'SeparationJob',
    'SeparationModel', 
    'SeparationQuality',
    'source_separation_monitor'
]