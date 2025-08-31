"""
Advanced Real-Time Processing Models for IA Influencer Agent Platform
Enterprise-grade real-time content processing and streaming models

Copyright (c) 2025 Fahed Mlaiel <mlaiel@live.de>
  STRICT WARNING: Unauthorized use, copying, or stealing of this concept, 
    code, or intellectual property without explicit written authorization 
    from Fahed Mlaiel is strictly prohibited and will result in legal action.

Lead Developer: Fahed Mlaiel
Development Team Specialties:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Security
- Microservices + Audio + DevOps + IA Prompt Engineer
Email: mlaiel@live.de
"""

import asyncio
import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import time
from collections import deque
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import websocket
import cv2
import librosa

from ..core.base_models import BaseAIModel, ModelConfig, ProcessingResult
from ..core.exceptions import ModelError, ValidationError


class StreamingMode(Enum):
    """Real-time streaming modes"""
    LIVE = "live"
    BUFFERED = "buffered"
    BATCH = "batch"
    PIPELINE = "pipeline"
    HYBRID = "hybrid"


class ProcessingLatency(Enum):
    """Processing latency requirements"""
    ULTRA_LOW = "ultra_low"  # < 10ms
    LOW = "low"              # < 50ms  
    MEDIUM = "medium"        # < 200ms
    HIGH = "high"            # < 1000ms
    BATCH = "batch"          # No real-time requirement


@dataclass
class StreamingConfig:
    """Configuration for real-time streaming models"""
    mode: StreamingMode
    latency_requirement: ProcessingLatency
    buffer_size: int = 1024
    batch_size: int = 32
    max_concurrent_streams: int = 100
    enable_gpu_acceleration: bool = True
    enable_tensorrt: bool = False
    enable_quantization: bool = False
    quality_vs_speed: float = 0.5  # 0.0 = speed, 1.0 = quality
    adaptive_quality: bool = True
    stream_compression: bool = True
    checkpoint_interval: int = 1000
    error_recovery: bool = True


@dataclass
class StreamMetrics:
    """Real-time streaming performance metrics"""
    current_fps: float
    avg_fps: float
    latency_ms: float
    buffer_utilization: float
    gpu_utilization: float
    memory_usage_mb: float
    dropped_frames: int
    processed_frames: int
    error_count: int
    throughput_mbps: float
    quality_score: float


class RealTimeAudioProcessor(BaseAIModel):
    """
    Real-time audio processing engine with ultra-low latency
    Supports live audio streaming, analysis, and enhancement
    """
    
    def __init__(self, config: ModelConfig, streaming_config: StreamingConfig):
        super().__init__(config)
        self.streaming_config = streaming_config
        self.audio_buffer = deque(maxlen=streaming_config.buffer_size)
        self.processing_queue = queue.Queue(maxsize=streaming_config.buffer_size)
        self.result_queue = queue.Queue()
        self.is_streaming = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Audio processing models
        self.feature_extractor = self._initialize_feature_extractor()
        self.enhancer = self._initialize_enhancer()
        self.analyzer = self._initialize_analyzer()
        
        # Performance monitoring
        self.metrics = StreamMetrics(
            current_fps=0.0, avg_fps=0.0, latency_ms=0.0,
            buffer_utilization=0.0, gpu_utilization=0.0,
            memory_usage_mb=0.0, dropped_frames=0,
            processed_frames=0, error_count=0,
            throughput_mbps=0.0, quality_score=0.0
        )
        
    def _initialize_feature_extractor(self) -> torch.nn.Module:
        """Initialize optimized feature extractor for real-time processing"""
        class FastAudioFeatureExtractor(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.conv_layers = torch.nn.Sequential(
                    torch.nn.Conv1d(1, 32, kernel_size=7, stride=2, padding=3),
                    torch.nn.BatchNorm1d(32),
                    torch.nn.ReLU(),
                    torch.nn.Conv1d(32, 64, kernel_size=5, stride=2, padding=2),
                    torch.nn.BatchNorm1d(64),
                    torch.nn.ReLU(),
                    torch.nn.AdaptiveAvgPool1d(128)
                )
                self.feature_projection = torch.nn.Linear(64, 256)
            
            def forward(self, x):
                x = self.conv_layers(x)
                x = x.transpose(1, 2)  # (B, T, C)
                x = self.feature_projection(x)
                return x.mean(dim=1)  # Global average pooling
        
        model = FastAudioFeatureExtractor()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
            
        if self.streaming_config.enable_quantization:
            model = torch.quantization.quantize_dynamic(
                model, {torch.nn.Linear, torch.nn.Conv1d}, dtype=torch.qint8
            )
            
        return model
    
    def _initialize_enhancer(self) -> torch.nn.Module:
        """Initialize real-time audio enhancer"""
        class RealTimeAudioEnhancer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.noise_gate = torch.nn.Sequential(
                    torch.nn.Conv1d(1, 16, kernel_size=3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.Conv1d(16, 1, kernel_size=3, padding=1),
                    torch.nn.Sigmoid()
                )
                
                self.dynamic_compressor = torch.nn.Sequential(
                    torch.nn.Conv1d(1, 32, kernel_size=5, padding=2),
                    torch.nn.ReLU(),
                    torch.nn.Conv1d(32, 1, kernel_size=5, padding=2)
                )
                
            def forward(self, x):
                # Apply noise gating
                gate = self.noise_gate(x)
                x_gated = x * gate
                
                # Apply dynamic compression
                compressed = self.dynamic_compressor(x_gated)
                
                return compressed
                
        model = RealTimeAudioEnhancer()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
        return model
    
    def _initialize_analyzer(self) -> torch.nn.Module:
        """Initialize real-time audio analyzer"""
        class FastAudioAnalyzer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.classifier = torch.nn.Sequential(
                    torch.nn.Linear(256, 128),
                    torch.nn.ReLU(),
                    torch.nn.Dropout(0.1),
                    torch.nn.Linear(128, 64),
                    torch.nn.ReLU(),
                    torch.nn.Linear(64, 32)  # Multiple output classes
                )
                
            def forward(self, x):
                return self.classifier(x)
                
        model = FastAudioAnalyzer()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
        return model
    
    async def start_streaming(
        self, 
        audio_source: Union[str, int, Callable],
        callback: Optional[Callable] = None
    ) -> None:
        """Start real-time audio streaming and processing"""



        try:
            self.is_streaming = True
            self.logger.info("Starting real-time audio streaming")
            
            # Start processing threads
            processing_task = asyncio.create_task(self._processing_loop())
            metrics_task = asyncio.create_task(self._metrics_update_loop())
            
            # Start audio capture
            if isinstance(audio_source, (str, int)):
                await self._capture_from_device(audio_source, callback)
            elif callable(audio_source):
                await self._capture_from_callback(audio_source, callback)
            else:
                raise ValueError("Invalid audio source type")
                
        except Exception as e:
            self.logger.error(f"Streaming start failed: {e}")
            self.is_streaming = False
            raise ModelError(f"Streaming error: {e}")
        finally:
            # Cleanup
            if 'processing_task' in locals():
                processing_task.cancel()
            if 'metrics_task' in locals():
                metrics_task.cancel()
    
    async def _capture_from_device(
        self, 
        device_id: Union[str, int],
        callback: Optional[Callable]
    ) -> None:
        """Capture audio from device (microphone, audio interface)"""



        try:
            import sounddevice as sd
            
            def audio_callback(indata, frames, time, status):
                if status:
                    self.logger.warning(f"Audio callback status: {status}")
                
                # Convert to tensor and add to processing queue
                audio_tensor = torch.from_numpy(indata.T).float()
                
                if not self.processing_queue.full():
                    self.processing_queue.put({
                        "audio": audio_tensor,
                        "timestamp": time.inputBufferAdcTime,
                        "frames": frames
                    })
                else:
                    self.metrics.dropped_frames += 1
            
            # Start audio stream
            with sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=22050,
                callback=audio_callback,
                blocksize=512,
                latency='low'
            ):
                while self.is_streaming:
                    await asyncio.sleep(0.01)  # Small sleep to prevent blocking
                    
        except Exception as e:
            self.logger.error(f"Audio capture failed: {e}")
            raise
    
    async def _capture_from_callback(
        self, 
        audio_callback: Callable,
        result_callback: Optional[Callable]
    ) -> None:
        """Capture audio from custom callback function"""



        try:
            while self.is_streaming:
                try:
                    audio_data = await asyncio.get_event_loop().run_in_executor(
                        self.executor, audio_callback
                    )
                    
                    if audio_data is not None:
                        self.processing_queue.put({
                            "audio": audio_data,
                            "timestamp": time.time(),
                            "frames": len(audio_data)
                        })
                        
                    await asyncio.sleep(0.001)  # Ultra-low latency
                    
                except Exception as e:
                    self.logger.warning(f"Audio callback error: {e}")
                    self.metrics.error_count += 1
                    
        except Exception as e:
            self.logger.error(f"Callback capture failed: {e}")
            raise
    
    async def _processing_loop(self) -> None:
        """Main audio processing loop"""



        try:
            while self.is_streaming:
                try:
                    # Get audio data from queue (non-blocking)
                    try:
                        audio_data = self.processing_queue.get_nowait()
                    except queue.Empty:
                        await asyncio.sleep(0.001)
                        continue
                    
                    start_time = time.time()
                    
                    # Process audio in real-time
                    result = await self._process_audio_chunk(audio_data)
                    
                    processing_time = (time.time() - start_time) * 1000
                    
                    # Update metrics
                    self.metrics.processed_frames += 1
                    self.metrics.latency_ms = processing_time
                    
                    # Put result in output queue
                    if not self.result_queue.full():
                        self.result_queue.put({
                            "result": result,
                            "latency_ms": processing_time,
                            "timestamp": audio_data["timestamp"]
                        })
                    
                    # Adaptive quality control
                    if self.streaming_config.adaptive_quality:
                        await self._adjust_quality_based_on_performance()
                        
                except Exception as e:
                    self.logger.warning(f"Processing loop error: {e}")
                    self.metrics.error_count += 1
                    
        except Exception as e:
            self.logger.error(f"Processing loop failed: {e}")
    
    async def _process_audio_chunk(self, audio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process single audio chunk in real-time"""



        try:
            audio_tensor = audio_data["audio"]
            
            # Ensure correct tensor format
            if len(audio_tensor.shape) == 1:
                audio_tensor = audio_tensor.unsqueeze(0).unsqueeze(0)  # (1, 1, T)
            elif len(audio_tensor.shape) == 2:
                audio_tensor = audio_tensor.unsqueeze(0)  # (1, C, T)
            
            # Move to GPU if available
            if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
                audio_tensor = audio_tensor.cuda()
            
            # Extract features
            with torch.no_grad():
                features = self.feature_extractor(audio_tensor)
                
                # Enhance audio
                enhanced = self.enhancer(audio_tensor)
                
                # Analyze audio
                analysis = self.analyzer(features)
            
            # Convert back to CPU for output
            if torch.cuda.is_available():
                enhanced = enhanced.cpu()
                analysis = analysis.cpu()
                features = features.cpu()
            
            return {
                "enhanced_audio": enhanced.squeeze().numpy(),
                "features": features.squeeze().numpy(),
                "analysis": analysis.squeeze().numpy(),
                "quality_score": self._calculate_quality_score(audio_tensor, enhanced),
                "processing_info": {
                    "latency_target_met": self.metrics.latency_ms < self._get_latency_threshold(),
                    "gpu_used": self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Audio chunk processing failed: {e}")
            raise
    
    def _get_latency_threshold(self) -> float:
        """Get latency threshold based on configuration"""
        thresholds = {
            ProcessingLatency.ULTRA_LOW: 10.0,
            ProcessingLatency.LOW: 50.0,
            ProcessingLatency.MEDIUM: 200.0,
            ProcessingLatency.HIGH: 1000.0,
            ProcessingLatency.BATCH: float('inf')
        }
        return thresholds.get(self.streaming_config.latency_requirement, 200.0)
    
    async def _adjust_quality_based_on_performance(self) -> None:
        """Dynamically adjust processing quality based on performance"""
        if self.metrics.latency_ms > self._get_latency_threshold():
            # Reduce quality to meet latency requirements
            self.streaming_config.quality_vs_speed = max(0.0, self.streaming_config.quality_vs_speed - 0.1)
            self.logger.info(f"Reduced quality to {self.streaming_config.quality_vs_speed}")
        elif self.metrics.latency_ms < self._get_latency_threshold() * 0.5:
            # Increase quality if we have headroom
            self.streaming_config.quality_vs_speed = min(1.0, self.streaming_config.quality_vs_speed + 0.05)
    
    def _calculate_quality_score(self, original: torch.Tensor, enhanced: torch.Tensor) -> float:
        """Calculate audio quality score"""



        try:
            # Simple SNR-based quality metric
            noise = original - enhanced
            signal_power = torch.mean(enhanced ** 2)
            noise_power = torch.mean(noise ** 2)
            
            if noise_power == 0:
                return 1.0
                
            snr = 10 * torch.log10(signal_power / (noise_power + 1e-8))
            quality_score = min(1.0, max(0.0, snr.item() / 30.0))
            
            return quality_score
            
        except:
            return 0.5  # Default quality score
    
    async def _metrics_update_loop(self) -> None:
        """Update performance metrics periodically"""
        frame_times = deque(maxlen=100)
        last_frame_count = 0
        
        try:
            while self.is_streaming:
                current_time = time.time()
                frame_times.append(current_time)
                
                if len(frame_times) > 1:
                    time_diff = frame_times[-1] - frame_times[0]
                    if time_diff > 0:
                        self.metrics.current_fps = len(frame_times) / time_diff
                        
                        # Calculate average FPS
                        total_frames = self.metrics.processed_frames
                        if total_frames > last_frame_count:
                            self.metrics.avg_fps = (total_frames - last_frame_count) / time_diff
                            last_frame_count = total_frames
                
                # Update buffer utilization
                self.metrics.buffer_utilization = self.processing_queue.qsize() / self.streaming_config.buffer_size
                
                # Update GPU utilization (if available)
                if torch.cuda.is_available():
                    self.metrics.gpu_utilization = torch.cuda.utilization()
                    self.metrics.memory_usage_mb = torch.cuda.memory_allocated() / (1024 ** 2)
                
                await asyncio.sleep(1.0)  # Update every second
                
        except Exception as e:
            self.logger.warning(f"Metrics update error: {e}")
    
    async def stop_streaming(self) -> Dict[str, Any]:
        """Stop streaming and return final metrics"""
        self.is_streaming = False
        self.logger.info("Stopping real-time audio streaming")
        
        # Return final performance report
        return {
            "session_metrics": self.metrics,
            "total_processed": self.metrics.processed_frames,
            "total_dropped": self.metrics.dropped_frames,
            "average_latency": self.metrics.latency_ms,
            "average_quality": self.metrics.quality_score,
            "error_rate": self.metrics.error_count / max(1, self.metrics.processed_frames)
        }
    
    async def get_processed_results(self) -> AsyncGenerator[Dict[str, Any], None]:
        """Get processed results as they become available"""
        while self.is_streaming or not self.result_queue.empty():
            try:
                result = self.result_queue.get_nowait()
                yield result
            except queue.Empty:
                await asyncio.sleep(0.001)
                continue


class RealTimeVideoProcessor(BaseAIModel):
    """
    Real-time video processing engine with low-latency streaming
    Supports live video analysis, enhancement, and content protection
    """
    
    def __init__(self, config: ModelConfig, streaming_config: StreamingConfig):
        super().__init__(config)
        self.streaming_config = streaming_config
        self.video_buffer = deque(maxlen=streaming_config.buffer_size)
        self.frame_queue = queue.Queue(maxsize=streaming_config.buffer_size)
        self.result_queue = queue.Queue()
        self.is_streaming = False
        
        # Video processing models
        self.frame_analyzer = self._initialize_frame_analyzer()
        self.enhancer = self._initialize_video_enhancer()
        self.detector = self._initialize_object_detector()
        
        # Performance monitoring
        self.metrics = StreamMetrics(
            current_fps=0.0, avg_fps=0.0, latency_ms=0.0,
            buffer_utilization=0.0, gpu_utilization=0.0,
            memory_usage_mb=0.0, dropped_frames=0,
            processed_frames=0, error_count=0,
            throughput_mbps=0.0, quality_score=0.0
        )
    
    def _initialize_frame_analyzer(self) -> torch.nn.Module:
        """Initialize optimized frame analyzer for real-time processing"""
        class FastFrameAnalyzer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.backbone = torch.nn.Sequential(
                    torch.nn.Conv2d(3, 32, kernel_size=3, stride=2, padding=1),
                    torch.nn.BatchNorm2d(32),
                    torch.nn.ReLU(),
                    torch.nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
                    torch.nn.BatchNorm2d(64),
                    torch.nn.ReLU(),
                    torch.nn.AdaptiveAvgPool2d((8, 8))
                )
                self.classifier = torch.nn.Sequential(
                    torch.nn.Linear(64 * 8 * 8, 256),
                    torch.nn.ReLU(),
                    torch.nn.Linear(256, 128)
                )
                
            def forward(self, x):
                x = self.backbone(x)
                x = x.view(x.size(0), -1)
                x = self.classifier(x)
                return x
        
        model = FastFrameAnalyzer()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
        return model
    
    def _initialize_video_enhancer(self) -> torch.nn.Module:
        """Initialize real-time video enhancer"""
        class RealTimeVideoEnhancer(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.denoise_net = torch.nn.Sequential(
                    torch.nn.Conv2d(3, 32, kernel_size=3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.Conv2d(32, 32, kernel_size=3, padding=1),
                    torch.nn.ReLU(),
                    torch.nn.Conv2d(32, 3, kernel_size=3, padding=1)
                )
                
            def forward(self, x):
                return self.denoise_net(x) + x  # Residual connection
                
        model = RealTimeVideoEnhancer()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
        return model
    
    def _initialize_object_detector(self) -> torch.nn.Module:
        """Initialize fast object detector"""
        class FastObjectDetector(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.feature_extractor = torch.nn.Sequential(
                    torch.nn.Conv2d(3, 64, kernel_size=3, stride=2, padding=1),
                    torch.nn.BatchNorm2d(64),
                    torch.nn.ReLU(),
                    torch.nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
                    torch.nn.BatchNorm2d(128),
                    torch.nn.ReLU(),
                    torch.nn.AdaptiveAvgPool2d((1, 1))
                )
                self.detector_head = torch.nn.Linear(128, 80)  # COCO classes
                
            def forward(self, x):
                features = self.feature_extractor(x)
                features = features.view(features.size(0), -1)
                detections = self.detector_head(features)
                return detections
        
        model = FastObjectDetector()
        if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
            model = model.cuda()
        return model
    
    async def start_video_streaming(
        self, 
        video_source: Union[str, int, cv2.VideoCapture],
        callback: Optional[Callable] = None
    ) -> None:
        """Start real-time video streaming and processing"""



        try:
            self.is_streaming = True
            self.logger.info("Starting real-time video streaming")
            
            # Start processing and metrics tasks
            processing_task = asyncio.create_task(self._video_processing_loop())
            metrics_task = asyncio.create_task(self._video_metrics_loop())
            
            # Start video capture
            await self._capture_video_frames(video_source, callback)
            
        except Exception as e:
            self.logger.error(f"Video streaming start failed: {e}")
            self.is_streaming = False
            raise ModelError(f"Video streaming error: {e}")
        finally:
            if 'processing_task' in locals():
                processing_task.cancel()
            if 'metrics_task' in locals():
                metrics_task.cancel()
    
    async def _capture_video_frames(
        self, 
        video_source: Union[str, int, cv2.VideoCapture],
        callback: Optional[Callable]
    ) -> None:
        """Capture video frames from source"""



        try:
            if isinstance(video_source, (str, int)):
                cap = cv2.VideoCapture(video_source)
            else:
                cap = video_source
            
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer lag
            
            frame_count = 0
            
            while self.is_streaming and cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    self.logger.warning("Failed to read video frame")
                    break
                
                # Convert frame to tensor
                frame_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
                
                # Add to processing queue if not full
                if not self.frame_queue.full():
                    self.frame_queue.put({
                        "frame": frame_tensor,
                        "timestamp": time.time(),
                        "frame_id": frame_count
                    })
                    frame_count += 1
                else:
                    self.metrics.dropped_frames += 1
                
                # Small sleep to control frame rate
                await asyncio.sleep(1.0 / 30.0)  # 30 FPS target
                
            cap.release()
            
        except Exception as e:
            self.logger.error(f"Video capture failed: {e}")
            raise
    
    async def _video_processing_loop(self) -> None:
        """Main video processing loop"""



        try:
            while self.is_streaming:
                try:
                    # Get frame from queue
                    try:
                        frame_data = self.frame_queue.get_nowait()
                    except queue.Empty:
                        await asyncio.sleep(0.001)
                        continue
                    
                    start_time = time.time()
                    
                    # Process frame
                    result = await self._process_video_frame(frame_data)
                    
                    processing_time = (time.time() - start_time) * 1000
                    
                    # Update metrics
                    self.metrics.processed_frames += 1
                    self.metrics.latency_ms = processing_time
                    
                    # Put result in output queue
                    if not self.result_queue.full():
                        self.result_queue.put({
                            "result": result,
                            "latency_ms": processing_time,
                            "frame_id": frame_data["frame_id"],
                            "timestamp": frame_data["timestamp"]
                        })
                    
                except Exception as e:
                    self.logger.warning(f"Video processing loop error: {e}")
                    self.metrics.error_count += 1
                    
        except Exception as e:
            self.logger.error(f"Video processing loop failed: {e}")
    
    async def _process_video_frame(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process single video frame in real-time"""



        try:
            frame_tensor = frame_data["frame"].unsqueeze(0)  # Add batch dimension
            
            # Move to GPU if available
            if self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available():
                frame_tensor = frame_tensor.cuda()
            
            # Process frame
            with torch.no_grad():
                # Analyze frame
                analysis = self.frame_analyzer(frame_tensor)
                
                # Enhance frame
                enhanced = self.enhancer(frame_tensor)
                
                # Detect objects
                detections = self.detector(frame_tensor)
            
            # Convert back to CPU
            if torch.cuda.is_available():
                enhanced = enhanced.cpu()
                analysis = analysis.cpu()
                detections = detections.cpu()
            
            return {
                "enhanced_frame": enhanced.squeeze().permute(1, 2, 0).numpy(),
                "frame_analysis": analysis.squeeze().numpy(),
                "object_detections": detections.squeeze().numpy(),
                "quality_score": self._calculate_frame_quality(frame_tensor, enhanced),
                "processing_info": {
                    "latency_target_met": self.metrics.latency_ms < self._get_latency_threshold(),
                    "gpu_used": self.streaming_config.enable_gpu_acceleration and torch.cuda.is_available()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Frame processing failed: {e}")
            raise
    
    def _calculate_frame_quality(self, original: torch.Tensor, enhanced: torch.Tensor) -> float:
        """Calculate frame quality score"""



        try:
            # Calculate PSNR-based quality
            mse = torch.mean((original - enhanced) ** 2)
            if mse == 0:
                return 1.0
            
            psnr = 20 * torch.log10(1.0 / torch.sqrt(mse))
            quality_score = min(1.0, max(0.0, psnr.item() / 40.0))
            
            return quality_score
            
        except:
            return 0.5
    
    async def _video_metrics_loop(self) -> None:
        """Update video processing metrics"""
        frame_times = deque(maxlen=100)
        last_frame_count = 0
        
        try:
            while self.is_streaming:
                current_time = time.time()
                frame_times.append(current_time)
                
                if len(frame_times) > 1:
                    time_diff = frame_times[-1] - frame_times[0]
                    if time_diff > 0:
                        self.metrics.current_fps = len(frame_times) / time_diff
                
                # Update buffer utilization
                self.metrics.buffer_utilization = self.frame_queue.qsize() / self.streaming_config.buffer_size
                
                # Update GPU metrics
                if torch.cuda.is_available():
                    self.metrics.gpu_utilization = torch.cuda.utilization()
                    self.metrics.memory_usage_mb = torch.cuda.memory_allocated() / (1024 ** 2)
                
                await asyncio.sleep(1.0)
                
        except Exception as e:
            self.logger.warning(f"Video metrics update error: {e}")
    
    async def stop_video_streaming(self) -> Dict[str, Any]:
        """Stop video streaming and return metrics"""
        self.is_streaming = False
        self.logger.info("Stopping real-time video streaming")
        
        return {
            "session_metrics": self.metrics,
            "total_processed": self.metrics.processed_frames,
            "total_dropped": self.metrics.dropped_frames,
            "average_latency": self.metrics.latency_ms,
            "average_fps": self.metrics.avg_fps,
            "error_rate": self.metrics.error_count / max(1, self.metrics.processed_frames)
        }


# Export classes
__all__ = [
    "StreamingMode",
    "ProcessingLatency", 
    "StreamingConfig",
    "StreamMetrics",
    "RealTimeAudioProcessor",
    "RealTimeVideoProcessor"
]
