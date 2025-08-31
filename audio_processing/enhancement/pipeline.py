"""
Audio Enhancement Pipeline Orchestrator
=======================================

High-level orchestration system for audio enhancement workflows.
Combines multiple enhancement processors, quality analysis, and configuration
management into cohesive processing pipelines for different use cases.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Union, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .processor import AudioEnhancementProcessor, EnhancementParameters, EnhancementResult, ContentType
from .quality_analyzer import AudioQualityAnalyzer, QualityMetrics, ComparisonResult
from .config_manager import EnhancementConfigManager, EnhancementPreset, PresetCategory
from .realtime import RealTimeEnhancer, RealTimeConfig, ProcessingMode
from ..core.exceptions import AudioProcessingError
from ..core.validators import AudioValidator


class PipelineMode(Enum):
    """Processing pipeline modes"""
    SINGLE_PASS = "single_pass"              # One-time enhancement
    MULTI_PASS = "multi_pass"                # Multiple enhancement passes
    ADAPTIVE_QUALITY = "adaptive_quality"    # Quality-guided enhancement
    REAL_TIME = "real_time"                  # Real-time processing
    BATCH_PROCESSING = "batch_processing"    # Batch file processing


class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PipelineConfig:
    """Audio enhancement pipeline configuration"""
    mode: PipelineMode = PipelineMode.SINGLE_PASS
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    target_quality_score: float = 75.0
    max_processing_time: float = 300.0  # seconds
    enable_quality_validation: bool = True
    enable_progress_callback: bool = False
    enable_intermediate_results: bool = False
    max_passes: int = 3
    quality_improvement_threshold: float = 5.0
    parallel_processing: bool = True
    max_workers: int = 4


@dataclass
class ProcessingTask:
    """Individual processing task definition"""
    task_id: str
    audio: np.ndarray
    sample_rate: int
    content_type: ContentType = ContentType.GENERAL
    preset_name: Optional[str] = None
    custom_parameters: Optional[EnhancementParameters] = None
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    callback: Optional[Callable[[str, EnhancementResult], None]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineResult:
    """Complete pipeline processing result"""
    task_id: str
    success: bool
    enhancement_result: Optional[EnhancementResult] = None
    quality_metrics: Optional[QualityMetrics] = None
    comparison_result: Optional[ComparisonResult] = None
    processing_time: float = 0.0
    passes_completed: int = 0
    error_message: str = ""
    warnings: List[str] = field(default_factory=list)
    intermediate_results: List[EnhancementResult] = field(default_factory=list)


class AudioEnhancementPipeline:
    """
    Professional Audio Enhancement Pipeline Orchestrator
    
    High-level orchestration system that combines audio enhancement processing,
    quality analysis, and configuration management into comprehensive workflows.
    """
    
    def __init__(self, 
                 config: Optional[PipelineConfig] = None,
                 config_dir: Optional[Union[str, Path]] = None):
        """Initialize audio enhancement pipeline"""
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.config = config or PipelineConfig()
        
        # Core components
        self.processor = AudioEnhancementProcessor()
        self.quality_analyzer = AudioQualityAnalyzer()
        self.config_manager = EnhancementConfigManager(config_dir)
        self.validator = AudioValidator()
        
        # Real-time processor (initialized on demand)
        self.realtime_processor: Optional[RealTimeEnhancer] = None
        
        # Processing state
        self.active_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: Dict[str, PipelineResult] = {}
        self.processing_lock = threading.RLock()
        
        # Task queue for batch processing
        self.task_queue: List[ProcessingTask] = []
        self.batch_executor: Optional[ThreadPoolExecutor] = None
        
        # Progress callbacks
        self.progress_callbacks: List[Callable[[str, str, float], None]] = []
        
        self.logger.info("Audio enhancement pipeline initialized")
    
    def add_progress_callback(self, callback: Callable[[str, str, float], None]):
        """Add progress callback function"""
        self.progress_callbacks.append(callback)
    
    def remove_progress_callback(self, callback: Callable[[str, str, float], None]):
        """Remove progress callback function"""
        if callback in self.progress_callbacks:
            self.progress_callbacks.remove(callback)
    
    def _notify_progress(self, task_id: str, stage: str, progress: float):
        """Notify progress callbacks"""
        if self.config.enable_progress_callback:
            for callback in self.progress_callbacks:
                try:
                    callback(task_id, stage, progress)
                except Exception as e:
                    self.logger.warning(f"Progress callback error: {str(e)}")
    
    def process_audio(self, 
                     audio: np.ndarray,
                     sample_rate: int,
                     task_id: Optional[str] = None,
                     content_type: ContentType = ContentType.GENERAL,
                     preset_name: Optional[str] = None,
                     custom_parameters: Optional[EnhancementParameters] = None,
                     priority: ProcessingPriority = ProcessingPriority.NORMAL) -> PipelineResult:
        """
        Process single audio input through enhancement pipeline
        
        Args:
            audio: Input audio signal
            sample_rate: Sample rate in Hz
            task_id: Optional task identifier
            content_type: Type of audio content
            preset_name: Enhancement preset name
            custom_parameters: Custom enhancement parameters
            priority: Processing priority
            
        Returns:
            PipelineResult with processing outcomes
        """
        if task_id is None:
            task_id = f"task_{int(time.time() * 1000)}"
        
        start_time = time.time()
        result = PipelineResult(task_id=task_id, success=False)
        
        try:
            # Validate input
            self.validator.validate_audio_array(audio, sample_rate)
            self._notify_progress(task_id, "validation", 0.1)
            
            # Get enhancement parameters
            parameters = self._get_enhancement_parameters(
                content_type, preset_name, custom_parameters, audio, sample_rate
            )
            self._notify_progress(task_id, "parameter_setup", 0.2)
            
            # Initial quality analysis
            original_metrics = None
            if self.config.enable_quality_validation:
                original_metrics = self.quality_analyzer.analyze_quality(audio, sample_rate)
                self._notify_progress(task_id, "initial_quality_analysis", 0.3)
            
            # Process based on pipeline mode
            if self.config.mode == PipelineMode.SINGLE_PASS:
                enhancement_result = self._single_pass_processing(
                    audio, sample_rate, parameters, task_id
                )
                result.passes_completed = 1
                
            elif self.config.mode == PipelineMode.MULTI_PASS:
                enhancement_result = self._multi_pass_processing(
                    audio, sample_rate, parameters, task_id, result
                )
                
            elif self.config.mode == PipelineMode.ADAPTIVE_QUALITY:
                enhancement_result = self._adaptive_quality_processing(
                    audio, sample_rate, parameters, original_metrics, task_id, result
                )
                
            else:
                raise AudioProcessingError(f"Unsupported pipeline mode: {self.config.mode}")
            
            result.enhancement_result = enhancement_result
            self._notify_progress(task_id, "enhancement_complete", 0.8)
            
            # Final quality analysis and comparison
            if self.config.enable_quality_validation and original_metrics:
                final_metrics = self.quality_analyzer.analyze_quality(
                    enhancement_result.enhanced_audio, sample_rate
                )
                comparison = self.quality_analyzer.compare_quality(
                    audio, enhancement_result.enhanced_audio, sample_rate
                )
                
                result.quality_metrics = final_metrics
                result.comparison_result = comparison
                
                # Add quality-based warnings
                if comparison.overall_improvement < 0:
                    result.warnings.append("Enhancement may have degraded audio quality")
                
            self._notify_progress(task_id, "quality_analysis", 0.95)
            
            # Finalize result
            result.success = True
            result.processing_time = time.time() - start_time
            
            # Store completed task
            with self.processing_lock:
                self.completed_tasks[task_id] = result
            
            self._notify_progress(task_id, "complete", 1.0)
            self.logger.info(f"Pipeline processing completed for task {task_id} "
                           f"in {result.processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            result.processing_time = time.time() - start_time
            
            self.logger.error(f"Pipeline processing failed for task {task_id}: {str(e)}")
            return result
    
    def _get_enhancement_parameters(self, 
                                   content_type: ContentType,
                                   preset_name: Optional[str],
                                   custom_parameters: Optional[EnhancementParameters],
                                   audio: np.ndarray,
                                   sample_rate: int) -> EnhancementParameters:
        """Get enhancement parameters from preset or custom settings"""
        if custom_parameters:
            return custom_parameters
        
        if preset_name:
            preset = self.config_manager.get_preset(preset_name)
            if preset:
                # Analyze audio for adaptive parameters
                content_analysis = self._analyze_audio_content(audio, sample_rate)
                return self.config_manager.create_adaptive_parameters(
                    preset, content_analysis
                )
        
        # Get default preset for content type
        preset = self.config_manager.get_preset_for_content(content_type)
        if preset:
            content_analysis = self._analyze_audio_content(audio, sample_rate)
            return self.config_manager.create_adaptive_parameters(preset, content_analysis)
        
        # Fallback to default parameters
        return EnhancementParameters()
    
    def _analyze_audio_content(self, audio: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Analyze audio content for adaptive parameter selection"""
        analysis = {}
        
        try:
            # Basic metrics
            rms = np.sqrt(np.mean(audio ** 2))
            peak = np.max(np.abs(audio))
            
            analysis['rms_level'] = rms
            analysis['peak_level'] = peak
            analysis['dynamic_range'] = 20 * np.log10(peak / (rms + 1e-10))
            
            # Noise level estimation
            sorted_samples = np.sort(np.abs(audio))
            noise_threshold = sorted_samples[int(len(sorted_samples) * 0.1)]  # Bottom 10%
            noise_level = noise_threshold / (rms + 1e-10)
            analysis['noise_level'] = min(1.0, noise_level)
            
            # Spectral analysis
            if len(audio) > 1024:
                import librosa
                spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
                spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
                
                analysis['spectral_content'] = {
                    'centroid': np.mean(spectral_centroid),
                    'bandwidth': np.mean(spectral_bandwidth),
                    'high_frequency_energy': np.mean(spectral_centroid) / (sample_rate / 4)
                }
                
                # Simple speech detection
                zcr = librosa.feature.zero_crossing_rate(audio)[0]
                speech_indicators = np.mean(zcr) < 0.1 and 1000 < np.mean(spectral_centroid) < 4000
                analysis['speech_probability'] = 0.8 if speech_indicators else 0.3
            
        except Exception as e:
            self.logger.warning(f"Content analysis warning: {str(e)}")
        
        return analysis
    
    def _single_pass_processing(self, 
                               audio: np.ndarray,
                               sample_rate: int,
                               parameters: EnhancementParameters,
                               task_id: str) -> EnhancementResult:
        """Single pass enhancement processing"""
        self._notify_progress(task_id, "single_pass_enhancement", 0.4)
        
        result = self.processor.enhance_audio(
            audio, sample_rate, parameters, ContentType.GENERAL
        )
        
        self._notify_progress(task_id, "single_pass_complete", 0.7)
        return result
    
    def _multi_pass_processing(self,
                              audio: np.ndarray,
                              sample_rate: int,
                              parameters: EnhancementParameters,
                              task_id: str,
                              result: PipelineResult) -> EnhancementResult:
        """Multi-pass enhancement processing"""
        current_audio = audio.copy()
        best_result = None
        best_quality_score = 0.0
        
        for pass_num in range(1, self.config.max_passes + 1):
            progress = 0.4 + (pass_num - 1) * 0.3 / self.config.max_passes
            self._notify_progress(task_id, f"pass_{pass_num}", progress)
            
            # Adjust parameters for each pass
            pass_parameters = self._adjust_parameters_for_pass(parameters, pass_num)
            
            # Enhance current audio
            enhancement_result = self.processor.enhance_audio(
                current_audio, sample_rate, pass_parameters, ContentType.GENERAL
            )
            
            # Store intermediate result if enabled
            if self.config.enable_intermediate_results:
                result.intermediate_results.append(enhancement_result)
            
            # Evaluate quality
            if self.config.enable_quality_validation:
                quality_metrics = self.quality_analyzer.analyze_quality(
                    enhancement_result.enhanced_audio, sample_rate
                )
                
                if quality_metrics.overall_quality_score > best_quality_score:
                    best_result = enhancement_result
                    best_quality_score = quality_metrics.overall_quality_score
                
                # Check if target quality achieved
                if quality_metrics.overall_quality_score >= self.config.target_quality_score:
                    result.passes_completed = pass_num
                    self.logger.info(f"Target quality achieved in pass {pass_num}")
                    break
            else:
                best_result = enhancement_result
            
            # Prepare for next pass
            current_audio = enhancement_result.enhanced_audio
            result.passes_completed = pass_num
        
        return best_result or enhancement_result
    
    def _adaptive_quality_processing(self,
                                   audio: np.ndarray,
                                   sample_rate: int,
                                   parameters: EnhancementParameters,
                                   original_metrics: Optional[QualityMetrics],
                                   task_id: str,
                                   result: PipelineResult) -> EnhancementResult:
        """Adaptive quality-guided processing"""
        current_audio = audio.copy()
        current_parameters = parameters
        best_result = None
        best_improvement = -float('inf')
        
        for pass_num in range(1, self.config.max_passes + 1):
            progress = 0.4 + (pass_num - 1) * 0.3 / self.config.max_passes
            self._notify_progress(task_id, f"adaptive_pass_{pass_num}", progress)
            
            # Enhance audio
            enhancement_result = self.processor.enhance_audio(
                current_audio, sample_rate, current_parameters, ContentType.GENERAL
            )
            
            if self.config.enable_intermediate_results:
                result.intermediate_results.append(enhancement_result)
            
            # Analyze quality and improvement
            current_metrics = self.quality_analyzer.analyze_quality(
                enhancement_result.enhanced_audio, sample_rate
            )
            
            if original_metrics:
                improvement = current_metrics.overall_quality_score - original_metrics.overall_quality_score
            else:
                improvement = current_metrics.overall_quality_score
            
            # Update best result
            if improvement > best_improvement:
                best_result = enhancement_result
                best_improvement = improvement
            
            # Check termination conditions
            if improvement >= self.config.quality_improvement_threshold:
                result.passes_completed = pass_num
                break
            
            if improvement < 1.0 and pass_num > 1:
                # Diminishing returns, stop processing
                result.warnings.append("Stopped processing due to diminishing quality returns")
                break
            
            # Adapt parameters for next pass based on current quality
            current_parameters = self._adapt_parameters_for_quality(
                current_parameters, current_metrics, original_metrics
            )
            
            current_audio = enhancement_result.enhanced_audio
            result.passes_completed = pass_num
        
        return best_result or enhancement_result
    
    def _adjust_parameters_for_pass(self, 
                                   base_parameters: EnhancementParameters,
                                   pass_number: int) -> EnhancementParameters:
        """Adjust parameters for multi-pass processing"""
        # Create copy to avoid modifying original
        adjusted = EnhancementParameters(**base_parameters.__dict__)
        
        # Reduce intensity for subsequent passes
        reduction_factor = 0.7 ** (pass_number - 1)
        
        adjusted.noise_reduction_strength *= reduction_factor
        adjusted.spectral_enhancement_gain *= reduction_factor
        adjusted.restoration_strength *= reduction_factor
        
        return adjusted
    
    def _adapt_parameters_for_quality(self,
                                     current_parameters: EnhancementParameters,
                                     current_metrics: QualityMetrics,
                                     original_metrics: Optional[QualityMetrics]) -> EnhancementParameters:
        """Adapt parameters based on current quality metrics"""
        adapted = EnhancementParameters(**current_parameters.__dict__)
        
        if original_metrics is None:
            return adapted
        
        # Adjust based on specific quality issues
        if current_metrics.snr_db < original_metrics.snr_db:
            # Increased noise, reduce noise reduction
            adapted.noise_reduction_strength = max(0.1, adapted.noise_reduction_strength * 0.8)
        
        if current_metrics.dynamic_range_db < original_metrics.dynamic_range_db - 3:
            # Reduced dynamics, ease compression
            adapted.dynamic_range_target = min(0.9, adapted.dynamic_range_target + 0.1)
        
        if current_metrics.thd_percent > original_metrics.thd_percent * 1.5:
            # Increased distortion, reduce enhancement
            adapted.spectral_enhancement_gain *= 0.7
            adapted.harmonic_emphasis *= 0.7
        
        return adapted
    
    def start_realtime_processing(self, 
                                 realtime_config: Optional[RealTimeConfig] = None) -> bool:
        """Start real-time processing mode"""
        if self.realtime_processor and self.realtime_processor.is_running:
            self.logger.warning("Real-time processing already running")
            return False
        
        try:
            if realtime_config is None:
                realtime_config = RealTimeConfig(
                    buffer_size=512,
                    processing_mode=ProcessingMode.BALANCED
                )
            
            self.realtime_processor = RealTimeEnhancer(realtime_config)
            success = self.realtime_processor.start_processing()
            
            if success:
                self.logger.info("Real-time processing started")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to start real-time processing: {str(e)}")
            return False
    
    def stop_realtime_processing(self):
        """Stop real-time processing mode"""
        if self.realtime_processor:
            self.realtime_processor.stop_processing()
            self.logger.info("Real-time processing stopped")
    
    def process_realtime_chunk(self, audio_chunk: np.ndarray) -> bool:
        """Process audio chunk in real-time mode"""
        if not self.realtime_processor or not self.realtime_processor.is_running:
            return False
        
        return self.realtime_processor.process_audio_chunk(audio_chunk)
    
    def get_realtime_output(self, num_samples: int) -> Optional[np.ndarray]:
        """Get processed real-time audio output"""
        if not self.realtime_processor:
            return None
        
        return self.realtime_processor.get_processed_audio(num_samples)
    
    def submit_batch_task(self, task: ProcessingTask):
        """Submit task for batch processing"""
        with self.processing_lock:
            self.task_queue.append(task)
            self.active_tasks[task.task_id] = task
        
        self.logger.debug(f"Submitted batch task: {task.task_id}")
    
    def start_batch_processing(self, max_workers: Optional[int] = None) -> bool:
        """Start batch processing of queued tasks"""
        if self.batch_executor and not self.batch_executor._shutdown:
            self.logger.warning("Batch processing already running")
            return False
        
        try:
            workers = max_workers or self.config.max_workers
            self.batch_executor = ThreadPoolExecutor(max_workers=workers)
            
            # Submit all queued tasks
            futures = []
            for task in self.task_queue.copy():
                future = self.batch_executor.submit(self._process_batch_task, task)
                futures.append((future, task.task_id))
            
            # Monitor completion
            def monitor_completion():
                for future, task_id in futures:
                    try:
                        result = future.result()
                        if task_id in self.active_tasks:
                            # Call task callback if provided
                            task = self.active_tasks[task_id]
                            if task.callback:
                                task.callback(task_id, result)
                            
                            # Move from active to completed
                            del self.active_tasks[task_id]
                            
                    except Exception as e:
                        self.logger.error(f"Batch task {task_id} failed: {str(e)}")
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=monitor_completion)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            self.logger.info(f"Started batch processing with {workers} workers, {len(futures)} tasks")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start batch processing: {str(e)}")
            return False
    
    def _process_batch_task(self, task: ProcessingTask) -> PipelineResult:
        """Process individual batch task"""



        return self.process_audio(
            task.audio,
            task.sample_rate,
            task.task_id,
            task.content_type,
            task.preset_name,
            task.custom_parameters,
            task.priority
        )
    
    def stop_batch_processing(self):
        """Stop batch processing"""
        if self.batch_executor:
            self.batch_executor.shutdown(wait=True)
            self.batch_executor = None
            self.logger.info("Batch processing stopped")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of specific task"""
        with self.processing_lock:
            if task_id in self.active_tasks:
                return {
                    'status': 'active',
                    'task': self.active_tasks[task_id]
                }
            elif task_id in self.completed_tasks:
                return {
                    'status': 'completed',
                    'result': self.completed_tasks[task_id]
                }
            else:
                return {'status': 'not_found'}
    
    def get_pipeline_statistics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline statistics"""
        with self.processing_lock:
            completed_results = list(self.completed_tasks.values())
        
        if not completed_results:
            return {
                'total_tasks': 0,
                'success_rate': 0.0,
                'average_processing_time': 0.0
            }
        
        successful_tasks = [r for r in completed_results if r.success]
        total_time = sum(r.processing_time for r in completed_results)
        
        stats = {
            'total_tasks': len(completed_results),
            'successful_tasks': len(successful_tasks),
            'failed_tasks': len(completed_results) - len(successful_tasks),
            'success_rate': len(successful_tasks) / len(completed_results) * 100,
            'average_processing_time': total_time / len(completed_results),
            'active_tasks': len(self.active_tasks),
            'queued_tasks': len(self.task_queue)
        }
        
        if successful_tasks:
            # Quality improvement statistics
            improvements = []
            for result in successful_tasks:
                if result.comparison_result:
                    improvements.append(result.comparison_result.overall_improvement)
            
            if improvements:
                stats['quality_improvements'] = {
                    'average': np.mean(improvements),
                    'median': np.median(improvements),
                    'min': np.min(improvements),
                    'max': np.max(improvements)
                }
        
        return stats
    
    def cleanup_completed_tasks(self, keep_recent: int = 100):
        """Clean up old completed tasks to free memory"""
        with self.processing_lock:
            if len(self.completed_tasks) <= keep_recent:
                return
            
            # Sort by completion time and keep most recent
            sorted_tasks = sorted(
                self.completed_tasks.items(),
                key=lambda x: x[1].processing_time,
                reverse=True
            )
            
            # Keep only recent tasks
            recent_tasks = dict(sorted_tasks[:keep_recent])
            removed_count = len(self.completed_tasks) - len(recent_tasks)
            
            self.completed_tasks = recent_tasks
            
        self.logger.info(f"Cleaned up {removed_count} completed tasks")
    
    def export_pipeline_config(self, file_path: Union[str, Path]):
        """Export pipeline configuration"""
        config_data = {
            'pipeline_config': {
                'mode': self.config.mode.value,
                'priority': self.config.priority.value,
                'target_quality_score': self.config.target_quality_score,
                'max_processing_time': self.config.max_processing_time,
                'enable_quality_validation': self.config.enable_quality_validation,
                'max_passes': self.config.max_passes,
                'quality_improvement_threshold': self.config.quality_improvement_threshold,
                'parallel_processing': self.config.parallel_processing,
                'max_workers': self.config.max_workers
            },
            'statistics': self.get_pipeline_statistics()
        }
        
        import json
        with open(file_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        self.logger.info(f"Pipeline configuration exported to {file_path}")
    
    def __enter__(self):
        """Context manager entry"""



        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_realtime_processing()
        self.stop_batch_processing()
