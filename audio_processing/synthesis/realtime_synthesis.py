"""🎵 Real-time Audio Synthesis Engine - Low-Latency Audio Generation

This module provides real-time audio synthesis capabilities with optimized
performance for streaming and interactive applications.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ LEGAL WARNING: Unauthorized use prohibited. Contact mlaiel@live.de for licensing.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import logging
import threading
import time
import queue
from collections import deque
import asyncio
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

logger = logging.getLogger(__name__)


@dataclass
class RealtimeConfig:
    """
Configuration for real-time synthesis."""
    # Audio settings
    sample_rate: int = 22050
    buffer_size: int = 1024
    max_buffer_size: int = 4096
    num_buffers: int = 4
    latency_target: float = 0.1  # seconds
    
    # Performance settings
    max_concurrent_streams: int = 8
    gpu_memory_fraction: float = 0.7
    cpu_threads: int = 4
    priority_synthesis: bool = True
    
    # Quality settings
    quality_level: str = "balanced"  # "fast", "balanced", "high"
    adaptive_quality: bool = True
    dynamic_buffering: bool = True
    
    # Monitoring settings
    enable_monitoring: bool = True
    log_performance: bool = True
    alert_threshold: float = 0.2  # latency threshold for alerts
    
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


class AudioBuffer:
    """Thread-safe circular audio buffer for real-time processing."""
    
    def __init__(self, size: int, sample_rate: int, channels: int = 1):
        self.size = size
        self.sample_rate = sample_rate
        self.channels = channels
        
        # Buffer storage
        self.buffer = np.zeros((size, channels), dtype=np.float32)
        self.write_pos = 0
        self.read_pos = 0
        self.available_samples = 0
        
        # Thread safety
        self.lock = threading.RLock()
        self.read_event = threading.Event()
        self.write_event = threading.Event()
        
        # Statistics
        self.underruns = 0
        self.overruns = 0
        
    def write(self, data: np.ndarray) -> int:
        """
Write audio data to buffer. Returns number of samples written."""
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
            
        samples_to_write = min(data.shape[0], self.size - self.available_samples)
        
        if samples_to_write == 0:
            self.overruns += 1
            return 0
            
        with self.lock:
            # Handle wrap-around
            if self.write_pos + samples_to_write <= self.size:
                self.buffer[self.write_pos:self.write_pos + samples_to_write] = data[:samples_to_write]
            else:
                # Split write
                first_part = self.size - self.write_pos
                self.buffer[self.write_pos:] = data[:first_part]
                self.buffer[:samples_to_write - first_part] = data[first_part:samples_to_write]
                
            self.write_pos = (self.write_pos + samples_to_write) % self.size
            self.available_samples += samples_to_write
            
        self.read_event.set()
        return samples_to_write
        
    def read(self, num_samples: int) -> np.ndarray:
        """
Read audio data from buffer."""
        samples_to_read = min(num_samples, self.available_samples)
        
        if samples_to_read == 0:
            self.underruns += 1
            return np.zeros((num_samples, self.channels), dtype=np.float32)
            
        with self.lock:
            # Handle wrap-around
            if self.read_pos + samples_to_read <= self.size:
                data = self.buffer[self.read_pos:self.read_pos + samples_to_read].copy()
            else:
                # Split read
                first_part = self.size - self.read_pos
                data = np.zeros((samples_to_read, self.channels), dtype=np.float32)
                data[:first_part] = self.buffer[self.read_pos:]
                data[first_part:] = self.buffer[:samples_to_read - first_part]
                
            self.read_pos = (self.read_pos + samples_to_read) % self.size
            self.available_samples -= samples_to_read
            
        self.write_event.set()
        
        # Pad with zeros if not enough samples
        if samples_to_read < num_samples:
            padding = np.zeros((num_samples - samples_to_read, self.channels), dtype=np.float32)
            data = np.vstack([data, padding])
            
        return data
        
    def get_fill_level(self) -> float:
        """
Get buffer fill level as fraction."""
        return self.available_samples / self.size
        
    def clear(self) -> None:
        """
Clear buffer contents."""
        with self.lock:
            self.buffer.fill(0)
            self.write_pos = 0
            self.read_pos = 0
            self.available_samples = 0


class StreamingProcessor:
    """
Base class for streaming audio processors."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.is_active = False
        self.processing_time = 0.0
        self.samples_processed = 0
        
    def process_chunk(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
Process audio chunk. Override in subclasses."""
        start_time = time.perf_counter()
        
        # Default: pass through
        result = audio_chunk
        
        # Update statistics
        self.processing_time += time.perf_counter() - start_time
        self.samples_processed += len(audio_chunk)
        
        return result
        
    def get_latency(self) -> float:
        """
Get processing latency."""
        if self.samples_processed == 0:
            return 0.0
        return self.processing_time / (self.samples_processed / self.config.sample_rate)


class RealtimeSynthesisEngine:
    """
Main real-time synthesis engine."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.device = torch.device(config.device)
        
        # Audio buffers
        self.input_buffer = AudioBuffer(
            config.buffer_size * config.num_buffers,
            config.sample_rate
        )
        self.output_buffer = AudioBuffer(
            config.buffer_size * config.num_buffers,
            config.sample_rate
        )
        
        # Processing components
        self.processors: List[StreamingProcessor] = []
        self.synthesis_models: Dict[str, nn.Module] = {}
        
        # Threading
        self.processing_thread = None
        self.is_running = False
        self.thread_pool = ThreadPoolExecutor(max_workers=config.cpu_threads)
        
        # Performance monitoring
        self.latency_monitor = LatencyMonitor(config)
        self.resource_monitor = ResourceManager(config)
        
        # Quality controller
        self.quality_controller = QualityOptimizer(config)
        
    def start(self) -> None:
        """
Start real-time processing."""
        if self.is_running:
            logger.warning("Engine already running")
            return
            
        self.is_running = True
        self.processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self.processing_thread.start()
        
        if self.config.enable_monitoring:
            self.latency_monitor.start()
            self.resource_monitor.start()
            
        logger.info("Real-time synthesis engine started")
        
    def stop(self) -> None:
        """Stop real-time processing."""
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.processing_thread:
            self.processing_thread.join(timeout=1.0)
            
        self.latency_monitor.stop()
        self.resource_monitor.stop()
        self.thread_pool.shutdown(wait=True)
        
        logger.info("Real-time synthesis engine stopped")
        
    def add_processor(self, processor: StreamingProcessor) -> None:
        """Add streaming processor to pipeline."""
        self.processors.append(processor)
        logger.info(f"Added processor: {type(processor).__name__}")
        
    def register_synthesis_model(self, name: str, model: nn.Module) -> None:
        """Register synthesis model."""
        model = model.to(self.device)
        model.eval()
        self.synthesis_models[name] = model
        logger.info(f"Registered synthesis model: {name}")
        
    def synthesize_realtime(self, input_data: Any, model_name: str = None) -> None:
        """Queue synthesis request for real-time processing."""
        # Convert input to audio chunk and add to buffer
        audio_chunk = self._convert_input_to_audio(input_data, model_name)
        
        if audio_chunk is not None:
            samples_written = self.input_buffer.write(audio_chunk)
            
            if samples_written < len(audio_chunk):
                logger.warning("Input buffer overflow, dropping samples")
                
    def read_output(self, num_samples: int) -> np.ndarray:
        """Read synthesized audio output."""
        return self.output_buffer.read(num_samples)
        
    def _processing_loop(self) -> None:
        """
Main processing loop."""
        chunk_size = self.config.buffer_size
        
        while self.is_running:
            try:
                # Read input chunk
                input_chunk = self.input_buffer.read(chunk_size)
                
                if np.sum(np.abs(input_chunk)) == 0:
                    # No input data, sleep briefly
                    time.sleep(0.001)
                    continue
                    
                # Process chunk
                start_time = time.perf_counter()
                processed_chunk = self._process_chunk(input_chunk)
                processing_time = time.perf_counter() - start_time
                
                # Update latency monitor
                self.latency_monitor.update_latency(processing_time)
                
                # Write output
                samples_written = self.output_buffer.write(processed_chunk)
                
                if samples_written < len(processed_chunk):
                    logger.warning("Output buffer overflow")
                    
                # Adaptive quality control
                if self.config.adaptive_quality:
                    self.quality_controller.adjust_quality(processing_time)
                    
            except Exception as e:
                logger.error(f"Processing loop error: {e}")
                time.sleep(0.001)
                
    def _process_chunk(self, chunk: np.ndarray) -> np.ndarray:
        """Process audio chunk through pipeline."""
        processed = chunk
        
        # Apply processors in sequence
        for processor in self.processors:
            if processor.is_active:
                processed = processor.process_chunk(processed)
                
        return processed
        
    def _convert_input_to_audio(self, input_data: Any, model_name: str = None) -> np.ndarray:
        """
Convert various input types to audio."""
        if isinstance(input_data, np.ndarray):
            return input_data.astype(np.float32)
        elif isinstance(input_data, torch.Tensor):
            return input_data.cpu().numpy().astype(np.float32)
        elif isinstance(input_data, str) and model_name:
            # Text-to-speech
            return self._synthesize_text(input_data, model_name)
        else:
            logger.warning(f"Unsupported input type: {type(input_data)}")
            return None
            
    def _synthesize_text(self, text: str, model_name: str) -> np.ndarray:
        """Synthesize text using specified model."""
        if model_name not in self.synthesis_models:
            logger.warning(f"Model {model_name} not found")
            return np.zeros(1000, dtype=np.float32)
            
        # Simplified synthesis (would use actual model)
        duration = len(text) * 0.1
        samples = int(duration * self.config.sample_rate)
        
        # Generate dummy audio
        t = np.linspace(0, duration, samples)
        freq = 220 + (len(text) % 100)
        audio = 0.3 * np.sin(2 * np.pi * freq * t)
        
        return audio.astype(np.float32)
        
    def get_status(self) -> Dict[str, Any]:
        """Get engine status information."""
        return {
            'is_running': self.is_running,
            'input_buffer_fill': self.input_buffer.get_fill_level(),
            'output_buffer_fill': self.output_buffer.get_fill_level(),
            'latency': self.latency_monitor.get_current_latency(),
            'cpu_usage': self.resource_monitor.get_cpu_usage(),
            'memory_usage': self.resource_monitor.get_memory_usage(),
            'quality_level': self.quality_controller.current_quality,
            'underruns': self.input_buffer.underruns + self.output_buffer.underruns,
            'overruns': self.input_buffer.overruns + self.output_buffer.overruns
        }


class StreamingSynthesizer(StreamingProcessor):
    """
Streaming synthesizer with chunked processing."""
    
    def __init__(self, config: RealtimeConfig, model: nn.Module):
        super().__init__(config)
        self.model = model.to(torch.device(config.device))
        self.model.eval()
        
        # Chunk overlap for smooth synthesis
        self.overlap_samples = config.buffer_size // 4
        self.previous_chunk = np.zeros(self.overlap_samples, dtype=np.float32)
        
    def process_chunk(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
Process audio chunk with overlap-add."""
        start_time = time.perf_counter()
        
        # Add overlap from previous chunk
        extended_chunk = np.concatenate([self.previous_chunk, audio_chunk.flatten()])
        
        # Convert to tensor
        input_tensor = torch.FloatTensor(extended_chunk).unsqueeze(0)
        input_tensor = input_tensor.to(torch.device(self.config.device))
        
        # Synthesize
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
            
        # Convert back to numpy
        output_chunk = output_tensor.cpu().numpy().squeeze()
        
        # Handle overlap
        if len(output_chunk) > len(audio_chunk):
            # Save overlap for next chunk
            self.previous_chunk = output_chunk[-self.overlap_samples:]
            output_chunk = output_chunk[:len(audio_chunk)]
        else:
            self.previous_chunk = np.zeros(self.overlap_samples, dtype=np.float32)
            
        # Update statistics
        self.processing_time += time.perf_counter() - start_time
        self.samples_processed += len(audio_chunk)
        
        return output_chunk.astype(np.float32)


class LowLatencySynthesis:
    """
Ultra-low latency synthesis optimizations."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        
        # Pre-allocated buffers
        self.temp_buffers = [
            np.zeros(config.buffer_size, dtype=np.float32)
            for _ in range(8)
        ]
        self.buffer_index = 0
        
        # Model optimizations
        self.quantized_models: Dict[str, nn.Module] = {}
        self.jit_models: Dict[str, torch.jit.ScriptModule] = {}
        
    def optimize_model(self, name: str, model: nn.Module) -> nn.Module:
        """
Optimize model for low latency."""
        # JIT compilation
        example_input = torch.randn(1, self.config.buffer_size)
        jit_model = torch.jit.trace(model, example_input)
        self.jit_models[name] = jit_model
        
        # Quantization
        quantized_model = torch.quantization.quantize_dynamic(
            model, {nn.Linear}, dtype=torch.qint8
        )
        self.quantized_models[name] = quantized_model
        
        logger.info(f"Model {name} optimized for low latency")
        return jit_model
        
    def get_temp_buffer(self, size: int = None) -> np.ndarray:
        """Get temporary buffer to avoid allocations."""
        if size is None:
            size = self.config.buffer_size
            
        if size <= self.config.buffer_size:
            buffer = self.temp_buffers[self.buffer_index]
            self.buffer_index = (self.buffer_index + 1) % len(self.temp_buffers)
            return buffer[:size]
        else:
            return np.zeros(size, dtype=np.float32)
            
    def synthesize_minimal_latency(self, input_data: np.ndarray,
                                  model_name: str) -> np.ndarray:
        """
Synthesize with minimal latency optimizations."""
        if model_name in self.jit_models:
            model = self.jit_models[model_name]
        elif model_name in self.quantized_models:
            model = self.quantized_models[model_name]
        else:
            raise ValueError(f"Optimized model {model_name} not found")
            
        # Use pre-allocated buffer
        output_buffer = self.get_temp_buffer(len(input_data))
        
        # Minimal tensor operations
        with torch.no_grad():
            input_tensor = torch.from_numpy(input_data).unsqueeze(0)
            output_tensor = model(input_tensor)
            output_buffer[:] = output_tensor.squeeze().cpu().numpy()
            
        return output_buffer


class BufferedSynthesisManager:
    """Manager for buffered synthesis with lookahead."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        
        # Multi-level buffering
        self.immediate_buffer = deque(maxlen=2)  # Current + next chunk
        self.lookahead_buffer = deque(maxlen=8)  # Future chunks
        self.emergency_buffer = deque(maxlen=4)  # Emergency backup
        
        # Synthesis worker
        self.synthesis_queue = queue.Queue(maxsize=16)
        self.result_queue = queue.Queue(maxsize=16)
        self.worker_thread = None
        self.is_active = False
        
    def start_buffered_synthesis(self) -> None:
        """
Start buffered synthesis worker."""
        self.is_active = True
        self.worker_thread = threading.Thread(
            target=self._synthesis_worker,
            daemon=True
        )
        self.worker_thread.start()
        logger.info("Buffered synthesis started")
        
    def stop_buffered_synthesis(self) -> None:
        """Stop buffered synthesis worker."""
        self.is_active = False
        if self.worker_thread:
            self.worker_thread.join(timeout=1.0)
        logger.info("Buffered synthesis stopped")
        
    def queue_synthesis(self, synthesis_request: Dict[str, Any]) -> None:
        """Queue synthesis request for background processing."""
        try:
            self.synthesis_queue.put_nowait(synthesis_request)
        except queue.Full:
            logger.warning("Synthesis queue full, dropping request")
            
    def get_next_chunk(self) -> Optional[np.ndarray]:
        try:
                    # Request validation
                    if not data:
                        raise ValueError("Invalid request")
            
                    # Process request
                    result = await self._handle_get_next_chunk_request(data)
            
                    # Return response
                    return {"status": "success", "data": result}
            
                except Exception as e:
                    logger.error(f"API handler get_next_chunk failed: {e}")
                    return {"status": "error", "message": str(e)}
    def _synthesis_worker(self) -> None:
        """Background synthesis worker."""
        while self.is_active:
            try:
                # Get synthesis request
                request = self.synthesis_queue.get(timeout=0.1)
                
                # Perform synthesis
                result = self._perform_synthesis(request)
                
                # Queue result
                try:
                    self.result_queue.put_nowait(result)
                except queue.Full:
                    logger.warning("Result queue full, dropping result")
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Synthesis worker error: {e}")
                
    def _perform_synthesis(self, request: Dict[str, Any]) -> np.ndarray:
        """Perform actual synthesis."""
        # Placeholder synthesis
        size = request.get('size', self.config.buffer_size)
        return np.random.randn(size).astype(np.float32) * 0.1


class AdaptiveSynthesisController:
    """
Adaptive controller for synthesis parameters."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        
        # Adaptation parameters
        self.target_latency = config.latency_target
        self.current_latency = 0.0
        self.latency_history = deque(maxlen=100)
        
        # Control parameters
        self.quality_levels = ['fast', 'balanced', 'high']
        self.current_quality_idx = 1  # Start with balanced
        
        # PID controller parameters
        self.kp = 1.0  # Proportional gain
        self.ki = 0.1  # Integral gain
        self.kd = 0.05  # Derivative gain
        
        self.integral_error = 0.0
        self.previous_error = 0.0
        
    def update_latency(self, latency: float) -> None:
        """
Update latency measurement and adapt parameters."""
        self.current_latency = latency
        self.latency_history.append(latency)
        
        # Calculate error
        error = latency - self.target_latency
        
        # PID control
        self.integral_error += error
        derivative_error = error - self.previous_error
        
        control_signal = (self.kp * error + 
                         self.ki * self.integral_error + 
                         self.kd * derivative_error)
                         
        # Adapt quality level
        if control_signal > 0.1:  # Too slow, reduce quality
            self._reduce_quality()
        elif control_signal < -0.1:  # Too fast, can increase quality
            self._increase_quality()
            
        self.previous_error = error
        
    def _reduce_quality(self) -> None:
        """
Reduce synthesis quality to improve speed."""
        if self.current_quality_idx > 0:
            self.current_quality_idx -= 1
            quality = self.quality_levels[self.current_quality_idx]
            logger.info(f"Reducing quality to: {quality}")
            
    def _increase_quality(self) -> None:
        """Increase synthesis quality."""
        if self.current_quality_idx < len(self.quality_levels) - 1:
            self.current_quality_idx += 1
            quality = self.quality_levels[self.current_quality_idx]
            logger.info(f"Increasing quality to: {quality}")
            
    def get_current_quality(self) -> str:
        """Get current quality level."""
        return self.quality_levels[self.current_quality_idx]
        
    def get_adaptation_params(self) -> Dict[str, Any]:
        """
Get current adaptation parameters."""
        return {
            'quality_level': self.get_current_quality(),
            'target_latency': self.target_latency,
            'current_latency': self.current_latency,
            'average_latency': np.mean(list(self.latency_history)) if self.latency_history else 0.0,
            'control_signal': (self.kp * self.previous_error + 
                             self.ki * self.integral_error)
        }


class QualityOptimizer:
    """
Quality optimization based on performance metrics."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.current_quality = config.quality_level
        
        # Quality profiles
        self.quality_profiles = {
            'fast': {
                'model_precision': 'fp16',
                'batch_size': 1,
                'num_layers': 'minimal',
                'sampling_rate': 16000
            },
            'balanced': {
                'model_precision': 'fp32',
                'batch_size': 2,
                'num_layers': 'medium',
                'sampling_rate': 22050
            },
            'high': {
                'model_precision': 'fp32',
                'batch_size': 4,
                'num_layers': 'full',
                'sampling_rate': 44100
            }
        }
        
    def adjust_quality(self, processing_time: float) -> None:
        """
Adjust quality based on processing time."""
        target_time = self.config.buffer_size / self.config.sample_rate
        
        if processing_time > target_time * 1.5:  # Too slow
            if self.current_quality == 'high':
                self.current_quality = 'balanced'
            elif self.current_quality == 'balanced':
                self.current_quality = 'fast'
        elif processing_time < target_time * 0.5:  # Too fast, can increase
            if self.current_quality == 'fast':
                self.current_quality = 'balanced'
            elif self.current_quality == 'balanced':
                self.current_quality = 'high'
                
    def get_quality_params(self) -> Dict[str, Any]:
        """
Get current quality parameters."""
        return self.quality_profiles[self.current_quality]


class LatencyMonitor:
    """
Monitor and track latency metrics."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.latencies = deque(maxlen=1000)
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start(self) -> None:
        """
Start latency monitoring."""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop(self) -> None:
        """
Stop latency monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def update_latency(self, latency: float) -> None:
        """
Update latency measurement."""
        self.latencies.append(latency)
        
        # Alert on high latency
        if latency > self.config.alert_threshold:
            logger.warning(f"High latency detected: {latency:.3f}s")
            
    def get_current_latency(self) -> float:
        """Get current latency."""
        return self.latencies[-1] if self.latencies else 0.0
        
    def get_latency_stats(self) -> Dict[str, float]:
        """
Get latency statistics."""
        if not self.latencies:
            return {'mean': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}
            
        latencies_array = np.array(list(self.latencies))
        return {
            'mean': np.mean(latencies_array),
            'std': np.std(latencies_array),
            'min': np.min(latencies_array),
            'max': np.max(latencies_array),
            'p95': np.percentile(latencies_array, 95),
            'p99': np.percentile(latencies_array, 99)
        }
        
    def _monitoring_loop(self) -> None:
        """
Background monitoring loop."""
        while self.is_monitoring:
            if self.config.log_performance and len(self.latencies) % 100 == 0:
                stats = self.get_latency_stats()
                logger.info(f"Latency stats: {stats}")
                
            time.sleep(1.0)


class ResourceManager:
    """Monitor and manage system resources."""
    
    def __init__(self, config: RealtimeConfig):
        self.config = config
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Resource history
        self.cpu_usage = deque(maxlen=100)
        self.memory_usage = deque(maxlen=100)
        self.gpu_memory_usage = deque(maxlen=100)
        
    def start(self) -> None:
        """
Start resource monitoring."""
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._resource_loop,
            daemon=True
        )
        self.monitor_thread.start()
        
    def stop(self) -> None:
        """
Stop resource monitoring."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
            
    def get_cpu_usage(self) -> float:
        """
Get current CPU usage."""
        return self.cpu_usage[-1] if self.cpu_usage else 0.0
        
    def get_memory_usage(self) -> float:
        """
Get current memory usage."""
        return self.memory_usage[-1] if self.memory_usage else 0.0
        
    def get_gpu_memory_usage(self) -> float:
        """
Get current GPU memory usage."""
        return self.gpu_memory_usage[-1] if self.gpu_memory_usage else 0.0
        
    def _resource_loop(self) -> None:
        """
Background resource monitoring loop."""
        while self.is_monitoring:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=None)
                self.cpu_usage.append(cpu_percent)
                
                # Memory usage
                memory_info = psutil.virtual_memory()
                self.memory_usage.append(memory_info.percent)
                
                # GPU memory usage (if available)
                if torch.cuda.is_available():
                    gpu_memory = torch.cuda.memory_allocated() / torch.cuda.max_memory_allocated()
                    self.gpu_memory_usage.append(gpu_memory * 100)
                else:
                    self.gpu_memory_usage.append(0.0)
                    
                # Garbage collection if memory is high
                if memory_info.percent > 85:
                    gc.collect()
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                time.sleep(1.0)


# Factory functions
def create_realtime_engine(config: RealtimeConfig = None) -> RealtimeSynthesisEngine:
    """Create real-time synthesis engine with default configuration."""
    if config is None:
        config = RealtimeConfig()
    return RealtimeSynthesisEngine(config)


def create_streaming_synthesizer(model: nn.Module, 
                                config: RealtimeConfig = None) -> StreamingSynthesizer:
    """
Create streaming synthesizer with model."""
    if config is None:
        config = RealtimeConfig()
    return StreamingSynthesizer(config, model)
