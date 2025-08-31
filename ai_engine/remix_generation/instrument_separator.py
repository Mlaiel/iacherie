#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent Instrument Separator
================================================================================
Module: ai_engine/remix_generation/instrument_separator.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Audio Source Separation AI (Level 3)
Created: 2025-08-30
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps + IA Prompt Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Séparation avancée de sources audio et isolation d'instruments avec IA
TECHNOLOGIES: Deep Learning, Spectral Analysis, Neural Networks, Audio Processing
LOGIQUE MÉTIER: Mixed audio → Source analysis → Neural separation → Quality enhancement → Isolated tracks
"""import asyncio
import logging
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
import librosa
import scipy.signal as signal
from scipy.sparse import diags
import sklearn.decomposition

# Configure logging
logger = logging.getLogger(__name__)

class InstrumentType(Enum):
    """Types of instruments for separation"""    VOCALS = "vocals"
    DRUMS = "drums"
    BASS = "bass"
    GUITAR = "guitar"
    PIANO = "piano"
    STRINGS = "strings"
    BRASS = "brass"
    WOODWINDS = "woodwinds"
    SYNTHESIZER = "synthesizer"
    PERCUSSION = "percussion"
    HARMONIC = "harmonic"
    PERCUSSIVE = "percussive"
    OTHER = "other"

class SeparationMethod(Enum):
    """Source separation methods"""    NEURAL_NETWORK = "neural_network"
    SPECTRAL_MASKING = "spectral_masking"
    HARMONIC_PERCUSSIVE = "harmonic_percussive"
    NON_NEGATIVE_FACTORIZATION = "nnf"
    INDEPENDENT_COMPONENT_ANALYSIS = "ica"
    MEDIAN_FILTERING = "median_filtering"
    REPET = "repet"
    SPLEETER = "spleeter"

class SeparationQuality(Enum):
    """Quality levels for separation"""    FAST = "fast"
    STANDARD = "standard"
    HIGH = "high"
    AUDIOPHILE = "audiophile"

@dataclass
class SeparationParameters:
    """Parameters for source separation"""    method: SeparationMethod = SeparationMethod.NEURAL_NETWORK
    quality: SeparationQuality = SeparationQuality.HIGH
    target_instruments: List[InstrumentType] = field(default_factory=lambda: [InstrumentType.VOCALS, InstrumentType.DRUMS, InstrumentType.BASS, InstrumentType.OTHER])
    frame_size: int = 4096
    hop_length: int = 1024
    num_iterations: int = 100
    spectral_resolution: int = 2048
    temporal_resolution: float = 0.1
    isolation_threshold: float = 0.7
    noise_suppression: bool = True
    harmonic_emphasis: float = 1.0
    percussive_emphasis: float = 1.0

@dataclass
class SeparatedTrack:
    """Individual separated track"""    instrument_type: InstrumentType
    audio_data: np.ndarray
    confidence_score: float
    spectral_mask: np.ndarray
    quality_metrics: Dict[str, float]
    isolation_level: float

@dataclass
class SeparationResult:
    """Complete separation result"""    separation_id: str
    original_audio: np.ndarray
    separated_tracks: Dict[InstrumentType, SeparatedTrack]
    sample_rate: int
    separation_method: SeparationMethod
    quality_assessment: Dict[str, float]
    processing_time_seconds: float
    parameters_used: SeparationParameters
    success: bool

class UNetSeparator(nn.Module):
    """U-Net architecture for source separation"""    
    def __init__(self, input_channels: int = 2, output_channels: int = 4, 
                 feature_maps: int = 64):
        super(UNetSeparator, self).__init__()
        
        self.input_channels = input_channels
        self.output_channels = output_channels
        
        # Encoder (downsampling)
        self.enc1 = self._conv_block(input_channels, feature_maps)
        self.enc2 = self._conv_block(feature_maps, feature_maps * 2)
        self.enc3 = self._conv_block(feature_maps * 2, feature_maps * 4)
        self.enc4 = self._conv_block(feature_maps * 4, feature_maps * 8)
        
        # Bottleneck
        self.bottleneck = self._conv_block(feature_maps * 8, feature_maps * 16)
        
        # Decoder (upsampling)
        self.upconv4 = nn.ConvTranspose2d(feature_maps * 16, feature_maps * 8, 2, stride=2)
        self.dec4 = self._conv_block(feature_maps * 16, feature_maps * 8)
        
        self.upconv3 = nn.ConvTranspose2d(feature_maps * 8, feature_maps * 4, 2, stride=2)
        self.dec3 = self._conv_block(feature_maps * 8, feature_maps * 4)
        
        self.upconv2 = nn.ConvTranspose2d(feature_maps * 4, feature_maps * 2, 2, stride=2)
        self.dec2 = self._conv_block(feature_maps * 4, feature_maps * 2)
        
        self.upconv1 = nn.ConvTranspose2d(feature_maps * 2, feature_maps, 2, stride=2)
        self.dec1 = self._conv_block(feature_maps * 2, feature_maps)
        
        # Output layer
        self.final_conv = nn.Conv2d(feature_maps, output_channels, 1)
        
    def _conv_block(self, in_channels: int, out_channels: int):
        """Convolutional block with batch normalization and activation"""        return nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder path
        enc1 = self.enc1(x)
        enc2 = self.enc2(F.max_pool2d(enc1, 2))
        enc3 = self.enc3(F.max_pool2d(enc2, 2))
        enc4 = self.enc4(F.max_pool2d(enc3, 2))
        
        # Bottleneck
        bottleneck = self.bottleneck(F.max_pool2d(enc4, 2))
        
        # Decoder path
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.dec4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.dec3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.dec2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.dec1(dec1)
        
        # Output
        output = torch.sigmoid(self.final_conv(dec1))
        
        return output

class ConvTasNet(nn.Module):
    """Conv-TasNet for real-time source separation"""    
    def __init__(self, num_sources: int = 4, encoder_dim: int = 512, 
                 num_blocks: int = 8, num_repeats: int = 3):
        super(ConvTasNet, self).__init__()
        
        self.num_sources = num_sources
        self.encoder_dim = encoder_dim
        
        # Encoder
        self.encoder = nn.Conv1d(1, encoder_dim, 20, stride=10, bias=False)
        
        # Separation network
        self.separation_net = TCNSeparator(encoder_dim, num_sources, num_blocks, num_repeats)
        
        # Decoder
        self.decoder = nn.ConvTranspose1d(encoder_dim, 1, 20, stride=10, bias=False)
        
    def forward(self, x):
        batch_size, num_channels, seq_len = x.shape
        
        # Reshape for mono processing
        x = x.view(batch_size * num_channels, 1, seq_len)
        
        # Encode
        encoded = self.encoder(x)
        
        # Separate
        masks = self.separation_net(encoded)
        
        # Apply masks
        separated = []
        for i in range(self.num_sources):
            masked = encoded * masks[:, i:i+1, :]
            decoded = self.decoder(masked)
            separated.append(decoded)
        
        # Stack sources
        separated = torch.stack(separated, dim=1)
        
        # Reshape back to original format
        separated = separated.view(batch_size, num_channels, self.num_sources, seq_len)
        
        return separated

class TCNSeparator(nn.Module):
    """Temporal Convolutional Network for separation"""    
    def __init__(self, input_dim: int, num_sources: int, 
                 num_blocks: int = 8, num_repeats: int = 3):
        super(TCNSeparator, self).__init__()
        
        self.num_sources = num_sources
        
        # Layer normalization
        self.layer_norm = nn.GroupNorm(1, input_dim, eps=1e-8)
        
        # Bottleneck layer
        self.bottleneck = nn.Conv1d(input_dim, input_dim, 1)
        
        # TCN blocks
        self.tcn_blocks = nn.ModuleList()
        for r in range(num_repeats):
            for x in range(num_blocks):
                dilation = 2 ** x
                self.tcn_blocks.append(
                    TCNBlock(input_dim, input_dim, 3, dilation)
                )
        
        # Output layer
        self.output = nn.Conv1d(input_dim, num_sources * input_dim, 1)
        
    def forward(self, x):
        # Normalization
        x = self.layer_norm(x)
        
        # Bottleneck
        x = self.bottleneck(x)
        residual = x
        
        # TCN processing
        for block in self.tcn_blocks:
            x = block(x)
            x = x + residual
            residual = x
        
        # Output masks
        output = self.output(x)
        
        # Reshape to [batch, num_sources, features, time]
        batch_size, features, time_steps = output.shape
        output = output.view(batch_size, self.num_sources, features, time_steps)
        
        # Apply sigmoid activation for masking
        masks = torch.sigmoid(output)
        
        return masks

class TCNBlock(nn.Module):
    """Temporal Convolutional Block"""    
    def __init__(self, input_dim: int, hidden_dim: int, 
                 kernel_size: int, dilation: int):
        super(TCNBlock, self).__init__()
        
        # Depthwise separable convolution
        self.depthwise = nn.Conv1d(
            input_dim, input_dim, kernel_size,
            padding=(kernel_size - 1) * dilation // 2,
            dilation=dilation, groups=input_dim
        )
        
        self.pointwise = nn.Conv1d(input_dim, hidden_dim, 1)
        
        # Normalization and activation
        self.norm = nn.GroupNorm(1, hidden_dim, eps=1e-8)
        self.activation = nn.PReLU()
        
        # Output projection
        self.output_proj = nn.Conv1d(hidden_dim, input_dim, 1)
        
    def forward(self, x):
        # Depthwise separable convolution
        out = self.depthwise(x)
        out = self.pointwise(out)
        
        # Normalization and activation
        out = self.norm(out)
        out = self.activation(out)
        
        # Output projection
        out = self.output_proj(out)
        
        return out

class SpectralAnalyzer:
    """Advanced spectral analysis for source separation"""    
    def __init__(self):
        self.instrument_profiles = self._initialize_instrument_profiles()
    
    def _initialize_instrument_profiles(self) -> Dict[InstrumentType, Dict[str, Any]]:
        """Initialize spectral profiles for different instruments"""        return {
            InstrumentType.VOCALS: {
                "frequency_range": (80, 1200),
                "formant_regions": [(400, 800), (800, 1200), (2400, 3200)],
                "harmonic_content": "high",
                "temporal_characteristics": "variable",
                "spectral_centroid_range": (500, 2000)
            },
            InstrumentType.DRUMS: {
                "frequency_range": (40, 15000),
                "dominant_frequencies": [60, 100, 200, 400, 1000, 5000, 10000],
                "harmonic_content": "low",
                "temporal_characteristics": "transient",
                "spectral_centroid_range": (1000, 8000)
            },
            InstrumentType.BASS: {
                "frequency_range": (40, 350),
                "fundamental_range": (40, 200),
                "harmonic_content": "medium",
                "temporal_characteristics": "sustained",
                "spectral_centroid_range": (80, 300)
            },
            InstrumentType.GUITAR: {
                "frequency_range": (80, 5000),
                "fundamental_range": (80, 1200),
                "harmonic_content": "high",
                "temporal_characteristics": "mixed",
                "spectral_centroid_range": (200, 2000)
            },
            InstrumentType.PIANO: {
                "frequency_range": (27, 4200),
                "harmonic_structure": "rich",
                "attack_characteristics": "sharp",
                "decay_characteristics": "exponential",
                "spectral_centroid_range": (400, 2000)
            }
        }
    
    async def analyze_spectral_content(self, audio: np.ndarray, 
                                     sample_rate: int = 44100) -> Dict[str, Any]:
        """Analyze spectral content of audio"""        try:
            # Compute STFT
            stft = librosa.stft(audio, n_fft=2048, hop_length=512)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sample_rate)[0]
            zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]
            
            # Harmonic-percussive separation
            harmonic, percussive = librosa.decompose.hpss(stft)
            
            # Onset detection
            onset_frames = librosa.onset.onset_detect(y=audio, sr=sample_rate)
            onset_times = librosa.frames_to_time(onset_frames, sr=sample_rate)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(S=magnitude, sr=sample_rate)
            
            return {
                "stft_magnitude": magnitude,
                "stft_phase": phase,
                "harmonic_component": harmonic,
                "percussive_component": percussive,
                "spectral_centroid": spectral_centroid,
                "spectral_rolloff": spectral_rolloff,
                "spectral_bandwidth": spectral_bandwidth,
                "zero_crossing_rate": zero_crossing_rate,
                "onset_times": onset_times,
                "chroma": chroma,
                "frequency_bins": librosa.fft_frequencies(sr=sample_rate, n_fft=2048)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing spectral content: {e}")
            return {}
    
    async def identify_instruments(self, spectral_data: Dict[str, Any]) -> Dict[InstrumentType, float]:
        """Identify likely instruments based on spectral analysis"""        try:
            instrument_scores = {}
            
            magnitude = spectral_data.get("stft_magnitude", np.array([]))
            if magnitude.size == 0:
                return {}
            
            # Calculate average spectrum
            avg_spectrum = np.mean(magnitude, axis=1)
            freqs = spectral_data.get("frequency_bins", np.arange(len(avg_spectrum)))
            
            # Score each instrument type
            for instrument, profile in self.instrument_profiles.items():
                score = await self._calculate_instrument_score(
                    avg_spectrum, freqs, profile, spectral_data
                )
                instrument_scores[instrument] = score
            
            # Normalize scores
            total_score = sum(instrument_scores.values())
            if total_score > 0:
                instrument_scores = {k: v/total_score for k, v in instrument_scores.items()}
            
            return instrument_scores
            
        except Exception as e:
            logger.error(f"Error identifying instruments: {e}")
            return {}
    
    async def _calculate_instrument_score(self, spectrum: np.ndarray, 
                                        frequencies: np.ndarray,
                                        profile: Dict[str, Any],
                                        spectral_data: Dict[str, Any]) -> float:
        """Calculate likelihood score for specific instrument"""        try:
            score = 0.0
            
            # Frequency range matching
            freq_range = profile.get("frequency_range", (20, 20000))
            freq_mask = (frequencies >= freq_range[0]) & (frequencies <= freq_range[1])
            
            if np.any(freq_mask):
                range_energy = np.sum(spectrum[freq_mask])
                total_energy = np.sum(spectrum)
                if total_energy > 0:
                    score += (range_energy / total_energy) * 0.3
            
            # Spectral centroid matching
            centroid_range = profile.get("spectral_centroid_range", (0, 22050))
            avg_centroid = np.mean(spectral_data.get("spectral_centroid", [1000]))
            
            if centroid_range[0] <= avg_centroid <= centroid_range[1]:
                centroid_score = 1.0 - abs(avg_centroid - np.mean(centroid_range)) / (centroid_range[1] - centroid_range[0])
                score += centroid_score * 0.2
            
            # Harmonic vs percussive content
            harmonic_component = spectral_data.get("harmonic_component", np.array([]))
            percussive_component = spectral_data.get("percussive_component", np.array([]))
            
            if harmonic_component.size > 0 and percussive_component.size > 0:
                harmonic_energy = np.sum(np.abs(harmonic_component))
                percussive_energy = np.sum(np.abs(percussive_component))
                total_hp_energy = harmonic_energy + percussive_energy
                
                if total_hp_energy > 0:
                    harmonic_ratio = harmonic_energy / total_hp_energy
                    
                    harmonic_content = profile.get("harmonic_content", "medium")
                    if harmonic_content == "high" and harmonic_ratio > 0.7:
                        score += 0.3
                    elif harmonic_content == "low" and harmonic_ratio < 0.3:
                        score += 0.3
                    elif harmonic_content == "medium" and 0.3 <= harmonic_ratio <= 0.7:
                        score += 0.3
            
            # Temporal characteristics
            onset_times = spectral_data.get("onset_times", [])
            temporal_char = profile.get("temporal_characteristics", "mixed")
            
            if len(onset_times) > 1:
                onset_density = len(onset_times) / spectral_data.get("duration", 1.0)
                
                if temporal_char == "transient" and onset_density > 2.0:
                    score += 0.2
                elif temporal_char == "sustained" and onset_density < 1.0:
                    score += 0.2
                elif temporal_char == "variable":
                    score += 0.1
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.error(f"Error calculating instrument score: {e}")
            return 0.0

class InstrumentSeparator:
    """Main instrument separation engine"""    
    def __init__(self):
        # Neural networks
        self.unet_model = UNetSeparator()
        self.convtasnet_model = ConvTasNet()
        
        # Analysis components
        self.spectral_analyzer = SpectralAnalyzer()
        
        # Separation algorithms
        self.separation_algorithms = {
            SeparationMethod.NEURAL_NETWORK: self._separate_with_neural_network,
            SeparationMethod.SPECTRAL_MASKING: self._separate_with_spectral_masking,
            SeparationMethod.HARMONIC_PERCUSSIVE: self._separate_harmonic_percussive,
            SeparationMethod.NON_NEGATIVE_FACTORIZATION: self._separate_with_nnf,
            SeparationMethod.INDEPENDENT_COMPONENT_ANALYSIS: self._separate_with_ica,
            SeparationMethod.MEDIAN_FILTERING: self._separate_with_median_filtering,
            SeparationMethod.REPET: self._separate_with_repet
        }
        
        # Separation history
        self.separation_history = []
        
        logger.info("InstrumentSeparator initialized successfully")
    
    async def separate_sources(self, audio: np.ndarray,
                             sample_rate: int = 44100,
                             parameters: SeparationParameters = SeparationParameters()) -> SeparationResult:
        """Separate audio sources into individual instruments"""        try:
            start_time = datetime.now()
            separation_id = f"separation_{int(start_time.timestamp())}"
            
            # Analyze spectral content
            spectral_data = await self.spectral_analyzer.analyze_spectral_content(audio, sample_rate)
            
            # Identify likely instruments
            instrument_probabilities = await self.spectral_analyzer.identify_instruments(spectral_data)
            
            # Perform separation
            separation_func = self.separation_algorithms.get(
                parameters.method, self._separate_with_neural_network
            )
            
            separated_tracks = await separation_func(
                audio, sample_rate, parameters, spectral_data, instrument_probabilities
            )
            
            # Quality assessment
            quality_assessment = await self._assess_separation_quality(
                audio, separated_tracks, parameters
            )
            
            # Processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = SeparationResult(
                separation_id=separation_id,
                original_audio=audio,
                separated_tracks=separated_tracks,
                sample_rate=sample_rate,
                separation_method=parameters.method,
                quality_assessment=quality_assessment,
                processing_time_seconds=processing_time,
                parameters_used=parameters,
                success=quality_assessment.get("overall_quality", 0.0) >= 0.6
            )
            
            # Store in history
            self.separation_history.append({
                "timestamp": start_time.isoformat(),
                "separation_id": separation_id,
                "method": parameters.method.value,
                "quality": parameters.quality.value,
                "num_tracks": len(separated_tracks),
                "overall_quality": quality_assessment.get("overall_quality", 0.0)
            })
            
            logger.info(f"Separated sources {separation_id}: {len(separated_tracks)} tracks, quality={quality_assessment.get('overall_quality', 0.0):.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error separating sources: {e}")
            raise
    
    async def _separate_with_neural_network(self, audio: np.ndarray,
                                          sample_rate: int,
                                          parameters: SeparationParameters,
                                          spectral_data: Dict[str, Any],
                                          instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using neural network models"""        try:
            # Convert to tensor
            if audio.ndim == 1:
                audio_tensor = torch.FloatTensor(audio).unsqueeze(0).unsqueeze(0)
            else:
                audio_tensor = torch.FloatTensor(audio.T).unsqueeze(0)
            
            # Use ConvTasNet for real-time separation
            with torch.no_grad():
                separated_sources = self.convtasnet_model(audio_tensor)
            
            # Convert back to numpy
            separated_sources = separated_sources.squeeze(0).cpu().numpy()
            
            # Create separated tracks
            separated_tracks = {}
            target_instruments = parameters.target_instruments
            
            for i, instrument in enumerate(target_instruments):
                if i < separated_sources.shape[1]:
                    track_audio = separated_sources[0, i, :]  # Take first channel
                    
                    # Calculate confidence based on instrument probabilities
                    confidence = instrument_probs.get(instrument, 0.5)
                    
                    # Create spectral mask (simplified)
                    stft = librosa.stft(track_audio)
                    spectral_mask = np.abs(stft) > (np.max(np.abs(stft)) * 0.1)
                    
                    # Quality metrics
                    quality_metrics = await self._calculate_track_quality(track_audio, audio)
                    
                    # Isolation level
                    isolation_level = await self._calculate_isolation_level(track_audio, audio)
                    
                    separated_track = SeparatedTrack(
                        instrument_type=instrument,
                        audio_data=track_audio,
                        confidence_score=confidence,
                        spectral_mask=spectral_mask,
                        quality_metrics=quality_metrics,
                        isolation_level=isolation_level
                    )
                    
                    separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in neural network separation: {e}")
            # Fallback to spectral masking
            return await self._separate_with_spectral_masking(
                audio, sample_rate, parameters, spectral_data, instrument_probs
            )
    
    async def _separate_with_spectral_masking(self, audio: np.ndarray,
                                            sample_rate: int,
                                            parameters: SeparationParameters,
                                            spectral_data: Dict[str, Any],
                                            instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using spectral masking techniques"""        try:
            stft_magnitude = spectral_data.get("stft_magnitude", np.array([]))
            stft_phase = spectral_data.get("stft_phase", np.array([]))
            
            if stft_magnitude.size == 0:
                # Compute STFT if not available
                stft = librosa.stft(audio, n_fft=parameters.frame_size, hop_length=parameters.hop_length)
                stft_magnitude = np.abs(stft)
                stft_phase = np.angle(stft)
            
            separated_tracks = {}
            
            for instrument in parameters.target_instruments:
                # Create instrument-specific mask
                mask = await self._create_instrument_mask(
                    stft_magnitude, instrument, spectral_data, sample_rate
                )
                
                # Apply mask
                masked_stft = stft_magnitude * mask * np.exp(1j * stft_phase)
                
                # Reconstruct audio
                track_audio = librosa.istft(masked_stft, hop_length=parameters.hop_length)
                
                # Ensure same length as original
                if len(track_audio) != len(audio):
                    if len(track_audio) > len(audio):
                        track_audio = track_audio[:len(audio)]
                    else:
                        padded = np.zeros(len(audio))
                        padded[:len(track_audio)] = track_audio
                        track_audio = padded
                
                # Calculate metrics
                confidence = instrument_probs.get(instrument, 0.3)
                quality_metrics = await self._calculate_track_quality(track_audio, audio)
                isolation_level = await self._calculate_isolation_level(track_audio, audio)
                
                separated_track = SeparatedTrack(
                    instrument_type=instrument,
                    audio_data=track_audio,
                    confidence_score=confidence,
                    spectral_mask=mask,
                    quality_metrics=quality_metrics,
                    isolation_level=isolation_level
                )
                
                separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in spectral masking separation: {e}")
            return {}
    
    async def _create_instrument_mask(self, magnitude: np.ndarray,
                                    instrument: InstrumentType,
                                    spectral_data: Dict[str, Any],
                                    sample_rate: int) -> np.ndarray:
        """Create spectral mask for specific instrument"""        try:
            freqs = spectral_data.get("frequency_bins", librosa.fft_frequencies(sr=sample_rate))
            mask = np.zeros_like(magnitude)
            
            # Get instrument profile
            profile = self.spectral_analyzer.instrument_profiles.get(instrument, {})
            
            if instrument == InstrumentType.VOCALS:
                # Vocal mask: emphasize formant regions
                formant_regions = profile.get("formant_regions", [(400, 800), (800, 1200)])
                for freq_low, freq_high in formant_regions:
                    freq_mask = (freqs >= freq_low) & (freqs <= freq_high)
                    mask[freq_mask, :] = 1.0
                
                # Harmonic enhancement
                harmonic_component = spectral_data.get("harmonic_component", magnitude)
                harmonic_ratio = np.abs(harmonic_component) / (magnitude + 1e-8)
                mask *= harmonic_ratio
                
            elif instrument == InstrumentType.DRUMS:
                # Drum mask: emphasize percussive content
                percussive_component = spectral_data.get("percussive_component", magnitude)
                percussive_ratio = np.abs(percussive_component) / (magnitude + 1e-8)
                mask = percussive_ratio
                
                # Emphasize transient regions
                onset_times = spectral_data.get("onset_times", [])
                for onset_time in onset_times:
                    onset_frame = int(onset_time * sample_rate / 512)  # Hop length
                    if onset_frame < mask.shape[1]:
                        mask[:, max(0, onset_frame-2):min(mask.shape[1], onset_frame+3)] *= 2.0
                
            elif instrument == InstrumentType.BASS:
                # Bass mask: low frequency emphasis
                freq_range = profile.get("frequency_range", (40, 350))
                freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
                mask[freq_mask, :] = 1.0
                
                # Harmonic emphasis for bass
                harmonic_component = spectral_data.get("harmonic_component", magnitude)
                harmonic_ratio = np.abs(harmonic_component) / (magnitude + 1e-8)
                mask[freq_mask, :] *= harmonic_ratio[freq_mask, :]
                
            elif instrument == InstrumentType.OTHER:
                # Residual mask: what's left after other instruments
                mask = np.ones_like(magnitude)
                
                # Subtract other instrument masks
                for other_instrument in [InstrumentType.VOCALS, InstrumentType.DRUMS, InstrumentType.BASS]:
                    if other_instrument != instrument:
                        other_mask = await self._create_instrument_mask(
                            magnitude, other_instrument, spectral_data, sample_rate
                        )
                        mask = mask - 0.7 * other_mask
                
                mask = np.maximum(mask, 0.1)  # Minimum mask value
            
            else:
                # Generic frequency range mask
                freq_range = profile.get("frequency_range", (200, 5000))
                freq_mask = (freqs >= freq_range[0]) & (freqs <= freq_range[1])
                mask[freq_mask, :] = 1.0
            
            # Smooth mask
            mask = await self._smooth_mask(mask)
            
            # Normalize mask
            mask = np.clip(mask, 0.0, 1.0)
            
            return mask
            
        except Exception as e:
            logger.error(f"Error creating instrument mask: {e}")
            return np.ones_like(magnitude) * 0.5
    
    async def _smooth_mask(self, mask: np.ndarray, sigma: float = 1.0) -> np.ndarray:
        """Apply smoothing to spectral mask"""        try:
            from scipy import ndimage
            return ndimage.gaussian_filter(mask, sigma=sigma)
        except ImportError:
            # Fallback: simple averaging
            return signal.convolve2d(mask, np.ones((3, 3))/9, mode='same', boundary='symm')
        except Exception as e:
            logger.error(f"Error smoothing mask: {e}")
            return mask
    
    async def _separate_harmonic_percussive(self, audio: np.ndarray,
                                          sample_rate: int,
                                          parameters: SeparationParameters,
                                          spectral_data: Dict[str, Any],
                                          instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using harmonic-percussive decomposition"""        try:
            # Get harmonic and percussive components
            harmonic_component = spectral_data.get("harmonic_component")
            percussive_component = spectral_data.get("percussive_component")
            
            if harmonic_component is None or percussive_component is None:
                stft = librosa.stft(audio)
                harmonic_component, percussive_component = librosa.decompose.hpss(stft)
            
            # Reconstruct audio
            harmonic_audio = librosa.istft(harmonic_component)
            percussive_audio = librosa.istft(percussive_component)
            
            separated_tracks = {}
            
            # Assign to instrument categories
            if InstrumentType.HARMONIC in parameters.target_instruments:
                quality_metrics = await self._calculate_track_quality(harmonic_audio, audio)
                isolated_level = await self._calculate_isolation_level(harmonic_audio, audio)
                
                separated_tracks[InstrumentType.HARMONIC] = SeparatedTrack(
                    instrument_type=InstrumentType.HARMONIC,
                    audio_data=harmonic_audio,
                    confidence_score=0.8,
                    spectral_mask=np.abs(harmonic_component) > np.max(np.abs(harmonic_component)) * 0.1,
                    quality_metrics=quality_metrics,
                    isolation_level=isolated_level
                )
            
            if InstrumentType.PERCUSSIVE in parameters.target_instruments:
                quality_metrics = await self._calculate_track_quality(percussive_audio, audio)
                isolated_level = await self._calculate_isolation_level(percussive_audio, audio)
                
                separated_tracks[InstrumentType.PERCUSSIVE] = SeparatedTrack(
                    instrument_type=InstrumentType.PERCUSSIVE,
                    audio_data=percussive_audio,
                    confidence_score=0.8,
                    spectral_mask=np.abs(percussive_component) > np.max(np.abs(percussive_component)) * 0.1,
                    quality_metrics=quality_metrics,
                    isolation_level=isolated_level
                )
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in harmonic-percussive separation: {e}")
            return {}
    
    async def _separate_with_nnf(self, audio: np.ndarray,
                               sample_rate: int,
                               parameters: SeparationParameters,
                               spectral_data: Dict[str, Any],
                               instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using Non-negative Matrix Factorization"""        try:
            # Compute magnitude spectrogram
            stft = librosa.stft(audio, n_fft=parameters.frame_size, hop_length=parameters.hop_length)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Apply NMF
            num_components = len(parameters.target_instruments)
            nmf = sklearn.decomposition.NMF(n_components=num_components, max_iter=parameters.num_iterations)
            W = nmf.fit_transform(magnitude)
            H = nmf.components_
            
            # Reconstruct sources
            separated_tracks = {}
            
            for i, instrument in enumerate(parameters.target_instruments):
                if i < num_components:
                    # Reconstruct magnitude for this component
                    component_magnitude = np.outer(W[:, i], H[i, :])
                    
                    # Create mask
                    mask = component_magnitude / (magnitude + 1e-8)
                    mask = np.clip(mask, 0.0, 1.0)
                    
                    # Apply mask and reconstruct
                    masked_stft = magnitude * mask * np.exp(1j * phase)
                    track_audio = librosa.istft(masked_stft, hop_length=parameters.hop_length)
                    
                    # Ensure same length
                    if len(track_audio) != len(audio):
                        if len(track_audio) > len(audio):
                            track_audio = track_audio[:len(audio)]
                        else:
                            padded = np.zeros(len(audio))
                            padded[:len(track_audio)] = track_audio
                            track_audio = padded
                    
                    # Calculate metrics
                    confidence = instrument_probs.get(instrument, 0.3)
                    quality_metrics = await self._calculate_track_quality(track_audio, audio)
                    isolation_level = await self._calculate_isolation_level(track_audio, audio)
                    
                    separated_track = SeparatedTrack(
                        instrument_type=instrument,
                        audio_data=track_audio,
                        confidence_score=confidence,
                        spectral_mask=mask,
                        quality_metrics=quality_metrics,
                        isolation_level=isolation_level
                    )
                    
                    separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in NMF separation: {e}")
            return {}
    
    async def _separate_with_ica(self, audio: np.ndarray,
                               sample_rate: int,
                               parameters: SeparationParameters,
                               spectral_data: Dict[str, Any],
                               instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using Independent Component Analysis"""        try:
            # ICA requires multiple channels
            if audio.ndim == 1:
                # Create artificial stereo by phase shifting
                audio_stereo = np.array([audio, np.roll(audio, len(audio)//100)])
            else:
                audio_stereo = audio
            
            # Apply ICA
            from sklearn.decomposition import FastICA
            
            num_components = min(len(parameters.target_instruments), audio_stereo.shape[0])
            ica = FastICA(n_components=num_components, max_iter=parameters.num_iterations)
            
            # Transpose for sklearn format
            components = ica.fit_transform(audio_stereo.T).T
            
            separated_tracks = {}
            
            for i, instrument in enumerate(parameters.target_instruments[:num_components]):
                track_audio = components[i]
                
                # Calculate metrics
                confidence = instrument_probs.get(instrument, 0.4)
                quality_metrics = await self._calculate_track_quality(track_audio, audio)
                isolation_level = await self._calculate_isolation_level(track_audio, audio)
                
                # Create simple mask
                track_stft = librosa.stft(track_audio)
                mask = np.abs(track_stft) > (np.max(np.abs(track_stft)) * 0.1)
                
                separated_track = SeparatedTrack(
                    instrument_type=instrument,
                    audio_data=track_audio,
                    confidence_score=confidence,
                    spectral_mask=mask,
                    quality_metrics=quality_metrics,
                    isolation_level=isolation_level
                )
                
                separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in ICA separation: {e}")
            return {}
    
    async def _separate_with_median_filtering(self, audio: np.ndarray,
                                            sample_rate: int,
                                            parameters: SeparationParameters,
                                            spectral_data: Dict[str, Any],
                                            instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using median filtering techniques"""        try:
            stft = librosa.stft(audio, n_fft=parameters.frame_size, hop_length=parameters.hop_length)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            separated_tracks = {}
            
            # Harmonic component (median filter across time)
            harmonic_magnitude = signal.medfilt2d(magnitude, kernel_size=(1, 17))
            harmonic_stft = harmonic_magnitude * np.exp(1j * phase)
            harmonic_audio = librosa.istft(harmonic_stft, hop_length=parameters.hop_length)
            
            # Percussive component (median filter across frequency)
            percussive_magnitude = signal.medfilt2d(magnitude, kernel_size=(17, 1))
            percussive_stft = percussive_magnitude * np.exp(1j * phase)
            percussive_audio = librosa.istft(percussive_stft, hop_length=parameters.hop_length)
            
            # Assign to instruments
            for instrument in parameters.target_instruments:
                if instrument in [InstrumentType.VOCALS, InstrumentType.GUITAR, InstrumentType.PIANO]:
                    track_audio = harmonic_audio
                    mask = harmonic_magnitude > (np.max(harmonic_magnitude) * 0.1)
                elif instrument in [InstrumentType.DRUMS, InstrumentType.PERCUSSION]:
                    track_audio = percussive_audio
                    mask = percussive_magnitude > (np.max(percussive_magnitude) * 0.1)
                else:
                    # Residual
                    track_audio = audio - harmonic_audio - percussive_audio
                    track_stft = librosa.stft(track_audio)
                    mask = np.abs(track_stft) > (np.max(np.abs(track_stft)) * 0.1)
                
                # Ensure same length
                if len(track_audio) != len(audio):
                    if len(track_audio) > len(audio):
                        track_audio = track_audio[:len(audio)]
                    else:
                        padded = np.zeros(len(audio))
                        padded[:len(track_audio)] = track_audio
                        track_audio = padded
                
                # Calculate metrics
                confidence = instrument_probs.get(instrument, 0.3)
                quality_metrics = await self._calculate_track_quality(track_audio, audio)
                isolation_level = await self._calculate_isolation_level(track_audio, audio)
                
                separated_track = SeparatedTrack(
                    instrument_type=instrument,
                    audio_data=track_audio,
                    confidence_score=confidence,
                    spectral_mask=mask,
                    quality_metrics=quality_metrics,
                    isolation_level=isolation_level
                )
                
                separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in median filtering separation: {e}")
            return {}
    
    async def _separate_with_repet(self, audio: np.ndarray,
                                 sample_rate: int,
                                 parameters: SeparationParameters,
                                 spectral_data: Dict[str, Any],
                                 instrument_probs: Dict[InstrumentType, float]) -> Dict[InstrumentType, SeparatedTrack]:
        """Separate using REpeating Pattern Extraction Technique (REPET)"""        try:
            # Compute STFT
            stft = librosa.stft(audio, n_fft=parameters.frame_size, hop_length=parameters.hop_length)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Find repeating period (simplified)
            # In practice, this would use autocorrelation or beat tracking
            beat_period = int(sample_rate * 0.5 / parameters.hop_length)  # Assume 120 BPM
            
            # Create repeating background model
            num_periods = magnitude.shape[1] // beat_period
            if num_periods > 1:
                # Reshape to periods
                reshaped = magnitude[:, :num_periods * beat_period].reshape(
                    magnitude.shape[0], num_periods, beat_period
                )
                
                # Take median across periods for background
                background_model = np.median(reshaped, axis=1)
                
                # Extend to full length
                background_full = np.tile(background_model, (1, magnitude.shape[1] // beat_period + 1))
                background_full = background_full[:, :magnitude.shape[1]]
                
                # Create mask for foreground
                foreground_mask = magnitude / (background_full + magnitude + 1e-8)
                background_mask = 1.0 - foreground_mask
                
            else:
                # Fallback: no repetition found
                background_mask = np.ones_like(magnitude) * 0.5
                foreground_mask = np.ones_like(magnitude) * 0.5
            
            # Reconstruct sources
            background_stft = magnitude * background_mask * np.exp(1j * phase)
            foreground_stft = magnitude * foreground_mask * np.exp(1j * phase)
            
            background_audio = librosa.istft(background_stft, hop_length=parameters.hop_length)
            foreground_audio = librosa.istft(foreground_stft, hop_length=parameters.hop_length)
            
            separated_tracks = {}
            
            # Assign based on target instruments
            for instrument in parameters.target_instruments:
                if instrument in [InstrumentType.DRUMS, InstrumentType.BASS]:
                    # Background (repeating)
                    track_audio = background_audio
                    mask = background_mask
                else:
                    # Foreground (non-repeating)
                    track_audio = foreground_audio
                    mask = foreground_mask
                
                # Ensure same length
                if len(track_audio) != len(audio):
                    if len(track_audio) > len(audio):
                        track_audio = track_audio[:len(audio)]
                    else:
                        padded = np.zeros(len(audio))
                        padded[:len(track_audio)] = track_audio
                        track_audio = padded
                
                # Calculate metrics
                confidence = instrument_probs.get(instrument, 0.4)
                quality_metrics = await self._calculate_track_quality(track_audio, audio)
                isolation_level = await self._calculate_isolation_level(track_audio, audio)
                
                separated_track = SeparatedTrack(
                    instrument_type=instrument,
                    audio_data=track_audio,
                    confidence_score=confidence,
                    spectral_mask=mask,
                    quality_metrics=quality_metrics,
                    isolation_level=isolation_level
                )
                
                separated_tracks[instrument] = separated_track
            
            return separated_tracks
            
        except Exception as e:
            logger.error(f"Error in REPET separation: {e}")
            return {}
    
    async def _calculate_track_quality(self, track_audio: np.ndarray, 
                                     original_audio: np.ndarray) -> Dict[str, float]:
        """Calculate quality metrics for separated track"""        try:
            quality_metrics = {}
            
            # Signal-to-artifact ratio (simplified)
            if len(track_audio) > 0 and len(original_audio) > 0:
                track_energy = np.sum(track_audio ** 2)
                total_energy = np.sum(original_audio ** 2)
                
                if total_energy > 0:
                    energy_ratio = track_energy / total_energy
                    quality_metrics["energy_ratio"] = min(1.0, energy_ratio)
                else:
                    quality_metrics["energy_ratio"] = 0.0
            else:
                quality_metrics["energy_ratio"] = 0.0
            
            # Dynamic range
            if len(track_audio) > 0:
                rms = np.sqrt(np.mean(track_audio ** 2))
                peak = np.max(np.abs(track_audio))
                
                if rms > 0:
                    dynamic_range = 20 * np.log10(peak / rms)
                    quality_metrics["dynamic_range"] = min(1.0, dynamic_range / 40.0)  # Normalize
                else:
                    quality_metrics["dynamic_range"] = 0.0
            else:
                quality_metrics["dynamic_range"] = 0.0
            
            # Spectral coherence
            if len(track_audio) > 1024:
                fft_track = np.fft.rfft(track_audio)
                spectral_coherence = np.sum(np.abs(fft_track)) / len(fft_track)
                quality_metrics["spectral_coherence"] = min(1.0, spectral_coherence)
            else:
                quality_metrics["spectral_coherence"] = 0.0
            
            # Overall quality
            quality_metrics["overall_quality"] = np.mean([
                quality_metrics["energy_ratio"],
                quality_metrics["dynamic_range"],
                quality_metrics["spectral_coherence"]
            ])
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error calculating track quality: {e}")
            return {"overall_quality": 0.0}
    
    async def _calculate_isolation_level(self, track_audio: np.ndarray,
                                       original_audio: np.ndarray) -> float:
        """Calculate how well the track is isolated from the mix"""        try:
            if len(track_audio) == 0 or len(original_audio) == 0:
                return 0.0
            
            # Cross-correlation to measure isolation
            if len(track_audio) == len(original_audio):
                correlation = np.corrcoef(track_audio, original_audio)[0, 1]
                if not np.isnan(correlation):
                    # Higher correlation means less isolation
                    isolation = 1.0 - abs(correlation)
                    return max(0.0, isolation)
            
            # Fallback: energy-based isolation
            track_energy = np.sum(track_audio ** 2)
            original_energy = np.sum(original_audio ** 2)
            
            if original_energy > 0:
                isolation = min(1.0, track_energy / original_energy)
            else:
                isolation = 0.0
            
            return isolation
            
        except Exception as e:
            logger.error(f"Error calculating isolation level: {e}")
            return 0.0
    
    async def _assess_separation_quality(self, original_audio: np.ndarray,
                                       separated_tracks: Dict[InstrumentType, SeparatedTrack],
                                       parameters: SeparationParameters) -> Dict[str, float]:
        """Assess overall separation quality"""        try:
            if not separated_tracks:
                return {"overall_quality": 0.0}
            
            quality_assessment = {}
            
            # Track quality scores
            track_qualities = [track.quality_metrics.get("overall_quality", 0.0) 
                             for track in separated_tracks.values()]
            quality_assessment["average_track_quality"] = np.mean(track_qualities)
            
            # Isolation scores
            isolation_scores = [track.isolation_level for track in separated_tracks.values()]
            quality_assessment["average_isolation"] = np.mean(isolation_scores)
            
            # Confidence scores
            confidence_scores = [track.confidence_score for track in separated_tracks.values()]
            quality_assessment["average_confidence"] = np.mean(confidence_scores)
            
            # Reconstruction quality (sum of tracks vs original)
            if len(original_audio) > 0:
                reconstructed = np.zeros_like(original_audio)
                for track in separated_tracks.values():
                    if len(track.audio_data) == len(original_audio):
                        reconstructed += track.audio_data
                
                # MSE between original and reconstruction
                mse = np.mean((original_audio - reconstructed) ** 2)
                original_energy = np.mean(original_audio ** 2)
                
                if original_energy > 0:
                    snr = 10 * np.log10(original_energy / (mse + 1e-8))
                    reconstruction_quality = min(1.0, max(0.0, (snr + 10) / 30.0))  # Normalize
                else:
                    reconstruction_quality = 0.0
                
                quality_assessment["reconstruction_quality"] = reconstruction_quality
            else:
                quality_assessment["reconstruction_quality"] = 0.0
            
            # Overall quality
            quality_assessment["overall_quality"] = np.mean([
                quality_assessment["average_track_quality"],
                quality_assessment["average_isolation"],
                quality_assessment["average_confidence"],
                quality_assessment["reconstruction_quality"]
            ])
            
            return quality_assessment
            
        except Exception as e:
            logger.error(f"Error assessing separation quality: {e}")
            return {"overall_quality": 0.0}
    
    def get_separation_statistics(self) -> Dict[str, Any]:
        """Get separation performance statistics"""        try:
            if not self.separation_history:
                return {"total_separations": 0}
            
            recent_history = self.separation_history[-25:]  # Last 25 separations
            
            return {
                "total_separations": len(self.separation_history),
                "recent_average_quality": np.mean([h["overall_quality"] for h in recent_history]),
                "method_distribution": {
                    method: sum(1 for h in recent_history if h["method"] == method)
                    for method in set(h["method"] for h in recent_history)
                },
                "quality_distribution": {
                    quality: sum(1 for h in recent_history if h["quality"] == quality)
                    for quality in set(h["quality"] for h in recent_history)
                },
                "average_tracks_separated": np.mean([h["num_tracks"] for h in recent_history]),
                "last_separation": recent_history[-1] if recent_history else None
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"total_separations": 0}

# Processing classes for export
AudioSourceSeparator = InstrumentSeparator
InstrumentIsolator = InstrumentSeparator
TrackSeparator = InstrumentSeparator

# Export classes
__all__ = [
    "InstrumentSeparator",
    "AudioSourceSeparator",
    "InstrumentIsolator", 
    "TrackSeparator",
    "InstrumentType",
    "SeparationMethod",
    "SeparationQuality",
    "SeparationParameters",
    "SeparatedTrack",
    "SeparationResult",
    "UNetSeparator",
    "ConvTasNet",
    "SpectralAnalyzer"
]