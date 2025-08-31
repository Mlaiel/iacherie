"""Neural Networks Utilities - IA Influencer Agent

Advanced utilities for neural network operations, data processing,
model management, and production deployment support.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  LEGAL WARNING / AVERTISSEMENT LÉGAL ⚠️
This code is the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use is strictly prohibited.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
import logging
import time
from pathlib import Path
import json
import hashlib
from dataclasses import dataclass
from contextlib import contextmanager
import psutil
import GPUtil
from PIL import Image
import librosa
import cv2
from transformers import AutoTokenizer, AutoProcessor

logger = logging.getLogger(__name__)


@dataclass
class ModelMetrics:
    """Comprehensive model performance metrics"""    accuracy: float
    precision: float
    recall: float
    f1_score: float
    inference_time_ms: float
    memory_usage_mb: float
    gpu_utilization: float
    throughput_samples_per_second: float
    confidence_scores: List[float]
    error_rates: Dict[str, float]


class DeviceManager:
    """Intelligent device management for optimal performance"""    
    def __init__(self):
        self.available_devices = self._detect_devices()
        self.device_capabilities = self._get_device_capabilities()
    
    def _detect_devices(self) -> List[str]:
        """Detect available computing devices"""        devices = ["cpu"]
        
        # CUDA devices
        if torch.cuda.is_available():
            for i in range(torch.cuda.device_count()):
                devices.append(f"cuda:{i}")
        
        # MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            devices.append("mps")
        
        return devices
    
    def _get_device_capabilities(self) -> Dict[str, Dict]:
        """Get capabilities and specs for each device"""        capabilities = {}
        
        for device in self.available_devices:
            if device == "cpu":
                capabilities[device] = {
                    "memory_gb": psutil.virtual_memory().total / (1024**3),
                    "cores": psutil.cpu_count(),
                    "type": "cpu"
                }
            elif device.startswith("cuda"):
                gpu_id = int(device.split(":")[1]) if ":" in device else 0
                try:
                    gpu = GPUtil.getGPUs()[gpu_id]
                    capabilities[device] = {
                        "memory_gb": gpu.memoryTotal / 1024,
                        "name": gpu.name,
                        "compute_capability": torch.cuda.get_device_capability(gpu_id),
                        "type": "gpu"
                    }
                except:
                    capabilities[device] = {"type": "gpu", "memory_gb": 0}
            elif device == "mps":
                capabilities[device] = {
                    "type": "mps",
                    "memory_gb": 16  # Typical Apple Silicon unified memory
                }
        
        return capabilities
    
    def get_optimal_device(self, model_size_mb: float = 0) -> str:
        """Select optimal device based on model size and availability"""        
        # Prefer GPU if available and model fits in memory
        gpu_devices = [d for d in self.available_devices if d.startswith("cuda")]
        if gpu_devices:
            for device in gpu_devices:
                if device in self.device_capabilities:
                    available_memory = self.device_capabilities[device]["memory_gb"] * 1024
                    if model_size_mb < available_memory * 0.8:  # 80% threshold
                        return device
        
        # Fallback to MPS if available
        if "mps" in self.available_devices:
            return "mps"
        
        # Default to CPU
        return "cpu"


class DataPreprocessor:
    """Advanced data preprocessing for multi-modal content"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
        
    def preprocess_audio(
        self,
        audio_path: str,
        target_sr: int = 44100,
        duration: Optional[float] = None
    ) -> Dict[str, np.ndarray]:
        """Preprocess audio file for neural network input"""        
        try:
            # Load audio
            audio, sr = librosa.load(audio_path, sr=target_sr, duration=duration)
            
            # Extract features
            features = {
                "waveform": audio,
                "mfcc": librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=13),
                "spectral_centroid": librosa.feature.spectral_centroid(y=audio, sr=sr),
                "spectral_rolloff": librosa.feature.spectral_rolloff(y=audio, sr=sr),
                "zero_crossing_rate": librosa.feature.zero_crossing_rate(audio),
                "chroma": librosa.feature.chroma_stft(y=audio, sr=sr),
                "mel_spectrogram": librosa.feature.melspectrogram(y=audio, sr=sr)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error preprocessing audio {audio_path}: {e}")
            return {}
    
    def preprocess_image(
        self,
        image_path: str,
        target_size: Tuple[int, int] = (224, 224)
    ) -> Dict[str, np.ndarray]:
        """Preprocess image for neural network input"""        
        try:
            # Load and resize image
            image = Image.open(image_path).convert('RGB')
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to array and normalize
            image_array = np.array(image) / 255.0
            
            # Extract additional features
            gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
            
            features = {
                "rgb_array": image_array,
                "normalized": (image_array - 0.5) / 0.5,  # [-1, 1] normalization
                "grayscale": gray_image / 255.0,
                "histogram": cv2.calcHist([np.array(image)], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error preprocessing image {image_path}: {e}")
            return {}
    
    def preprocess_video(
        self,
        video_path: str,
        max_frames: int = 30,
        frame_size: Tuple[int, int] = (224, 224)
    ) -> Dict[str, np.ndarray]:
        """Preprocess video for neural network input"""        
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            
            # Extract frames
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = frame_count / fps if fps > 0 else 0
            
            # Sample frames uniformly
            if frame_count > max_frames:
                frame_indices = np.linspace(0, frame_count - 1, max_frames, dtype=int)
            else:
                frame_indices = list(range(frame_count))
            
            for frame_idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                if ret:
                    # Resize and normalize
                    frame = cv2.resize(frame, frame_size)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) / 255.0
                    frames.append(frame)
            
            cap.release()
            
            features = {
                "frames": np.array(frames),
                "frame_count": frame_count,
                "fps": fps,
                "duration": duration,
                "aspect_ratio": frame_size[0] / frame_size[1]
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error preprocessing video {video_path}: {e}")
            return {}
    
    def preprocess_text(
        self,
        text: str,
        max_length: int = 512
    ) -> Dict[str, Union[List[int], torch.Tensor]]:
        """Preprocess text for neural network input"""        
        try:
            # Tokenize text
            encoded = self.tokenizer.encode_plus(
                text,
                max_length=max_length,
                padding='max_length',
                truncation=True,
                return_attention_mask=True,
                return_tensors='pt'
            )
            
            features = {
                "input_ids": encoded['input_ids'].squeeze().tolist(),
                "attention_mask": encoded['attention_mask'].squeeze().tolist(),
                "token_count": len([t for t in encoded['input_ids'].squeeze().tolist() if t != 0]),
                "text_length": len(text),
                "word_count": len(text.split())
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error preprocessing text: {e}")
            return {}


class ModelOptimizer:
    """Advanced model optimization and acceleration"""    
    @staticmethod
    def optimize_model_for_inference(
        model: nn.Module,
        example_input: torch.Tensor,
        optimization_level: str = "basic"
    ) -> nn.Module:
        """Optimize model for inference with various techniques"""        
        model.eval()
        
        # Basic optimizations
        if optimization_level in ["basic", "advanced", "ultra"]:
            # JIT compilation
            try:
                model = torch.jit.trace(model, example_input)
                logger.info("Model successfully JIT compiled")
            except Exception as e:
                logger.warning(f"JIT compilation failed: {e}")
        
        # Advanced optimizations
        if optimization_level in ["advanced", "ultra"]:
            # Quantization
            try:
                model = torch.quantization.quantize_dynamic(
                    model, 
                    {nn.Linear, nn.Conv2d}, 
                    dtype=torch.qint8
                )
                logger.info("Model quantization applied")
            except Exception as e:
                logger.warning(f"Quantization failed: {e}")
        
        # Ultra optimizations
        if optimization_level == "ultra":
            # ONNX export for further optimization
            try:
                import onnx
                import onnxruntime
                
                dummy_input = example_input
                onnx_path = "temp_model.onnx"
                torch.onnx.export(model, dummy_input, onnx_path, opset_version=11)
                logger.info("ONNX export successful")
            except Exception as e:
                logger.warning(f"ONNX export failed: {e}")
        
        return model
    
    @staticmethod
    def calculate_model_size(model: nn.Module) -> Dict[str, float]:
        """Calculate model size and parameter statistics"""        
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        # Calculate memory usage (rough estimate)
        memory_mb = total_params * 4 / (1024 * 1024)  # Assuming float32
        
        return {
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "non_trainable_parameters": total_params - trainable_params,
            "memory_mb": memory_mb,
            "memory_gb": memory_mb / 1024
        }


class PerformanceProfiler:
    """Advanced performance profiling and monitoring"""    
    def __init__(self):
        self.metrics_history = []
        self.start_time = None
        
    @contextmanager
    def profile_inference(self, model_name: str = "unknown"):
        """Context manager for profiling model inference"""        
        # Record start metrics
        start_time = time.time()
        start_memory = self._get_memory_usage()
        start_gpu = self._get_gpu_usage()
        
        try:
            yield
        finally:
            # Record end metrics
            end_time = time.time()
            end_memory = self._get_memory_usage()
            end_gpu = self._get_gpu_usage()
            
            metrics = {
                "model_name": model_name,
                "inference_time_ms": (end_time - start_time) * 1000,
                "memory_delta_mb": end_memory - start_memory,
                "gpu_utilization_avg": (start_gpu + end_gpu) / 2,
                "timestamp": time.time()
            }
            
            self.metrics_history.append(metrics)
            logger.info(f"Inference metrics for {model_name}: {metrics}")
    
    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""        return psutil.Process().memory_info().rss / (1024 * 1024)
    
    def _get_gpu_usage(self) -> float:
        """Get current GPU utilization percentage"""        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except:
            pass
        return 0.0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""        
        if not self.metrics_history:
            return {}
        
        inference_times = [m["inference_time_ms"] for m in self.metrics_history]
        memory_usage = [m["memory_delta_mb"] for m in self.metrics_history]
        
        return {
            "total_inferences": len(self.metrics_history),
            "avg_inference_time_ms": np.mean(inference_times),
            "median_inference_time_ms": np.median(inference_times),
            "p95_inference_time_ms": np.percentile(inference_times, 95),
            "avg_memory_delta_mb": np.mean(memory_usage),
            "max_memory_delta_mb": np.max(memory_usage),
            "throughput_per_second": 1000 / np.mean(inference_times) if inference_times else 0
        }


class ContentAnalyzer:
    """Advanced content analysis utilities"""    
    @staticmethod
    def extract_content_metadata(file_path: str) -> Dict[str, Any]:
        """Extract comprehensive metadata from content files"""        
        metadata = {
            "file_path": str(file_path),
            "file_size_mb": Path(file_path).stat().st_size / (1024 * 1024),
            "file_extension": Path(file_path).suffix.lower(),
            "creation_time": Path(file_path).stat().st_ctime,
            "modification_time": Path(file_path).stat().st_mtime
        }
        
        # Audio metadata
        if metadata["file_extension"] in [".mp3", ".wav", ".flac", ".m4a"]:
            try:
                import mutagen
                audio_file = mutagen.File(file_path)
                if audio_file:
                    metadata.update({
                        "duration_seconds": audio_file.info.length,
                        "bitrate": getattr(audio_file.info, 'bitrate', None),
                        "sample_rate": getattr(audio_file.info, 'sample_rate', None),
                        "channels": getattr(audio_file.info, 'channels', None)
                    })
            except Exception as e:
                logger.warning(f"Failed to extract audio metadata: {e}")
        
        # Image metadata
        elif metadata["file_extension"] in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                with Image.open(file_path) as img:
                    metadata.update({
                        "width": img.width,
                        "height": img.height,
                        "mode": img.mode,
                        "format": img.format
                    })
            except Exception as e:
                logger.warning(f"Failed to extract image metadata: {e}")
        
        # Video metadata
        elif metadata["file_extension"] in [".mp4", ".avi", ".mov", ".mkv"]:
            try:
                cap = cv2.VideoCapture(file_path)
                metadata.update({
                    "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    "fps": cap.get(cv2.CAP_PROP_FPS),
                    "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                    "duration_seconds": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
                })
                cap.release()
            except Exception as e:
                logger.warning(f"Failed to extract video metadata: {e}")
        
        return metadata
    
    @staticmethod
    def generate_content_hash(content: Union[str, bytes, np.ndarray]) -> str:
        """Generate unique hash for content"""        
        if isinstance(content, str):
            content_bytes = content.encode('utf-8')
        elif isinstance(content, np.ndarray):
            content_bytes = content.tobytes()
        else:
            content_bytes = content
        
        return hashlib.sha256(content_bytes).hexdigest()
    
    @staticmethod
    def calculate_content_similarity(
        content1: np.ndarray,
        content2: np.ndarray,
        method: str = "cosine"
    ) -> float:
        """Calculate similarity between content features"""        
        if method == "cosine":
            # Flatten arrays if needed
            flat1 = content1.flatten()
            flat2 = content2.flatten()
            
            # Cosine similarity
            dot_product = np.dot(flat1, flat2)
            norm1 = np.linalg.norm(flat1)
            norm2 = np.linalg.norm(flat2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        
        elif method == "euclidean":
            return 1.0 / (1.0 + np.linalg.norm(content1.flatten() - content2.flatten()))
        
        else:
            raise ValueError(f"Unsupported similarity method: {method}")


# Utility instances for global use
device_manager = DeviceManager()
profiler = PerformanceProfiler()

# Export utilities
__all__ = [
    "ModelMetrics",
    "DeviceManager", 
    "DataPreprocessor",
    "ModelOptimizer",
    "PerformanceProfiler",
    "ContentAnalyzer",
    "device_manager",
    "profiler"
]
