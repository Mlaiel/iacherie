"""
 Effects Module - Professional Audio Effects Processing

Complete audio effects suite with professional-grade processors for music production,
audio post-production, and content creation workflows.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.

=============================================================================
CONFIDENTIAL - IA INFLUENCER AGENT PLATFORM
=============================================================================
Expert Team Attribution:
- Lead Dev IA: Fahed Mlaiel (mlaiel@live.de) 
- Backend Senior: Professional Architecture Team
- ML Engineer: Advanced Audio Processing Algorithms
- DBA: Audio Metadata & Performance Optimization  
- Security: Content Protection & Copyright Management
- Microservices: Scalable Audio Processing Pipeline
- Audio Engineer: Professional DSP Implementation
- DevOps: Production Deployment & Monitoring
- IA Prompt Engineer: Intelligent Audio Enhancement

Business Logic Flow:
Creator Upload → Multi-format Audio → AI Analysis → Protection → Enhancement → 
Effects Processing → Quality Control → Distribution → Analytics

WARNING: This software contains proprietary algorithms and trade secrets.
Unauthorized reproduction, distribution, or reverse engineering is strictly
prohibited and may result in severe legal penalties under international
copyright law.
=============================================================================
"""

from .equalizer_processor import EqualizerProcessor, EQType, FilterType
from .compressor_processor import (
    CompressorProcessor, CompressorType, DetectionMode, KneeType,
    CompressorPreset, MultibandCrossover, SideChainProcessor
)
from .envelope_follower import EnvelopeFollower
from .reverb_processor import (
    ReverbProcessor, ReverbType, RoomSize, EarlyReflectionPattern,
    ReverbParameters, EarlyReflection, ConvolutionReverb
)
from .chorus_processor import ChorusProcessor, FlangerProcessor, ModulationType
from .distortion_processor import DistortionProcessor, DistortionType
from .noise_reduction_processor import NoiseReductionProcessor, NoiseReductionType
from .pitch_shifter_processor import PitchShifterProcessor, PitchShiftAlgorithm
from .time_stretcher_processor import TimeStretcherProcessor, TimeStretchAlgorithm
from .audio_mixer_processor import AudioMixerProcessor, MixerChannel, ChannelType, PanLaw
from .mastering_processor import (
    MasteringProcessor, MasteringMode, LimiterType, StereoMode,
    DistributionFormat, LUFSMeter, StereoProcessor, MultibandLimiter
)
from .channel_strip import (
    ChannelStrip, ChannelStripType, InsertPosition, ChannelEQ,
    ChannelDynamics, SendConfiguration
)
from .routing_matrix import (
    AudioRoutingMatrix, BusType, RoutingMode, BusConfiguration
)

__all__ = [
    # EQ Processing
    'EqualizerProcessor',
    'EQType',
    'FilterType',
    
    # Dynamics Processing
    'CompressorProcessor',
    'CompressorType', 
    'DetectionMode',
    'KneeType',
    'CompressorPreset',
    'MultibandCrossover',
    'SideChainProcessor',
    'EnvelopeFollower',
    
    # Spatial Effects
    'ReverbProcessor',
    'ReverbType',
    'RoomSize',
    'EarlyReflectionPattern',
    'ReverbParameters',
    'EarlyReflection',
    'ConvolutionReverb',
    
    # Modulation Effects
    'ChorusProcessor',
    'FlangerProcessor',
    'ModulationType',
    
    # Saturation & Distortion
    'DistortionProcessor',
    'DistortionType',
    
    # Restoration & Cleanup
    'NoiseReductionProcessor',
    'NoiseReductionType',
    
    # Pitch & Time Processing
    'PitchShifterProcessor',
    'PitchShiftAlgorithm',
    'TimeStretcherProcessor', 
    'TimeStretchAlgorithm',
    
    # Mixing & Routing
    'AudioMixerProcessor',
    'MixerChannel',
    'ChannelType',
    'PanLaw',
    'ChannelStrip',
    'ChannelStripType',
    'InsertPosition',
    'ChannelEQ',
    'ChannelDynamics',
    'SendConfiguration',
    'AudioRoutingMatrix',
    'BusType',
    'RoutingMode',
    'BusConfiguration',
    
    # Mastering & Finalization
    'MasteringProcessor',
    'MasteringMode',
    'LimiterType',
    'StereoMode',
    'DistributionFormat',
    'LUFSMeter',
    'StereoProcessor',
    'MultibandLimiter'
]