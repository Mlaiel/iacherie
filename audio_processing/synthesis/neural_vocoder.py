"""
 Neural Vocoder Engine - Advanced AI-Powered Audio Synthesis

This module implements state-of-the-art neural vocoding techniques for
high-quality audio synthesis from spectral representations.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

 LEGAL WARNING: Unauthorized use prohibited. Contact mlaiel@live.de for licensing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Optional, Tuple, Union, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time
import json

logger = logging.getLogger(__name__)


@dataclass
class VocoderConfig:
    """Configuration for neural vocoder models."""
    sample_rate: int = 22050
    hop_length: int = 256
    win_length: int = 1024
    n_fft: int = 1024
    n_mels: int = 80
    fmin: float = 0.0
    fmax: Optional[float] = None
    model_path: Optional[str] = None
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    batch_size: int = 1
    precision: str = "float32"
    
    # WaveNet specific
    layers: int = 30
    stacks: int = 3
    residual_channels: int = 512
    gate_channels: int = 512
    skip_channels: int = 256
    kernel_size: int = 3
    
    # HiFi-GAN specific
    upsample_rates: List[int] = None
    upsample_kernel_sizes: List[int] = None
    resblock_kernel_sizes: List[int] = None
    resblock_dilation_sizes: List[List[int]] = None
    
    def __post_init__(self):
        if self.fmax is None:
            self.fmax = self.sample_rate // 2
        if self.upsample_rates is None:
            self.upsample_rates = [8, 8, 2, 2]
        if self.upsample_kernel_sizes is None:
            self.upsample_kernel_sizes = [16, 16, 4, 4]
        if self.resblock_kernel_sizes is None:
            self.resblock_kernel_sizes = [3, 7, 11]
        if self.resblock_dilation_sizes is None:
            self.resblock_dilation_sizes = [[1, 3, 5], [1, 3, 5], [1, 3, 5]]


class BaseVocoder(ABC, nn.Module):
    """Abstract base class for neural vocoders."""
    
    def __init__(self, config: VocoderConfig):
        super().__init__()
        self.config = config
        self.device = torch.device(config.device)
        self.is_trained = False
        
    @abstractmethod
    def forward(self, mel_spectrogram: torch.Tensor) -> torch.Tensor:
        """Generate waveform from mel-spectrogram."""
        pass
        
    @abstractmethod
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load model weights from checkpoint."""
        pass
        
    def preprocess_mel(self, mel: np.ndarray) -> torch.Tensor:
        """Preprocess mel-spectrogram for vocoder input."""
        mel_tensor = torch.from_numpy(mel).float()
        if len(mel_tensor.shape) == 2:
            mel_tensor = mel_tensor.unsqueeze(0)
        return mel_tensor.to(self.device)
        
    def postprocess_audio(self, audio: torch.Tensor) -> np.ndarray:
        """Postprocess generated audio."""
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()
        if len(audio.shape) > 1:
            audio = audio.squeeze()
        return audio.astype(np.float32)


class WaveNetVocoder(BaseVocoder):
    """WaveNet-based neural vocoder for high-quality audio synthesis."""
    
    def __init__(self, config: VocoderConfig):
        super().__init__(config)
        
        self.n_mels = config.n_mels
        self.layers = config.layers
        self.stacks = config.stacks
        self.residual_channels = config.residual_channels
        self.gate_channels = config.gate_channels
        self.skip_channels = config.skip_channels
        self.kernel_size = config.kernel_size
        
        # Input projection
        self.mel_conv = nn.Conv1d(self.n_mels, self.residual_channels, 1)
        
        # WaveNet layers
        self.dilated_convs = nn.ModuleList()
        self.res_convs = nn.ModuleList()
        self.skip_convs = nn.ModuleList()
        self.gate_convs = nn.ModuleList()
        
        receptive_field = 1
        for stack in range(self.stacks):
            for layer in range(self.layers):
                dilation = 2 ** layer
                receptive_field += dilation * (self.kernel_size - 1)
                
                self.dilated_convs.append(
                    nn.Conv1d(self.residual_channels, 2 * self.gate_channels,
                             self.kernel_size, dilation=dilation, padding=dilation)
                )
                
                self.res_convs.append(
                    nn.Conv1d(self.gate_channels, self.residual_channels, 1)
                )
                
                self.skip_convs.append(
                    nn.Conv1d(self.gate_channels, self.skip_channels, 1)
                )
                
        # Output layers
        self.output_conv1 = nn.Conv1d(self.skip_channels, self.skip_channels, 1)
        self.output_conv2 = nn.Conv1d(self.skip_channels, 1, 1)
        
        self.receptive_field = receptive_field
        
    def forward(self, mel_spectrogram: torch.Tensor) -> torch.Tensor:
        """Generate waveform from mel-spectrogram using WaveNet."""
        # Upsample mel-spectrogram to match audio length
        mel_upsampled = F.interpolate(
            mel_spectrogram, 
            scale_factor=self.config.hop_length,
            mode='linear',
            align_corners=False
        )
        
        # Project mel features
        x = self.mel_conv(mel_upsampled)
        
        # WaveNet layers
        skip_connections = 0
        for i in range(len(self.dilated_convs)):
            # Gated activation
            dilated_out = self.dilated_convs[i](x)
            gate, filter_out = dilated_out.chunk(2, dim=1)
            gate = torch.sigmoid(gate)
            filter_out = torch.tanh(filter_out)
            gated = gate * filter_out
            
            # Residual connection
            res = self.res_convs[i](gated)
            x = x + res
            
            # Skip connection
            skip = self.skip_convs[i](gated)
            skip_connections = skip_connections + skip
            
        # Output layers
        x = F.relu(skip_connections)
        x = F.relu(self.output_conv1(x))
        x = torch.tanh(self.output_conv2(x))
        
        return x.squeeze(1)
        
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load WaveNet model weights."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.load_state_dict(checkpoint['model_state_dict'])
        self.is_trained = True
        logger.info(f"WaveNet checkpoint loaded from {checkpoint_path}")


class HiFiGANGenerator(nn.Module):
    """HiFi-GAN generator architecture."""
    
    def __init__(self, config: VocoderConfig):
        super().__init__()
        self.config = config
        
        self.num_kernels = len(config.resblock_kernel_sizes)
        self.num_upsamples = len(config.upsample_rates)
        
        # Initial convolution
        self.conv_pre = nn.Conv1d(config.n_mels, 512, 7, 1, padding=3)
        
        # Upsampling layers
        self.ups = nn.ModuleList()
        for i, (u, k) in enumerate(zip(config.upsample_rates, config.upsample_kernel_sizes)):
            self.ups.append(
                nn.ConvTranspose1d(512//(2**i), 512//(2**(i+1)), k, u, padding=(k-u)//2)
            )
            
        # Residual blocks
        self.resblocks = nn.ModuleList()
        for i in range(self.num_upsamples):
            ch = 512//(2**(i+1))
            for j, (k, d) in enumerate(zip(config.resblock_kernel_sizes, config.resblock_dilation_sizes)):
                self.resblocks.append(ResBlock(ch, k, d))
                
        # Output convolution
        self.conv_post = nn.Conv1d(ch, 1, 7, 1, padding=3)
        
    def forward(self, x):
        x = self.conv_pre(x)
        
        for i in range(self.num_upsamples):
            x = F.leaky_relu(x, 0.1)
            x = self.ups[i](x)
            
            xs = None
            for j in range(self.num_kernels):
                if xs is None:
                    xs = self.resblocks[i*self.num_kernels+j](x)
                else:
                    xs += self.resblocks[i*self.num_kernels+j](x)
            x = xs / self.num_kernels
            
        x = F.leaky_relu(x)
        x = self.conv_post(x)
        x = torch.tanh(x)
        
        return x


class ResBlock(nn.Module):
    """Residual block for HiFi-GAN."""
    
    def __init__(self, channels: int, kernel_size: int = 3, dilations: List[int] = [1, 3, 5]):
        super().__init__()
        self.convs1 = nn.ModuleList([
            nn.Conv1d(channels, channels, kernel_size, 1, 
                     dilation=d, padding=self.get_padding(kernel_size, d))
            for d in dilations
        ])
        self.convs2 = nn.ModuleList([
            nn.Conv1d(channels, channels, kernel_size, 1, 
                     dilation=1, padding=self.get_padding(kernel_size, 1))
            for _ in dilations
        ])
        
    def get_padding(self, kernel_size: int, dilation: int) -> int:
        return int((kernel_size * dilation - dilation) / 2)
        
    def forward(self, x):
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = F.leaky_relu(x, 0.1)
            xt = c1(xt)
            xt = F.leaky_relu(xt, 0.1)
            xt = c2(xt)
            x = xt + x
        return x


class HiFiGANVocoder(BaseVocoder):
    """HiFi-GAN neural vocoder for high-fidelity audio generation."""
    
    def __init__(self, config: VocoderConfig):
        super().__init__(config)
        self.generator = HiFiGANGenerator(config)
        
    def forward(self, mel_spectrogram: torch.Tensor) -> torch.Tensor:
        """Generate waveform using HiFi-GAN."""



        return self.generator(mel_spectrogram).squeeze(1)
        
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load HiFi-GAN model weights."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.generator.load_state_dict(checkpoint['generator'])
        self.is_trained = True
        logger.info(f"HiFi-GAN checkpoint loaded from {checkpoint_path}")


class MelGANVocoder(BaseVocoder):
    """MelGAN neural vocoder for efficient audio synthesis."""
    
    def __init__(self, config: VocoderConfig):
        super().__init__(config)
        
        # Generator architecture
        self.generator = nn.Sequential(
            nn.ReflectionPad1d(3),
            nn.Conv1d(config.n_mels, 512, 7),
            nn.LeakyReLU(0.2),
            
            # Upsampling blocks
            self._make_upsampling_block(512, 256, 16, 8),
            self._make_upsampling_block(256, 128, 16, 8),
            self._make_upsampling_block(128, 64, 4, 2),
            self._make_upsampling_block(64, 32, 4, 2),
            
            # Output layer
            nn.ReflectionPad1d(3),
            nn.Conv1d(32, 1, 7),
            nn.Tanh()
        )
        
    def _make_upsampling_block(self, in_channels: int, out_channels: int, 
                              kernel_size: int, stride: int) -> nn.Sequential:
        """Create upsampling block for MelGAN."""



        return nn.Sequential(
            nn.ConvTranspose1d(in_channels, out_channels, kernel_size, stride, 
                              padding=(kernel_size - stride) // 2),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
            
            # Residual stack
            nn.Conv1d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm1d(out_channels),
            nn.LeakyReLU(0.2),
            
            nn.Conv1d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm1d(out_channels)
        )
        
    def forward(self, mel_spectrogram: torch.Tensor) -> torch.Tensor:
        """Generate waveform using MelGAN."""



        return self.generator(mel_spectrogram).squeeze(1)
        
    def load_checkpoint(self, checkpoint_path: str) -> None:
        """Load MelGAN model weights."""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.generator.load_state_dict(checkpoint['generator'])
        self.is_trained = True
        logger.info(f"MelGAN checkpoint loaded from {checkpoint_path}")


class NeuralVocoderManager:
    """Manager for multiple neural vocoder models with intelligent routing."""
    
    def __init__(self):
        self.vocoders: Dict[str, BaseVocoder] = {}
        self.default_vocoder = None
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
    def register_vocoder(self, name: str, vocoder: BaseVocoder, 
                        is_default: bool = False) -> None:
        """Register a neural vocoder."""
        self.vocoders[name] = vocoder
        self.performance_metrics[name] = {
            'synthesis_time': 0.0,
            'quality_score': 0.0,
            'memory_usage': 0.0,
            'rtf': 0.0  # Real-time factor
        }
        
        if is_default or self.default_vocoder is None:
            self.default_vocoder = name
            
        logger.info(f"Registered vocoder: {name}")
        
    def synthesize(self, mel_spectrogram: np.ndarray, 
                  vocoder_name: Optional[str] = None,
                  quality_preference: str = "balanced") -> np.ndarray:
        """Synthesize audio using specified or optimal vocoder."""
        if vocoder_name is None:
            vocoder_name = self._select_optimal_vocoder(quality_preference)
            
        if vocoder_name not in self.vocoders:
            raise ValueError(f"Vocoder {vocoder_name} not found")
            
        vocoder = self.vocoders[vocoder_name]
        
        start_time = time.time()
        
        # Preprocess
        mel_tensor = vocoder.preprocess_mel(mel_spectrogram)
        
        # Synthesize
        with torch.no_grad():
            audio_tensor = vocoder(mel_tensor)
            
        # Postprocess
        audio = vocoder.postprocess_audio(audio_tensor)
        
        # Update metrics
        synthesis_time = time.time() - start_time
        rtf = synthesis_time / (len(audio) / vocoder.config.sample_rate)
        
        self.performance_metrics[vocoder_name]['synthesis_time'] = synthesis_time
        self.performance_metrics[vocoder_name]['rtf'] = rtf
        
        return audio
        
    async def synthesize_async(self, mel_spectrogram: np.ndarray,
                              vocoder_name: Optional[str] = None) -> np.ndarray:
        """Asynchronous audio synthesis."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, 
            self.synthesize, 
            mel_spectrogram, 
            vocoder_name
        )
        
    def _select_optimal_vocoder(self, quality_preference: str) -> str:
        """Select optimal vocoder based on quality preference and performance."""
        if quality_preference == "speed":
            # Select fastest vocoder
            return min(self.performance_metrics.keys(),
                      key=lambda x: self.performance_metrics[x]['rtf'])
        elif quality_preference == "quality":
            # Select highest quality vocoder
            return max(self.performance_metrics.keys(),
                      key=lambda x: self.performance_metrics[x]['quality_score'])
        else:  # balanced
            return self.default_vocoder or list(self.vocoders.keys())[0]
            
    def benchmark_vocoders(self, test_mel: np.ndarray, iterations: int = 5) -> Dict:
        """Benchmark all registered vocoders."""
        results = {}
        
        for name, vocoder in self.vocoders.items():
            if not vocoder.is_trained:
                continue
                
            times = []
            for _ in range(iterations):
                start = time.time()
                self.synthesize(test_mel, name)
                times.append(time.time() - start)
                
            results[name] = {
                'avg_time': np.mean(times),
                'std_time': np.std(times),
                'rtf': np.mean(times) / (test_mel.shape[-1] * vocoder.config.hop_length / vocoder.config.sample_rate)
            }
            
        return results
        
    def get_vocoder_info(self) -> Dict:
        """Get information about all registered vocoders."""



        return {
            name: {
                'type': type(vocoder).__name__,
                'config': vocoder.config.__dict__,
                'is_trained': vocoder.is_trained,
                'performance': self.performance_metrics[name]
            }
            for name, vocoder in self.vocoders.items()
        }


class VocoderConfigManager:
    """Configuration manager for neural vocoders with preset management."""
    
    def __init__(self):
        self.presets: Dict[str, VocoderConfig] = {}
        self._load_default_presets()
        
    def _load_default_presets(self) -> None:
        """Load default vocoder presets."""
        # High quality preset
        self.presets['high_quality'] = VocoderConfig(
            sample_rate=48000,
            n_mels=128,
            layers=40,
            stacks=4,
            residual_channels=768,
            precision="float32"
        )
        
        # Fast synthesis preset
        self.presets['fast'] = VocoderConfig(
            sample_rate=22050,
            n_mels=80,
            layers=20,
            stacks=2,
            residual_channels=256,
            precision="float16"
        )
        
        # Balanced preset
        self.presets['balanced'] = VocoderConfig(
            sample_rate=22050,
            n_mels=80,
            layers=30,
            stacks=3,
            residual_channels=512,
            precision="float32"
        )
        
    def create_config(self, preset_name: str = "balanced",
                     **overrides) -> VocoderConfig:
        """Create vocoder configuration from preset with overrides."""
        if preset_name not in self.presets:
            raise ValueError(f"Preset {preset_name} not found")
            
        base_config = self.presets[preset_name]
        config_dict = base_config.__dict__.copy()
        config_dict.update(overrides)
        
        return VocoderConfig(**config_dict)
        
    def save_preset(self, name: str, config: VocoderConfig) -> None:
        """Save configuration as preset."""
        self.presets[name] = config
        
    def export_config(self, config: VocoderConfig, filepath: str) -> None:
        """Export configuration to JSON file."""
        config_dict = config.__dict__.copy()
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
            
    def import_config(self, filepath: str) -> VocoderConfig:
        """Import configuration from JSON file."""
        with open(filepath, 'r') as f:
            config_dict = json.load(f)
        return VocoderConfig(**config_dict)


# Factory function for easy vocoder creation
def create_vocoder(vocoder_type: str, config: VocoderConfig) -> BaseVocoder:
    """Factory function to create vocoder instances."""
    vocoders = {
        'wavenet': WaveNetVocoder,
        'hifigan': HiFiGANVocoder,
        'melgan': MelGANVocoder
    }
    
    if vocoder_type.lower() not in vocoders:
        raise ValueError(f"Unknown vocoder type: {vocoder_type}")
        
    return vocoders[vocoder_type.lower()](config)
