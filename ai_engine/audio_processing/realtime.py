"""🔴 Real-time Audio Processing - Live Audio Engine

High-performance real-time audio processing system for live streaming and interactive applications.
Optimized for low-latency processing with advanced buffering and threading.

Created by: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from pathlib import Path
import numpy as np
import queue
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import psutil
import multiprocessing

# Audio I/O libraries
try:
    import sounddevice as sd
    import pyaudio
    AUDIO_IO_AVAILABLE = True
except (ImportError, OSError):
    AUDIO_IO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Audio I/O libraries not available. Real-time processing will be limited.")
    # Create dummy classes for when audio libraries are not available
    sd = None
    pyaudio = None

from .core import AudioProcessor
from .effects import EffectsProcessor
from .pipeline import AudioProcessingPipeline, PipelineConfig, ProcessingMode
from .config import AudioProcessingConfig

logger = logging.getLogger(__name__)


class AudioBackend(Enum):
    """Available audio backends"""

    SOUNDDEVICE = "sounddevice"
    PYAUDIO = "pyaudio"
    ALSA = "alsa"
    WASAPI = "wasapi"
    COREAUDIO = "coreaudio"


class ProcessingLatency(Enum):
    """Processing latency targets"""

    ULTRA_LOW = "ultra_low"    # < 5ms
    LOW = "low"                # < 10ms
    MEDIUM = "medium"          # < 20ms
    HIGH = "high"              # < 50ms
    RELAXED = "relaxed"        # < 100ms


class BufferMode(Enum):
    """Audio buffer management modes"""

    SINGLE = "single"          # Single buffer
    DOUBLE = "double"          # Double buffering
    RING = "ring"              # Ring buffer
    ADAPTIVE = "adaptive"      # Adaptive buffering


@dataclass
class AudioDeviceInfo:
    """Audio device information"""
    id: int
    name: str
    channels: int
    sample_rate: int
    latency: float
    backend: AudioBackend
    is_input: bool
    is_output: bool
    is_default: bool


@dataclass
class RealTimeConfig:
    """
Real-time processing configuration"""
    sample_rate: int = 44100
    channels: int = 2
    buffer_size: int = 512
    latency_target: ProcessingLatency = ProcessingLatency.LOW
    buffer_mode: BufferMode = BufferMode.DOUBLE
    audio_backend: AudioBackend = AudioBackend.SOUNDDEVICE
    input_device: Optional[int] = None
    output_device: Optional[int] = None
    enable_monitoring: bool = True
    enable_auto_gain: bool = True
    enable_limiter: bool = True
    processing_threads: int = 1
    max_latency_ms: float = 20.0
    dropout_threshold: float = 0.01
    
    def __post_init__(self):
        # Adjust buffer size based on latency target
        latency_buffer_map = {
            ProcessingLatency.ULTRA_LOW: 128,
            ProcessingLatency.LOW: 256,
            ProcessingLatency.MEDIUM: 512,
            ProcessingLatency.HIGH: 1024,
            ProcessingLatency.RELAXED: 2048
        }
        
        if self.buffer_size == 512:  # Default value
            self.buffer_size = latency_buffer_map.get(self.latency_target, 512)


@dataclass
class PerformanceMetrics:
    """
Real-time performance metrics"""
    current_latency_ms: float = 0.0
    average_latency_ms: float = 0.0
    peak_latency_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    buffer_underruns: int = 0
    buffer_overruns: int = 0
    dropouts: int = 0
    processing_load: float = 0.0
    uptime_seconds: float = 0.0
    processed_samples: int = 0


class AudioBuffer:
    """
    🔄 High-performance audio buffer
    
    Thread-safe circular buffer optimized for real-time audio:
    - Lock-free operations where possible
    - Configurable buffer modes
    - Automatic overflow/underflow handling
    - Performance monitoring
    """
    
    def __init__(self, 
                 size: int, 
                 channels: int,
                 mode: BufferMode = BufferMode.RING):
        self.size = size
        self.channels = channels
        self.mode = mode
        
        # Initialize buffers
        if mode == BufferMode.RING:
            self.buffer = np.zeros((channels, size), dtype=np.float32)
            self.write_pos = 0
            self.read_pos = 0
            self.available_samples = 0
        elif mode == BufferMode.DOUBLE:
            self.buffers = [
                np.zeros((channels, size), dtype=np.float32),
                np.zeros((channels, size), dtype=np.float32)
            ]
            self.current_buffer = 0
            self.buffer_ready = [False, False]
        else:
            self.buffer = np.zeros((channels, size), dtype=np.float32)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Performance tracking
        self.overruns = 0
        self.underruns = 0
        
        logger.debug(f"AudioBuffer initialized: {mode.value}, size={size}, channels={channels}")
    
    def write(self, data: np.ndarray) -> bool:
        """Write audio data to buffer"""
        try:
            with self.lock:
                if self.mode == BufferMode.RING:
                    return self._write_ring(data)
                elif self.mode == BufferMode.DOUBLE:
                    return self._write_double(data)
                else:
                    return self._write_single(data)
                    
        except Exception as e:
            logger.error(f"Buffer write failed: {e}")
            return False
    
    def read(self, num_samples: int) -> Optional[np.ndarray]:
        """Read audio data from buffer"""
        try:
            with self.lock:
                if self.mode == BufferMode.RING:
                    return self._read_ring(num_samples)
                elif self.mode == BufferMode.DOUBLE:
                    return self._read_double(num_samples)
                else:
                    return self._read_single(num_samples)
                    
        except Exception as e:
            logger.error(f"Buffer read failed: {e}")
            return None
    
    def _write_ring(self, data: np.ndarray) -> bool:
        """Write to ring buffer"""
        samples_to_write = data.shape[1] if data.ndim > 1 else len(data)
        
        # Check for overflow
        if self.available_samples + samples_to_write > self.size:
            self.overruns += 1
            return False
        
        # Write data
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        for i in range(samples_to_write):
            self.buffer[:, self.write_pos] = data[:, i]
            self.write_pos = (self.write_pos + 1) % self.size
        
        self.available_samples += samples_to_write
        return True
    
    def _read_ring(self, num_samples: int) -> Optional[np.ndarray]:
        """
Read from ring buffer"""
        if self.available_samples < num_samples:
            self.underruns += 1
            return None
        
        # Read data
        output = np.zeros((self.channels, num_samples), dtype=np.float32)
        
        for i in range(num_samples):
            output[:, i] = self.buffer[:, self.read_pos]
            self.read_pos = (self.read_pos + 1) % self.size
        
        self.available_samples -= num_samples
        return output
    
    def _write_double(self, data: np.ndarray) -> bool:
        """
Write to double buffer"""
        current_buf = self.current_buffer
        
        if self.buffer_ready[current_buf]:
            # Buffer is full, try to switch
            next_buf = 1 - current_buf
            if not self.buffer_ready[next_buf]:
                self.current_buffer = next_buf
                current_buf = next_buf
            else:
                self.overruns += 1
                return False
        
        # Write to current buffer
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        samples_to_write = min(data.shape[1], self.size)
        self.buffers[current_buf][:, :samples_to_write] = data[:, :samples_to_write]
        self.buffer_ready[current_buf] = True
        
        return True
    
    def _read_double(self, num_samples: int) -> Optional[np.ndarray]:
        """
Read from double buffer"""
        read_buf = 1 - self.current_buffer
        
        if not self.buffer_ready[read_buf]:
            self.underruns += 1
            return None
        
        # Read from buffer
        samples_to_read = min(num_samples, self.size)
        output = self.buffers[read_buf][:, :samples_to_read].copy()
        self.buffer_ready[read_buf] = False
        
        return output
    
    def _write_single(self, data: np.ndarray) -> bool:
        """
Write to single buffer"""
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        samples_to_write = min(data.shape[1], self.size)
        self.buffer[:, :samples_to_write] = data[:, :samples_to_write]
        return True
    
    def _read_single(self, num_samples: int) -> Optional[np.ndarray]:
        """
Read from single buffer"""
        samples_to_read = min(num_samples, self.size)
        return self.buffer[:, :samples_to_read].copy()
    
    def available_space(self) -> int:
        """
Get available space in buffer"""
        with self.lock:
            if self.mode == BufferMode.RING:
                return self.size - self.available_samples
            elif self.mode == BufferMode.DOUBLE:
                return self.size if not self.buffer_ready[self.current_buffer] else 0
            else:
                return self.size
    
    def available_data(self) -> int:
        """
Get available data in buffer"""
        with self.lock:
            if self.mode == BufferMode.RING:
                return self.available_samples
            elif self.mode == BufferMode.DOUBLE:
                read_buf = 1 - self.current_buffer
                return self.size if self.buffer_ready[read_buf] else 0
            else:
                return self.size
    
    def clear(self):
        """
Clear buffer contents"""
        with self.lock:
            if self.mode == BufferMode.RING:
                self.buffer.fill(0)
                self.write_pos = 0
                self.read_pos = 0
                self.available_samples = 0
            elif self.mode == BufferMode.DOUBLE:
                for buf in self.buffers:
                    buf.fill(0)
                self.buffer_ready = [False, False]
            else:
                self.buffer.fill(0)


class RealTimeProcessor(ABC):
    """
Abstract base class for real-time audio processors"""
    
    @abstractmethod
    async def process(self, 
                     input_buffer: np.ndarray, 
                     output_buffer: np.ndarray) -> bool:
        """
Process audio in real-time"""
        pass
    
    @abstractmethod
    def get_latency_samples(self) -> int:
        """
Get processing latency in samples"""
        pass


class EffectsRealTimeProcessor(RealTimeProcessor):
    """
Real-time effects processor"""
    
    def __init__(self, 
                 effects_processor: EffectsProcessor,
                 effect_chain: List[str] = None):
        self.effects_processor = effects_processor
        self.effect_chain = effect_chain or ['normalize']
        self.latency_samples = 0
        
    async def process(self, 
                     input_buffer: np.ndarray, 
                     output_buffer: np.ndarray) -> bool:
        """
Apply effects to audio buffer"""
        try:
            # Start with input buffer
            processed = input_buffer.copy()
            
            # Apply effects in chain
            for effect in self.effect_chain:
                if effect == 'normalize':
                    processed = await self.effects_processor.normalize_audio(processed)
                elif effect == 'noise_gate':
                    processed = await self.effects_processor.apply_noise_gate(
                        processed, threshold=-40.0
                    )
                elif effect == 'compressor':
                    processed = await self.effects_processor.apply_compressor(
                        processed, 44100, threshold=-20.0, ratio=4.0
                    )
                # Add more effects as needed
            
            # Copy to output buffer
            if processed.shape == output_buffer.shape:
                output_buffer[:] = processed
                return True
            else:
                logger.warning(f"Buffer shape mismatch: {processed.shape} vs {output_buffer.shape}")
                return False
                
        except Exception as e:
            logger.error(f"Real-time effects processing failed: {e}")
            # Pass through input on error
            output_buffer[:] = input_buffer
            return False
    
    def get_latency_samples(self) -> int:
        """Get processing latency"""
        return self.latency_samples


class RealTimeAudioEngine:
    """
    🎵 Real-time Audio Processing Engine
    
    High-performance real-time audio processing system:
    - Ultra-low latency processing
    - Multiple audio backend support
    - Adaptive buffering strategies
    - Real-time performance monitoring
    - Thread-safe audio processing
    - Automatic device management
    """
    
    def __init__(self, 
                 config: RealTimeConfig,
                 audio_config: Optional[AudioProcessingConfig] = None):
        self.config = config
        self.audio_config = audio_config or AudioProcessingConfig()
        
        # Initialize components
        self.audio_processor = AudioProcessor(self.audio_config)
        self.effects_processor = EffectsProcessor(self.audio_config)
        
        # Audio I/O
        self.input_stream = None
        self.output_stream = None
        self.audio_backend = None
        
        # Buffers
        self.input_buffer = AudioBuffer(
            config.buffer_size * 4,  # Larger buffer for input
            config.channels,
            config.buffer_mode
        )
        self.output_buffer = AudioBuffer(
            config.buffer_size * 4,  # Larger buffer for output
            config.channels,
            config.buffer_mode
        )
        
        # Processing
        self.processors: List[RealTimeProcessor] = []
        self.processing_thread = None
        self.is_running = False
        
        # Performance monitoring
        self.metrics = PerformanceMetrics()
        self.performance_monitor = None
        
        # Thread synchronization
        self.process_event = threading.Event()
        self.stop_event = threading.Event()
        
        logger.info(f"RealTimeAudioEngine initialized with {config.latency_target.value} latency")
    
    async def initialize(self) -> bool:
        """Initialize the real-time audio engine"""
        try:
            logger.info("Initializing real-time audio engine...")
            
            # Check audio I/O availability
            if not AUDIO_IO_AVAILABLE:
                logger.error("Audio I/O libraries not available")
                return False
            
            # Initialize audio backend
            success = await self._initialize_audio_backend()
            if not success:
                return False
            
            # Setup default processors
            await self._setup_default_processors()
            
            # Start performance monitoring
            if self.config.enable_monitoring:
                self._start_performance_monitoring()
            
            logger.info("Real-time audio engine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize real-time audio engine: {e}")
            return False
    
    async def _initialize_audio_backend(self) -> bool:
        """Initialize the audio backend"""
        try:
            if self.config.audio_backend == AudioBackend.SOUNDDEVICE:
                return await self._initialize_sounddevice()
            elif self.config.audio_backend == AudioBackend.PYAUDIO:
                return await self._initialize_pyaudio()
            else:
                logger.error(f"Unsupported audio backend: {self.config.audio_backend}")
                return False
                
        except Exception as e:
            logger.error(f"Audio backend initialization failed: {e}")
            return False
    
    async def _initialize_sounddevice(self) -> bool:
        """Initialize SoundDevice backend"""
        try:
            import sounddevice as sd
            
            # Set default parameters
            sd.default.samplerate = self.config.sample_rate
            sd.default.channels = self.config.channels
            sd.default.latency = 'low'
            
            # Set devices if specified
            if self.config.input_device is not None:
                sd.default.device[0] = self.config.input_device
            if self.config.output_device is not None:
                sd.default.device[1] = self.config.output_device
            
            # Test audio setup
            try:
                test_data = np.zeros((self.config.buffer_size, self.config.channels))
                sd.playrec(test_data, 
                          samplerate=self.config.sample_rate,
                          channels=self.config.channels,
                          blocking=True)
                logger.info("SoundDevice backend initialized successfully")
                return True
                
            except Exception as e:
                logger.error(f"SoundDevice test failed: {e}")
                return False
                
        except ImportError:
            logger.error("SoundDevice not available")
            return False
    
    async def _initialize_pyaudio(self) -> bool:
        """Initialize PyAudio backend"""
        try:
            import pyaudio
            
            self.audio_backend = pyaudio.PyAudio()
            
            # Get device information
            if self.config.input_device is None:
                self.config.input_device = self.audio_backend.get_default_input_device_info()['index']
            if self.config.output_device is None:
                self.config.output_device = self.audio_backend.get_default_output_device_info()['index']
            
            logger.info("PyAudio backend initialized successfully")
            return True
            
        except ImportError:
            logger.error("PyAudio not available")
            return False
    
    async def _setup_default_processors(self):
        """Setup default audio processors"""
        # Add effects processor
        effects_chain = []
        
        if self.config.enable_auto_gain:
            effects_chain.append('normalize')
        
        if self.config.enable_limiter:
            effects_chain.append('compressor')
        
        if effects_chain:
            effects_processor = EffectsRealTimeProcessor(
                self.effects_processor, 
                effects_chain
            )
            self.add_processor(effects_processor)
    
    def add_processor(self, processor: RealTimeProcessor):
        """
Add a real-time processor to the chain"""
        self.processors.append(processor)
        logger.debug(f"Added processor: {type(processor).__name__}")
    
    def remove_processor(self, processor: RealTimeProcessor):
        """Remove a processor from the chain"""
        if processor in self.processors:
            self.processors.remove(processor)
            logger.debug(f"Removed processor: {type(processor).__name__}")
    
    async def start(self) -> bool:
        """Start real-time audio processing"""
        try:
            if self.is_running:
                logger.warning("Real-time engine already running")
                return True
            
            logger.info("Starting real-time audio processing...")
            
            # Clear buffers
            self.input_buffer.clear()
            self.output_buffer.clear()
            
            # Reset metrics
            self.metrics = PerformanceMetrics()
            self.metrics.uptime_seconds = time.time()
            
            # Start audio streams
            success = await self._start_audio_streams()
            if not success:
                return False
            
            # Start processing thread
            self.is_running = True
            self.stop_event.clear()
            self.processing_thread = threading.Thread(
                target=self._processing_loop,
                name="AudioProcessingThread"
            )
            self.processing_thread.start()
            
            logger.info("Real-time audio processing started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start real-time processing: {e}")
            await self.stop()
            return False
    
    async def _start_audio_streams(self) -> bool:
        """Start audio input/output streams"""
        try:
            if self.config.audio_backend == AudioBackend.SOUNDDEVICE:
                return await self._start_sounddevice_streams()
            elif self.config.audio_backend == AudioBackend.PYAUDIO:
                return await self._start_pyaudio_streams()
            else:
                logger.error(f"Unsupported audio backend: {self.config.audio_backend}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start audio streams: {e}")
            return False
    
    async def _start_sounddevice_streams(self) -> bool:
        """Start SoundDevice streams"""
        try:
            import sounddevice as sd
            
            def audio_callback(indata, outdata, frames, time, status):
                """
Audio callback for SoundDevice"""
                if status:
                    logger.warning(f"Audio callback status: {status}")
                
                try:
                    # Convert input to our format
                    input_audio = indata.T.astype(np.float32)
                    
                    # Write to input buffer
                    self.input_buffer.write(input_audio)
                    
                    # Read from output buffer
                    output_audio = self.output_buffer.read(frames)
                    
                    if output_audio is not None:
                        outdata[:] = output_audio.T
                    else:
                        # No data available - output silence
                        outdata.fill(0)
                        self.metrics.buffer_underruns += 1
                    
                    # Signal processing thread
                    self.process_event.set()
                    
                except Exception as e:
                    logger.error(f"Audio callback error: {e}")
                    outdata.fill(0)
            
            # Create duplex stream
            self.input_stream = sd.Stream(
                callback=audio_callback,
                samplerate=self.config.sample_rate,
                channels=self.config.channels,
                blocksize=self.config.buffer_size,
                latency='low'
            )
            
            self.input_stream.start()
            logger.info("SoundDevice streams started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start SoundDevice streams: {e}")
            return False
    
    async def _start_pyaudio_streams(self) -> bool:
        """Start PyAudio streams"""
        try:
            import pyaudio
            
            def input_callback(in_data, frame_count, time_info, status):
                """
Input stream callback"""
                try:
                    # Convert bytes to numpy array
                    audio_data = np.frombuffer(in_data, dtype=np.float32)
                    audio_data = audio_data.reshape(-1, self.config.channels).T
                    
                    # Write to input buffer
                    self.input_buffer.write(audio_data)
                    
                    # Signal processing thread
                    self.process_event.set()
                    
                    return (None, pyaudio.paContinue)
                    
                except Exception as e:
                    logger.error(f"Input callback error: {e}")
                    return (None, pyaudio.paAbort)
            
            def output_callback(in_data, frame_count, time_info, status):
                """Output stream callback"""
                try:
                    # Read from output buffer
                    output_audio = self.output_buffer.read(frame_count)
                    
                    if output_audio is not None:
                        # Convert to bytes
                        output_bytes = output_audio.T.astype(np.float32).tobytes()
                        return (output_bytes, pyaudio.paContinue)
                    else:
                        # No data available - output silence
                        silence = np.zeros((frame_count, self.config.channels), dtype=np.float32)
                        self.metrics.buffer_underruns += 1
                        return (silence.tobytes(), pyaudio.paContinue)
                        
                except Exception as e:
                    logger.error(f"Output callback error: {e}")
                    return (None, pyaudio.paAbort)
            
            # Create input stream
            self.input_stream = self.audio_backend.open(
                format=pyaudio.paFloat32,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                input=True,
                input_device_index=self.config.input_device,
                frames_per_buffer=self.config.buffer_size,
                stream_callback=input_callback
            )
            
            # Create output stream
            self.output_stream = self.audio_backend.open(
                format=pyaudio.paFloat32,
                channels=self.config.channels,
                rate=self.config.sample_rate,
                output=True,
                output_device_index=self.config.output_device,
                frames_per_buffer=self.config.buffer_size,
                stream_callback=output_callback
            )
            
            # Start streams
            self.input_stream.start_stream()
            self.output_stream.start_stream()
            
            logger.info("PyAudio streams started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start PyAudio streams: {e}")
            return False
    
    def _processing_loop(self):
        """Main audio processing loop"""
        logger.info("Audio processing loop started")
        
        try:
            while self.is_running and not self.stop_event.is_set():
                # Wait for audio data
                if self.process_event.wait(timeout=0.1):
                    self.process_event.clear()
                    
                    # Process audio
                    self._process_audio_block()
                    
                    # Update metrics
                    self._update_processing_metrics()
        
        except Exception as e:
            logger.error(f"Processing loop error: {e}")
        
        finally:
            logger.info("Audio processing loop stopped")
    
    def _process_audio_block(self):
        """Process a block of audio"""
        try:
            start_time = time.time()
            
            # Check if we have enough input data
            available_input = self.input_buffer.available_data()
            if available_input < self.config.buffer_size:
                return
            
            # Read input data
            input_data = self.input_buffer.read(self.config.buffer_size)
            if input_data is None:
                return
            
            # Prepare output buffer
            output_data = np.zeros_like(input_data)
            
            # Apply processors in chain
            current_input = input_data
            for processor in self.processors:
                success = asyncio.run(processor.process(current_input, output_data))
                if success:
                    current_input = output_data.copy()
                else:
                    # Processor failed - use previous output
                    break
            
            # Write to output buffer
            success = self.output_buffer.write(output_data)
            if not success:
                self.metrics.buffer_overruns += 1
            
            # Update latency
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            self.metrics.current_latency_ms = processing_time
            
            # Update processed samples count
            self.metrics.processed_samples += self.config.buffer_size
            
        except Exception as e:
            logger.error(f"Audio block processing failed: {e}")
    
    def _update_processing_metrics(self):
        """Update performance metrics"""
        try:
            current_time = time.time()
            
            # Update average latency
            if self.metrics.average_latency_ms == 0:
                self.metrics.average_latency_ms = self.metrics.current_latency_ms
            else:
                alpha = 0.1  # Exponential moving average factor
                self.metrics.average_latency_ms = (
                    alpha * self.metrics.current_latency_ms +
                    (1 - alpha) * self.metrics.average_latency_ms
                )
            
            # Update peak latency
            if self.metrics.current_latency_ms > self.metrics.peak_latency_ms:
                self.metrics.peak_latency_ms = self.metrics.current_latency_ms
            
            # Calculate processing load
            buffer_time_ms = (self.config.buffer_size / self.config.sample_rate) * 1000
            self.metrics.processing_load = self.metrics.current_latency_ms / buffer_time_ms
            
            # Check for dropouts
            if self.metrics.current_latency_ms > self.config.max_latency_ms:
                self.metrics.dropouts += 1
            
            # Update uptime
            if hasattr(self.metrics, 'start_time'):
                self.metrics.uptime_seconds = current_time - self.metrics.start_time
            
        except Exception as e:
            logger.error(f"Metrics update failed: {e}")
    
    def _start_performance_monitoring(self):
        """Start performance monitoring thread"""
        def monitor_performance():
            while self.is_running:
                try:
                    # Get CPU usage
                    self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=0.1)
                    
                    # Get memory usage
                    process = psutil.Process()
                    memory_info = process.memory_info()
                    self.metrics.memory_usage_mb = memory_info.rss / 1024 / 1024
                    
                    time.sleep(1.0)  # Update every second
                    
                except Exception as e:
                    logger.error(f"Performance monitoring error: {e}")
                    time.sleep(1.0)
        
        self.performance_monitor = threading.Thread(
            target=monitor_performance,
            name="PerformanceMonitor",
            daemon=True
        )
        self.performance_monitor.start()
    
    async def stop(self):
        """Stop real-time audio processing"""
        try:
            logger.info("Stopping real-time audio processing...")
            
            # Signal stop
            self.is_running = False
            self.stop_event.set()
            
            # Wait for processing thread
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)
            
            # Stop audio streams
            await self._stop_audio_streams()
            
            # Clean up audio backend
            if self.audio_backend:
                if hasattr(self.audio_backend, 'terminate'):
                    self.audio_backend.terminate()
            
            logger.info("Real-time audio processing stopped")
            
        except Exception as e:
            logger.error(f"Failed to stop real-time processing: {e}")
    
    async def _stop_audio_streams(self):
        """Stop audio streams"""
        try:
            if self.input_stream:
                if hasattr(self.input_stream, 'stop'):
                    self.input_stream.stop()
                if hasattr(self.input_stream, 'close'):
                    self.input_stream.close()
            
            if self.output_stream:
                if hasattr(self.output_stream, 'stop_stream'):
                    self.output_stream.stop_stream()
                if hasattr(self.output_stream, 'close'):
                    self.output_stream.close()
                    
        except Exception as e:
            logger.error(f"Failed to stop audio streams: {e}")
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics
    
    def get_device_list(self) -> List[AudioDeviceInfo]:
        """
Get list of available audio devices"""
        devices = []
        
        try:
            if self.config.audio_backend == AudioBackend.SOUNDDEVICE:
                import sounddevice as sd
                
                device_list = sd.query_devices()
                for i, device in enumerate(device_list):
                    devices.append(AudioDeviceInfo(
                        id=i,
                        name=device['name'],
                        channels=device['max_input_channels'] if device['max_input_channels'] > 0 else device['max_output_channels'],
                        sample_rate=int(device['default_samplerate']),
                        latency=device['default_low_input_latency'] if device['max_input_channels'] > 0 else device['default_low_output_latency'],
                        backend=AudioBackend.SOUNDDEVICE,
                        is_input=device['max_input_channels'] > 0,
                        is_output=device['max_output_channels'] > 0,
                        is_default=(i == sd.default.device[0] or i == sd.default.device[1])
                    ))
            
            elif self.config.audio_backend == AudioBackend.PYAUDIO and self.audio_backend:
                for i in range(self.audio_backend.get_device_count()):
                    device = self.audio_backend.get_device_info_by_index(i)
                    devices.append(AudioDeviceInfo(
                        id=i,
                        name=device['name'],
                        channels=max(device['maxInputChannels'], device['maxOutputChannels']),
                        sample_rate=int(device['defaultSampleRate']),
                        latency=device['defaultLowInputLatency'] if device['maxInputChannels'] > 0 else device['defaultLowOutputLatency'],
                        backend=AudioBackend.PYAUDIO,
                        is_input=device['maxInputChannels'] > 0,
                        is_output=device['maxOutputChannels'] > 0,
                        is_default=(i == self.audio_backend.get_default_input_device_info()['index'] or 
                                  i == self.audio_backend.get_default_output_device_info()['index'])
                    ))
            
        except Exception as e:
            logger.error(f"Failed to get device list: {e}")
        
        return devices
    
    def is_running_status(self) -> bool:
        """Check if engine is running"""
        return self.is_running
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """
Get buffer status information"""
        return {
            'input_buffer': {
                'available_data': self.input_buffer.available_data(),
                'available_space': self.input_buffer.available_space(),
                'overruns': self.input_buffer.overruns,
                'underruns': self.input_buffer.underruns
            },
            'output_buffer': {
                'available_data': self.output_buffer.available_data(),
                'available_space': self.output_buffer.available_space(),
                'overruns': self.output_buffer.overruns,
                'underruns': self.output_buffer.underruns
            }
        }


# Factory functions for common configurations
def create_streaming_engine(sample_rate: int = 44100, 
                          channels: int = 2) -> RealTimeAudioEngine:
    """
Create engine optimized for live streaming"""
    config = RealTimeConfig(
        sample_rate=sample_rate,
        channels=channels,
        latency_target=ProcessingLatency.LOW,
        buffer_mode=BufferMode.DOUBLE,
        enable_auto_gain=True,
        enable_limiter=True,
        enable_monitoring=True
    )
    
    return RealTimeAudioEngine(config)


def create_gaming_engine(sample_rate: int = 48000, 
                        channels: int = 2) -> RealTimeAudioEngine:
    """
Create engine optimized for gaming/interactive applications"""
    config = RealTimeConfig(
        sample_rate=sample_rate,
        channels=channels,
        latency_target=ProcessingLatency.ULTRA_LOW,
        buffer_mode=BufferMode.RING,
        enable_auto_gain=False,
        enable_limiter=True,
        enable_monitoring=True
    )
    
    return RealTimeAudioEngine(config)


def create_podcast_engine(sample_rate: int = 44100, 
                         channels: int = 1) -> RealTimeAudioEngine:
    """
Create engine optimized for podcast recording"""
    config = RealTimeConfig(
        sample_rate=sample_rate,
        channels=channels,
        latency_target=ProcessingLatency.MEDIUM,
        buffer_mode=BufferMode.DOUBLE,
        enable_auto_gain=True,
        enable_limiter=True,
        enable_monitoring=False
    )
    
    return RealTimeAudioEngine(config)
