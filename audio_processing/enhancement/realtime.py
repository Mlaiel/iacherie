"""
Real-time Audio Enhancement Engine
=================================

High-performance real-time audio enhancement system for live streaming,
broadcasting, and real-time content creation. Provides ultra-low latency
processing with professional audio quality.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: 2025 Fahed Mlaiel. All rights reserved.

WARNING: This code is proprietary and confidential. Unauthorized use, reproduction, 
or distribution without explicit written permission from Fahed Mlaiel is strictly 
prohibited and will be prosecuted to the full extent of the law.
"""

import numpy as np
import threading
import queue
import time
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import deque
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .processor import (
    AudioEnhancementProcessor, 
    EnhancementParameters, 
    ContentType,
    EnhancementResult
)
from ..core.exceptions import AudioProcessingError


class ProcessingMode(Enum):
    """Real-time processing modes"""
    LOW_LATENCY = "low_latency"      # < 10ms
    BALANCED = "balanced"            # 10-50ms  
    HIGH_QUALITY = "high_quality"    # 50-100ms
    ULTRA_QUALITY = "ultra_quality"  # 100ms+


@dataclass
class RealTimeConfig:
    """Real-time processing configuration"""
    buffer_size: int = 512          # Samples per buffer
    sample_rate: int = 44100        # Sample rate in Hz
    channels: int = 2               # Number of channels
    processing_mode: ProcessingMode = ProcessingMode.BALANCED
    max_latency_ms: float = 50.0    # Maximum acceptable latency
    enable_lookahead: bool = True   # Enable lookahead processing
    lookahead_samples: int = 256    # Lookahead buffer size
    thread_priority: int = 1        # Processing thread priority


@dataclass 
class LatencyMetrics:
    """Real-time latency performance metrics"""
    input_latency_ms: float = 0.0
    processing_latency_ms: float = 0.0
    output_latency_ms: float = 0.0
    total_latency_ms: float = 0.0
    buffer_underruns: int = 0
    buffer_overruns: int = 0
    cpu_usage_percent: float = 0.0


class AudioBuffer:
    """Thread-safe circular audio buffer for real-time processing"""
    
    def __init__(self, size: int, channels: int = 2):
        self.size = size
        self.channels = channels
        self.buffer = np.zeros((size, channels), dtype=np.float32)
        self.write_pos = 0
        self.read_pos = 0
        self.lock = threading.RLock()
        self.available_samples = 0
        
    def write(self, data: np.ndarray) -> bool:
        """Write audio data to buffer"""
        with self.lock:
            if len(data.shape) == 1:
                data = data.reshape(-1, 1)
            
            samples_to_write = min(data.shape[0], self.size - self.available_samples)
            if samples_to_write <= 0:
                return False  # Buffer overflow
            
            # Handle wrap-around
            if self.write_pos + samples_to_write <= self.size:
                self.buffer[self.write_pos:self.write_pos + samples_to_write] = \
                    data[:samples_to_write]
            else:
                # Split write
                first_part = self.size - self.write_pos
                self.buffer[self.write_pos:] = data[:first_part]
                remaining = samples_to_write - first_part
                self.buffer[:remaining] = data[first_part:samples_to_write]
            
            self.write_pos = (self.write_pos + samples_to_write) % self.size
            self.available_samples += samples_to_write
            
            return True
    
    def read(self, num_samples: int) -> Optional[np.ndarray]:
        """Read audio data from buffer"""
        with self.lock:
            if self.available_samples < num_samples:
                return None  # Buffer underrun
            
            # Handle wrap-around
            if self.read_pos + num_samples <= self.size:
                data = self.buffer[self.read_pos:self.read_pos + num_samples].copy()
            else:
                # Split read
                first_part = self.size - self.read_pos
                data = np.zeros((num_samples, self.channels), dtype=np.float32)
                data[:first_part] = self.buffer[self.read_pos:]
                remaining = num_samples - first_part
                data[first_part:] = self.buffer[:remaining]
            
            self.read_pos = (self.read_pos + num_samples) % self.size
            self.available_samples -= num_samples
            
            return data
    
    def get_available_samples(self) -> int:
        """Get number of available samples in buffer"""
        with self.lock:
            return self.available_samples
    
    def get_free_space(self) -> int:
        """Get number of free samples in buffer"""
        with self.lock:
            return self.size - self.available_samples
    
    def clear(self):
        """Clear buffer contents"""
        with self.lock:
            self.buffer.fill(0.0)
            self.write_pos = 0
            self.read_pos = 0
            self.available_samples = 0


class RealTimeEnhancer:
    """
    Real-Time Audio Enhancement Engine
    
    High-performance real-time audio processing system designed for
    live streaming, broadcasting, and interactive audio applications.
    """
    
    def __init__(self, config: RealTimeConfig):
        """Initialize real-time audio enhancer"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Core processor
        self.processor = AudioEnhancementProcessor()
        
        # Audio buffers
        buffer_size = max(8192, config.buffer_size * 16)  # Large enough for stable processing
        self.input_buffer = AudioBuffer(buffer_size, config.channels)
        self.output_buffer = AudioBuffer(buffer_size, config.channels)
        
        # Processing state
        self.is_running = False
        self.processing_thread = None
        self.enhancement_parameters = EnhancementParameters()
        
        # Latency monitoring
        self.latency_metrics = LatencyMetrics()
        self.latency_history = deque(maxlen=1000)  # Keep last 1000 measurements
        
        # Performance monitoring
        self.cpu_usage_monitor = deque(maxlen=100)
        self.buffer_status_monitor = deque(maxlen=100)
        
        # Callbacks
        self.audio_callback: Optional[Callable[[np.ndarray], None]] = None
        self.error_callback: Optional[Callable[[Exception], None]] = None
        
        # Adaptive processing
        self.adaptive_mode = True
        self.performance_target = 0.8  # Target CPU usage
        
        self.logger.info(f"Real-time enhancer initialized with {config.processing_mode.value} mode")
    
    def set_enhancement_parameters(self, parameters: EnhancementParameters):
        """Update enhancement parameters for real-time processing"""
        # Adapt parameters for real-time constraints
        self.enhancement_parameters = self._adapt_for_realtime(parameters)
        self.logger.debug("Enhancement parameters updated for real-time processing")
    
    def set_audio_callback(self, callback: Callable[[np.ndarray], None]):
        """Set callback for processed audio output"""
        self.audio_callback = callback
    
    def set_error_callback(self, callback: Callable[[Exception], None]):
        """Set callback for error handling"""
        self.error_callback = callback
    
    def start_processing(self) -> bool:
        """Start real-time audio processing"""
        if self.is_running:
            self.logger.warning("Real-time processing already running")
            return False
        
        try:
            self.is_running = True
            
            # Start processing thread with high priority
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                name="AudioEnhancementRT"
            )
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            self.logger.info("Real-time audio enhancement started")
            return True
            
        except Exception as e:
            self.is_running = False
            self.logger.error(f"Failed to start real-time processing: {str(e)}")
            return False
    
    def stop_processing(self):
        """Stop real-time audio processing"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        # Clear buffers
        self.input_buffer.clear()
        self.output_buffer.clear()
        
        self.logger.info("Real-time audio enhancement stopped")
    
    def process_audio_chunk(self, audio_chunk: np.ndarray) -> bool:
        """
        Process incoming audio chunk for real-time enhancement
        
        Args:
            audio_chunk: Input audio data
            
        Returns:
            True if chunk was successfully queued for processing
        """
        start_time = time.perf_counter()
        
        try:
            # Validate input
            if not self.is_running:
                return False
            
            # Convert to float32 if needed
            if audio_chunk.dtype != np.float32:
                audio_chunk = audio_chunk.astype(np.float32)
            
            # Ensure correct shape
            if len(audio_chunk.shape) == 1 and self.config.channels > 1:
                # Duplicate mono to stereo
                audio_chunk = np.column_stack([audio_chunk] * self.config.channels)
            elif len(audio_chunk.shape) == 2 and audio_chunk.shape[1] != self.config.channels:
                # Channel mismatch handling
                if audio_chunk.shape[1] == 1 and self.config.channels == 2:
                    audio_chunk = np.column_stack([audio_chunk[:, 0]] * 2)
                elif audio_chunk.shape[1] == 2 and self.config.channels == 1:
                    audio_chunk = np.mean(audio_chunk, axis=1, keepdims=True)
            
            # Write to input buffer
            success = self.input_buffer.write(audio_chunk)
            
            # Update input latency
            input_latency = (time.perf_counter() - start_time) * 1000
            self.latency_metrics.input_latency_ms = input_latency
            
            if not success:
                self.latency_metrics.buffer_overruns += 1
                self.logger.warning("Input buffer overflow - audio data dropped")
            
            return success
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(e)
            self.logger.error(f"Error processing audio chunk: {str(e)}")
            return False
    
    def get_processed_audio(self, num_samples: int) -> Optional[np.ndarray]:
        """
        Get processed audio from output buffer
        
        Args:
            num_samples: Number of samples to retrieve
            
        Returns:
            Processed audio data or None if not enough data available
        """
        start_time = time.perf_counter()
        
        try:
            data = self.output_buffer.read(num_samples)
            
            if data is None:
                self.latency_metrics.buffer_underruns += 1
                # Generate silence to maintain audio stream
                data = np.zeros((num_samples, self.config.channels), dtype=np.float32)
            
            # Update output latency
            output_latency = (time.perf_counter() - start_time) * 1000
            self.latency_metrics.output_latency_ms = output_latency
            
            # Calculate total latency
            self.latency_metrics.total_latency_ms = (
                self.latency_metrics.input_latency_ms +
                self.latency_metrics.processing_latency_ms +
                self.latency_metrics.output_latency_ms
            )
            
            return data
            
        except Exception as e:
            if self.error_callback:
                self.error_callback(e)
            self.logger.error(f"Error getting processed audio: {str(e)}")
            return np.zeros((num_samples, self.config.channels), dtype=np.float32)
    
    def _processing_loop(self):
        """Main real-time processing loop"""
        self.logger.info("Real-time processing loop started")
        
        try:
            while self.is_running:
                start_time = time.perf_counter()
                
                # Check if we have enough input data
                available_samples = self.input_buffer.get_available_samples()
                if available_samples < self.config.buffer_size:
                    # Wait for more data
                    time.sleep(0.001)  # 1ms sleep
                    continue
                
                # Check output buffer space
                output_free_space = self.output_buffer.get_free_space()
                if output_free_space < self.config.buffer_size:
                    # Output buffer full, wait
                    time.sleep(0.001)
                    continue
                
                # Read input data
                input_data = self.input_buffer.read(self.config.buffer_size)
                if input_data is None:
                    continue
                
                # Process audio chunk
                try:
                    processed_data = self._process_chunk_realtime(input_data)
                except Exception as e:
                    self.logger.error(f"Processing error: {str(e)}")
                    # Pass through original audio on error
                    processed_data = input_data
                
                # Write processed data to output buffer
                self.output_buffer.write(processed_data)
                
                # Call audio callback if set
                if self.audio_callback:
                    try:
                        self.audio_callback(processed_data)
                    except Exception as e:
                        self.logger.error(f"Audio callback error: {str(e)}")
                
                # Update processing latency
                processing_time = (time.perf_counter() - start_time) * 1000
                self.latency_metrics.processing_latency_ms = processing_time
                
                # Monitor performance
                self._update_performance_metrics(processing_time)
                
                # Adaptive quality adjustment
                if self.adaptive_mode:
                    self._adjust_quality_for_performance()
                
        except Exception as e:
            self.logger.error(f"Processing loop error: {str(e)}")
            if self.error_callback:
                self.error_callback(e)
        
        self.logger.info("Real-time processing loop ended")
    
    def _process_chunk_realtime(self, audio_chunk: np.ndarray) -> np.ndarray:
        """Process single audio chunk with real-time constraints"""
        # Simplified processing chain for real-time performance
        processed = audio_chunk.copy()
        
        # Apply only essential enhancements based on processing mode
        if self.config.processing_mode == ProcessingMode.LOW_LATENCY:
            # Minimal processing for ultra-low latency
            processed = self._apply_fast_enhancement(processed)
            
        elif self.config.processing_mode == ProcessingMode.BALANCED:
            # Balanced processing
            processed = self._apply_balanced_enhancement(processed)
            
        elif self.config.processing_mode in [ProcessingMode.HIGH_QUALITY, ProcessingMode.ULTRA_QUALITY]:
            # Full processing with quality priority
            try:
                result = self.processor.enhance_audio(
                    processed, 
                    self.config.sample_rate,
                    self.enhancement_parameters,
                    ContentType.GENERAL
                )
                processed = result.enhanced_audio
            except Exception:
                # Fallback to balanced processing
                processed = self._apply_balanced_enhancement(processed)
        
        return processed
    
    def _apply_fast_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply minimal enhancement for ultra-low latency"""
        # Simple gain normalization
        peak = np.max(np.abs(audio))
        if peak > 0.95:
            audio = audio * (0.95 / peak)
        
        # Basic high-frequency emphasis
        if len(audio.shape) > 1:
            # Simple stereo enhancement
            if audio.shape[1] == 2:
                mid = (audio[:, 0] + audio[:, 1]) / 2
                side = (audio[:, 0] - audio[:, 1]) / 2 * 1.1
                audio[:, 0] = mid + side
                audio[:, 1] = mid - side
        
        return audio
    
    def _apply_balanced_enhancement(self, audio: np.ndarray) -> np.ndarray:
        """Apply balanced enhancement for moderate latency"""
        # Noise gate
        gate_threshold = 0.01
        mask = np.abs(audio) > gate_threshold
        audio = audio * mask
        
        # Simple compression
        threshold = 0.7
        ratio = 3.0
        
        above_threshold = np.abs(audio) > threshold
        compressed = np.sign(audio) * (threshold + (np.abs(audio) - threshold) / ratio)
        audio = np.where(above_threshold, compressed, audio)
        
        # Normalize
        peak = np.max(np.abs(audio))
        if peak > 0:
            audio = audio * (0.9 / peak)
        
        return audio
    
    def _adapt_for_realtime(self, parameters: EnhancementParameters) -> EnhancementParameters:
        """Adapt enhancement parameters for real-time constraints"""
        adapted = EnhancementParameters(**parameters.__dict__)
        
        # Reduce processing intensity based on mode
        if self.config.processing_mode == ProcessingMode.LOW_LATENCY:
            adapted.noise_reduction_strength *= 0.3
            adapted.spectral_enhancement_gain *= 0.5
            adapted.multiband_processing = False
            adapted.high_quality_mode = False
            
        elif self.config.processing_mode == ProcessingMode.BALANCED:
            adapted.noise_reduction_strength *= 0.7
            adapted.spectral_enhancement_gain *= 0.8
            adapted.high_quality_mode = False
        
        return adapted
    
    def _update_performance_metrics(self, processing_time_ms: float):
        """Update performance monitoring metrics"""
        # CPU usage estimation
        max_time_ms = (self.config.buffer_size / self.config.sample_rate) * 1000
        cpu_usage = min(100.0, (processing_time_ms / max_time_ms) * 100)
        
        self.latency_metrics.cpu_usage_percent = cpu_usage
        self.cpu_usage_monitor.append(cpu_usage)
        
        # Buffer status
        input_usage = self.input_buffer.get_available_samples() / self.input_buffer.size
        output_usage = self.output_buffer.get_available_samples() / self.output_buffer.size
        self.buffer_status_monitor.append((input_usage, output_usage))
        
        # Latency history
        self.latency_history.append(self.latency_metrics.total_latency_ms)
    
    def _adjust_quality_for_performance(self):
        """Adaptively adjust processing quality based on performance"""
        if len(self.cpu_usage_monitor) < 10:
            return
        
        avg_cpu = np.mean(list(self.cpu_usage_monitor)[-10:])
        
        # Reduce quality if CPU usage is too high
        if avg_cpu > self.performance_target * 100:
            if self.config.processing_mode == ProcessingMode.HIGH_QUALITY:
                self.config.processing_mode = ProcessingMode.BALANCED
                self.logger.info("Reduced processing quality due to high CPU usage")
            elif self.config.processing_mode == ProcessingMode.BALANCED:
                self.config.processing_mode = ProcessingMode.LOW_LATENCY
                self.logger.info("Switched to low-latency mode due to high CPU usage")
        
        # Increase quality if CPU usage is low
        elif avg_cpu < self.performance_target * 50:
            if self.config.processing_mode == ProcessingMode.LOW_LATENCY:
                self.config.processing_mode = ProcessingMode.BALANCED
                self.logger.info("Increased processing quality due to low CPU usage")
            elif self.config.processing_mode == ProcessingMode.BALANCED:
                self.config.processing_mode = ProcessingMode.HIGH_QUALITY
                self.logger.info("Switched to high-quality mode due to low CPU usage")
    
    def get_latency_metrics(self) -> LatencyMetrics:
        """Get current latency performance metrics"""
        return self.latency_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if len(self.latency_history) == 0:
            return {}
        
        latencies = list(self.latency_history)
        cpu_usages = list(self.cpu_usage_monitor)
        
        return {
            'latency_stats': {
                'current_ms': self.latency_metrics.total_latency_ms,
                'average_ms': np.mean(latencies),
                'min_ms': np.min(latencies),
                'max_ms': np.max(latencies),
                'std_ms': np.std(latencies)
            },
            'cpu_stats': {
                'current_percent': self.latency_metrics.cpu_usage_percent,
                'average_percent': np.mean(cpu_usages) if cpu_usages else 0.0,
                'max_percent': np.max(cpu_usages) if cpu_usages else 0.0
            },
            'buffer_stats': {
                'underruns': self.latency_metrics.buffer_underruns,
                'overruns': self.latency_metrics.buffer_overruns,
                'input_available': self.input_buffer.get_available_samples(),
                'output_available': self.output_buffer.get_available_samples()
            },
            'processing_mode': self.config.processing_mode.value,
            'is_running': self.is_running
        }
    
    def reset_performance_metrics(self):
        """Reset all performance metrics"""
        self.latency_metrics = LatencyMetrics()
        self.latency_history.clear()
        self.cpu_usage_monitor.clear()
        self.buffer_status_monitor.clear()
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """Get detailed buffer status information"""
        return {
            'input_buffer': {
                'size': self.input_buffer.size,
                'available_samples': self.input_buffer.get_available_samples(),
                'free_space': self.input_buffer.get_free_space(),
                'usage_percent': (self.input_buffer.get_available_samples() / 
                                self.input_buffer.size) * 100
            },
            'output_buffer': {
                'size': self.output_buffer.size,
                'available_samples': self.output_buffer.get_available_samples(), 
                'free_space': self.output_buffer.get_free_space(),
                'usage_percent': (self.output_buffer.get_available_samples() /
                                self.output_buffer.size) * 100
            }
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.start_processing()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_processing()
