"""
Loudness Normalization Monitor Module - Ainflue Platform
=======================================================

Monitor EBU R128 and ITU-R BS.1770 loudness normalization compliance,
dynamic range preservation, and broadcast standards adherence for
professional audio processing workflows.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)

class LoudnessStandard(Enum):
    """Supported loudness standards."""
    EBU_R128 = "ebu_r128"  # European Broadcasting Union
    ITU_R_BS1770 = "itu_r_bs1770"  # International Telecommunication Union
    ATSC_A85 = "atsc_a85"  # Advanced Television Systems Committee
    SMPTE_ST2067 = "smpte_st2067"  # Society of Motion Picture and Television Engineers

class BroadcastTarget(Enum):
    """Broadcast target specifications."""
    TV_BROADCAST = "tv_broadcast"  # -23 LUFS
    STREAMING_LOUD = "streaming_loud"  # -16 LUFS  
    STREAMING_STANDARD = "streaming_standard"  # -18 LUFS
    RADIO_BROADCAST = "radio_broadcast"  # -20 LUFS
    CINEMA = "cinema"  # -24 LUFS
    PODCAST = "podcast"  # -19 LUFS

@dataclass
class LoudnessTargets:
    """Loudness targets for different broadcast standards."""
    target_lufs: float  # Integrated loudness target
    max_true_peak_dbtp: float  # Maximum true peak in dBTP
    loudness_range_max_lu: float  # Maximum loudness range in LU
    short_term_max_lufs: float  # Maximum short-term loudness
    momentary_max_lufs: float  # Maximum momentary loudness

@dataclass 
class LoudnessMeasurement:
    """Loudness measurement results."""
    integrated_lufs: float
    loudness_range_lu: float
    true_peak_dbtp: float
    short_term_max_lufs: float
    momentary_max_lufs: float
    sample_peak_dbfs: float
    dynamic_range_db: float
    measurement_time: datetime

@dataclass
class NormalizationJob:
    """Represents a loudness normalization job."""
    job_id: str
    input_file: str
    output_file: str
    standard: LoudnessStandard
    target: BroadcastTarget
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"
    pre_normalization: Optional[LoudnessMeasurement] = None
    post_normalization: Optional[LoudnessMeasurement] = None
    gain_adjustment_db: Optional[float] = None
    compliance_score: Optional[float] = None
    processing_time_ms: Optional[int] = None

@dataclass
class LoudnessMetrics:
    """Metrics for loudness normalization monitoring."""
    total_jobs: int = 0
    compliant_jobs: int = 0
    non_compliant_jobs: int = 0
    average_compliance_score: float = 0.0
    average_gain_adjustment_db: float = 0.0
    average_processing_time_ms: float = 0.0
    standard_compliance: Dict[str, float] = field(default_factory=dict)
    target_distribution: Dict[str, int] = field(default_factory=dict)
    
class LoudnessNormalizationMonitor:
    """
    Monitor loudness normalization for broadcast standards compliance.
    
    Tracks EBU R128, ITU-R BS.1770 compliance, dynamic range preservation,
    and provides detailed analysis for broadcast and streaming platforms.
    """
    
    def __init__(self, config -> None: Optional[Dict[str, Any]] = None) -> None:
        """Initialize loudness normalization monitor."""
        self.config = config or self._default_config()
        self.jobs: Dict[str, NormalizationJob] = {}
        self.metrics = LoudnessMetrics()
        self.start_time = datetime.now()
        
        # Loudness targets configuration
        self.loudness_targets = self._initialize_targets()
        
        # Compliance tracking
        self.compliance_history: List[Tuple[datetime, float]] = []
        self.gain_distribution: List[float] = []
        
        logger.info("Loudness Normalization Monitor initialized")
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for loudness normalization monitoring."""
        return {
            "enabled_standards": [
                LoudnessStandard.EBU_R128,
                LoudnessStandard.ITU_R_BS1770
            ],
            "default_target": BroadcastTarget.STREAMING_STANDARD,
            "compliance_threshold": 0.95,
            "gate_threshold_lufs": -70.0,  # EBU R128 gating threshold
            "true_peak_limit_dbtp": -1.0,
            "loudness_range_target_lu": 7.0,
            "dynamic_range_preservation": True,
            "limiter_enabled": True,
            "sample_rate": 48000,
            "bit_depth": 24
        }
    
    def _initialize_targets(self) -> Dict[BroadcastTarget, LoudnessTargets]:
        """Initialize loudness targets for different broadcast standards."""
        return {
            BroadcastTarget.TV_BROADCAST: LoudnessTargets(
                target_lufs=-23.0,
                max_true_peak_dbtp=-1.0,
                loudness_range_max_lu=15.0,
                short_term_max_lufs=-18.0,
                momentary_max_lufs=-15.0
            ),
            BroadcastTarget.STREAMING_LOUD: LoudnessTargets(
                target_lufs=-16.0,
                max_true_peak_dbtp=-1.0,
                loudness_range_max_lu=12.0,
                short_term_max_lufs=-11.0,
                momentary_max_lufs=-8.0
            ),
            BroadcastTarget.STREAMING_STANDARD: LoudnessTargets(
                target_lufs=-18.0,
                max_true_peak_dbtp=-1.0,
                loudness_range_max_lu=10.0,
                short_term_max_lufs=-13.0,
                momentary_max_lufs=-10.0
            ),
            BroadcastTarget.RADIO_BROADCAST: LoudnessTargets(
                target_lufs=-20.0,
                max_true_peak_dbtp=-0.5,
                loudness_range_max_lu=8.0,
                short_term_max_lufs=-15.0,
                momentary_max_lufs=-12.0
            ),
            BroadcastTarget.CINEMA: LoudnessTargets(
                target_lufs=-24.0,
                max_true_peak_dbtp=-3.0,
                loudness_range_max_lu=20.0,
                short_term_max_lufs=-19.0,
                momentary_max_lufs=-16.0
            ),
            BroadcastTarget.PODCAST: LoudnessTargets(
                target_lufs=-19.0,
                max_true_peak_dbtp=-1.0,
                loudness_range_max_lu=6.0,
                short_term_max_lufs=-14.0,
                momentary_max_lufs=-11.0
            )
        }
    
    def start_normalization_job(
        self,
        job_id: str,
        input_file: str,
        output_file: str,
        standard: LoudnessStandard,
        target: BroadcastTarget
    ) -> str:
        """Start a new loudness normalization job."""
        job = NormalizationJob(
            job_id=job_id,
            input_file=input_file,
            output_file=output_file,
            standard=standard,
            target=target,
            start_time=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        # Start processing
        self._process_normalization_job(job)
        
        logger.info(f"Started normalization job {job_id} for {standard.value} -> {target.value}")
        return job_id
    
    def _process_normalization_job(self, job -> None: NormalizationJob) -> None:
        """Process loudness normalization job."""
        try:
            job.status = "analyzing"
            
            # Simulate pre-normalization measurement
            job.pre_normalization = self._simulate_loudness_measurement(job.input_file, "pre")
            
            job.status = "normalizing"
            
            # Calculate gain adjustment needed
            target_spec = self.loudness_targets[job.target]
            current_lufs = job.pre_normalization.integrated_lufs
            target_lufs = target_spec.target_lufs
            job.gain_adjustment_db = target_lufs - current_lufs
            
            # Simulate processing time
            import random
            processing_time = random.randint(1000, 5000)  # 1-5 seconds
            job.processing_time_ms = processing_time
            
            # Simulate post-normalization measurement
            job.post_normalization = self._simulate_post_normalization_measurement(
                job.pre_normalization, job.gain_adjustment_db, target_spec
            )
            
            # Calculate compliance score
            job.compliance_score = self._calculate_compliance_score(
                job.post_normalization, target_spec
            )
            
            job.status = "completed" if job.compliance_score >= self.config["compliance_threshold"] else "non_compliant"
            job.end_time = datetime.now()
            
            # Update metrics
            self._update_metrics(job)
            
            logger.info(f"Completed normalization job {job.job_id}: "
                       f"compliance={job.compliance_score:.3f}, gain={job.gain_adjustment_db:.1f}dB")
            
        except Exception as e:
            job.status = "failed"
            job.end_time = datetime.now()
            logger.error(f"Failed to process normalization job {job.job_id}: {e}")
    
    def _simulate_loudness_measurement(self, file_path: str, phase: str) -> LoudnessMeasurement:
        """Simulate loudness measurement."""
        import random
        
        # Simulate realistic loudness measurements
        if phase == "pre":
            integrated_lufs = random.uniform(-35.0, -8.0)
            loudness_range = random.uniform(3.0, 25.0)
            true_peak = random.uniform(-12.0, 0.0)
            short_term_max = integrated_lufs + random.uniform(3.0, 8.0)
            momentary_max = short_term_max + random.uniform(2.0, 5.0)
            sample_peak = true_peak - random.uniform(0.1, 2.0)
            dynamic_range = random.uniform(8.0, 30.0)
        else:
            # Post-normalization values should be closer to target
            integrated_lufs = random.uniform(-25.0, -15.0)
            loudness_range = random.uniform(4.0, 12.0)
            true_peak = random.uniform(-3.0, -0.5)
            short_term_max = integrated_lufs + random.uniform(2.0, 6.0)
            momentary_max = short_term_max + random.uniform(1.0, 4.0)
            sample_peak = true_peak - random.uniform(0.1, 1.0)
            dynamic_range = random.uniform(6.0, 20.0)
        
        return LoudnessMeasurement(
            integrated_lufs=integrated_lufs,
            loudness_range_lu=loudness_range,
            true_peak_dbtp=true_peak,
            short_term_max_lufs=short_term_max,
            momentary_max_lufs=momentary_max,
            sample_peak_dbfs=sample_peak,
            dynamic_range_db=dynamic_range,
            measurement_time=datetime.now()
        )
    
    def _simulate_post_normalization_measurement(
        self,
        pre_measurement: LoudnessMeasurement,
        gain_db: float,
        target: LoudnessTargets
    ) -> LoudnessMeasurement:
        """Simulate post-normalization measurement based on gain adjustment."""
        import random
        
        # Apply gain adjustment with some variance
        variance = random.uniform(-0.2, 0.2)
        
        return LoudnessMeasurement(
            integrated_lufs=pre_measurement.integrated_lufs + gain_db + variance,
            loudness_range_lu=pre_measurement.loudness_range_lu * random.uniform(0.9, 1.1),
            true_peak_dbtp=min(target.max_true_peak_dbtp, 
                              pre_measurement.true_peak_dbtp + gain_db + variance),
            short_term_max_lufs=pre_measurement.short_term_max_lufs + gain_db + variance,
            momentary_max_lufs=pre_measurement.momentary_max_lufs + gain_db + variance,
            sample_peak_dbfs=pre_measurement.sample_peak_dbfs + gain_db + variance,
            dynamic_range_db=pre_measurement.dynamic_range_db * random.uniform(0.95, 1.05),
            measurement_time=datetime.now()
        )
    
    def _calculate_compliance_score(
        self,
        measurement: LoudnessMeasurement,
        target: LoudnessTargets
    ) -> float:
        """Calculate compliance score based on target specifications."""
        scores = []
        
        # Integrated loudness compliance
        lufs_error = abs(measurement.integrated_lufs - target.target_lufs)
        lufs_score = max(0.0, 1.0 - (lufs_error / 2.0))  # ±2 LUFS tolerance
        scores.append(lufs_score)
        
        # True peak compliance
        if measurement.true_peak_dbtp <= target.max_true_peak_dbtp:
            peak_score = 1.0
        else:
            peak_excess = measurement.true_peak_dbtp - target.max_true_peak_dbtp
            peak_score = max(0.0, 1.0 - (peak_excess / 3.0))
        scores.append(peak_score)
        
        # Loudness range compliance
        if measurement.loudness_range_lu <= target.loudness_range_max_lu:
            range_score = 1.0
        else:
            range_excess = measurement.loudness_range_lu - target.loudness_range_max_lu
            range_score = max(0.0, 1.0 - (range_excess / 10.0))
        scores.append(range_score)
        
        # Short-term loudness compliance
        if measurement.short_term_max_lufs <= target.short_term_max_lufs:
            short_term_score = 1.0
        else:
            short_term_excess = measurement.short_term_max_lufs - target.short_term_max_lufs
            short_term_score = max(0.0, 1.0 - (short_term_excess / 5.0))
        scores.append(short_term_score)
        
        # Momentary loudness compliance
        if measurement.momentary_max_lufs <= target.momentary_max_lufs:
            momentary_score = 1.0
        else:
            momentary_excess = measurement.momentary_max_lufs - target.momentary_max_lufs
            momentary_score = max(0.0, 1.0 - (momentary_excess / 5.0))
        scores.append(momentary_score)
        
        # Weighted average (integrated loudness is most important)
        weights = [0.4, 0.2, 0.2, 0.1, 0.1]
        weighted_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return min(1.0, max(0.0, weighted_score))
    
    def _update_metrics(self, job -> None: NormalizationJob) -> None:
        """Update loudness normalization metrics."""
        self.metrics.total_jobs += 1
        
        if job.status == "completed":
            self.metrics.compliant_jobs += 1
        elif job.status == "non_compliant":
            self.metrics.non_compliant_jobs += 1
        
        if job.compliance_score is not None:
            # Update average compliance score
            total_compliance = (self.metrics.average_compliance_score * (self.metrics.total_jobs - 1) + 
                              job.compliance_score)
            self.metrics.average_compliance_score = total_compliance / self.metrics.total_jobs
            
            # Track compliance history
            self.compliance_history.append((job.end_time, job.compliance_score))
        
        if job.gain_adjustment_db is not None:
            # Update average gain adjustment
            total_gain = (self.metrics.average_gain_adjustment_db * (self.metrics.total_jobs - 1) + 
                         job.gain_adjustment_db)
            self.metrics.average_gain_adjustment_db = total_gain / self.metrics.total_jobs
            
            # Track gain distribution
            self.gain_distribution.append(job.gain_adjustment_db)
        
        if job.processing_time_ms is not None:
            # Update average processing time
            total_time = (self.metrics.average_processing_time_ms * (self.metrics.total_jobs - 1) + 
                         job.processing_time_ms)
            self.metrics.average_processing_time_ms = total_time / self.metrics.total_jobs
        
        # Update standard compliance rates
        standard_name = job.standard.value
        if standard_name not in self.metrics.standard_compliance:
            self.metrics.standard_compliance[standard_name] = 0.0
        
        # Update target distribution
        target_name = job.target.value
        self.metrics.target_distribution[target_name] = (
            self.metrics.target_distribution.get(target_name, 0) + 1
        )
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific normalization job."""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        result = {
            "job_id": job.job_id,
            "status": job.status,
            "standard": job.standard.value,
            "target": job.target.value,
            "start_time": job.start_time.isoformat(),
            "end_time": job.end_time.isoformat() if job.end_time else None,
            "processing_time_ms": job.processing_time_ms,
            "gain_adjustment_db": job.gain_adjustment_db,
            "compliance_score": job.compliance_score
        }
        
        if job.pre_normalization:
            result["pre_normalization"] = {
                "integrated_lufs": job.pre_normalization.integrated_lufs,
                "loudness_range_lu": job.pre_normalization.loudness_range_lu,
                "true_peak_dbtp": job.pre_normalization.true_peak_dbtp,
                "dynamic_range_db": job.pre_normalization.dynamic_range_db
            }
        
        if job.post_normalization:
            result["post_normalization"] = {
                "integrated_lufs": job.post_normalization.integrated_lufs,
                "loudness_range_lu": job.post_normalization.loudness_range_lu,
                "true_peak_dbtp": job.post_normalization.true_peak_dbtp,
                "dynamic_range_db": job.post_normalization.dynamic_range_db
            }
        
        return result
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive loudness normalization metrics."""
        compliance_rate = (self.metrics.compliant_jobs / max(1, self.metrics.total_jobs))
        
        return {
            "overview": {
                "total_jobs": self.metrics.total_jobs,
                "compliant_jobs": self.metrics.compliant_jobs,
                "non_compliant_jobs": self.metrics.non_compliant_jobs,
                "compliance_rate": round(compliance_rate, 3),
                "average_compliance_score": round(self.metrics.average_compliance_score, 3),
                "average_gain_adjustment_db": round(self.metrics.average_gain_adjustment_db, 2),
                "average_processing_time_ms": round(self.metrics.average_processing_time_ms, 1)
            },
            "standard_compliance": self.metrics.standard_compliance,
            "target_distribution": self.metrics.target_distribution,
            "gain_statistics": self._get_gain_statistics(),
            "compliance_trend": self._get_compliance_trend(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_gain_statistics(self) -> Dict[str, float]:
        """Get gain adjustment statistics."""
        if not self.gain_distribution:
            return {}
        
        return {
            "mean_db": round(statistics.mean(self.gain_distribution), 2),
            "median_db": round(statistics.median(self.gain_distribution), 2),
            "std_dev_db": round(statistics.stdev(self.gain_distribution) if len(self.gain_distribution) > 1 else 0.0, 2),
            "min_db": round(min(self.gain_distribution), 2),
            "max_db": round(max(self.gain_distribution), 2)
        }
    
    def _get_compliance_trend(self) -> Dict[str, Any]:
        """Get compliance trend over time."""
        if len(self.compliance_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_scores = [score for _, score in self.compliance_history[-10:]]
        older_scores = [score for _, score in self.compliance_history[-20:-10]] if len(self.compliance_history) >= 20 else []
        
        recent_avg = statistics.mean(recent_scores)
        
        if older_scores:
            older_avg = statistics.mean(older_scores)
            trend = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "recent_average": round(recent_avg, 3),
            "sample_size": len(recent_scores)
        }

# Create default instance
loudness_monitor = LoudnessNormalizationMonitor()

__all__ = [
    'LoudnessNormalizationMonitor',
    'NormalizationJob',
    'LoudnessStandard',
    'BroadcastTarget',
    'LoudnessTargets',
    'LoudnessMeasurement',
    'loudness_monitor'
]