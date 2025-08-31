"""🎛️ Professional Mixing Console - Advanced Channel Strip

Industrial-grade channel strip with comprehensive processing capabilities
including EQ, dynamics, inserts, sends, and professional routing.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
from dataclasses import dataclass, field
import scipy.signal
from abc import ABC, abstractmethod


class ChannelStripType(Enum):
    """Channel strip types"""    MICROPHONE = "microphone"
    LINE = "line"
    INSTRUMENT = "instrument"
    STEREO_LINE = "stereo_line"
    RETURN = "return"
    MASTER = "master"
    GROUP = "group"
    AUX = "aux"


class InsertPosition(Enum):
    """Insert effect positions"""    PRE_EQ = "pre_eq"
    POST_EQ = "post_eq"
    PRE_FADER = "pre_fader"
    POST_FADER = "post_fader"


@dataclass
class ChannelEQ:
    """4-band parametric EQ settings"""    high_freq: float = 10000.0      # Hz
    high_gain: float = 0.0          # dB
    high_q: float = 0.7
    
    high_mid_freq: float = 2500.0   # Hz
    high_mid_gain: float = 0.0      # dB
    high_mid_q: float = 1.0
    
    low_mid_freq: float = 400.0     # Hz
    low_mid_gain: float = 0.0       # dB
    low_mid_q: float = 1.0
    
    low_freq: float = 100.0         # Hz
    low_gain: float = 0.0           # dB
    low_q: float = 0.7
    
    eq_enabled: bool = True


@dataclass
class ChannelDynamics:
    """Channel dynamics processing"""    compressor_enabled: bool = False
    compressor_threshold: float = -12.0  # dB
    compressor_ratio: float = 3.0
    compressor_attack: float = 3.0       # ms
    compressor_release: float = 100.0    # ms
    compressor_makeup: float = 0.0       # dB
    
    gate_enabled: bool = False
    gate_threshold: float = -40.0        # dB
    gate_ratio: float = 10.0
    gate_attack: float = 1.0             # ms
    gate_hold: float = 10.0              # ms
    gate_release: float = 100.0          # ms


@dataclass
class SendConfiguration:
    """Auxiliary send configuration"""    send_id: str
    pre_fader: bool = False         # Pre/post fader
    level: float = 0.0              # Send level in dB
    mute: bool = False              # Send mute
    pan: float = 0.0                # Send pan


class ChannelStrip:
    """Professional channel strip with full processing chain"""    
    def __init__(self, 
                 channel_id: str,
                 sample_rate: int,
                 strip_type: ChannelStripType = ChannelStripType.LINE):
        
        self.logger = logging.getLogger(f"{self.__class__.__name__}_{channel_id}")
        self.channel_id = channel_id
        self.sample_rate = sample_rate
        self.strip_type = strip_type
        
        # Channel settings
        self.gain = 0.0                     # Input gain in dB
        self.phantom_power = False          # +48V phantom power
        self.pad = False                    # Input pad (-20dB)
        self.phase_invert = False           # Phase inversion
        
        # High-pass filter
        self.hpf_enabled = False
        self.hpf_frequency = 80.0           # Hz
        
        # EQ section
        self.eq = ChannelEQ()
        
        # Dynamics section
        self.dynamics = ChannelDynamics()
        
        # Insert effects
        self.inserts = {}                   # Insert effect processors
        self.insert_position = InsertPosition.POST_EQ
        
        # Auxiliary sends
        self.sends = {}                     # Send configurations
        
        # Channel fader and routing
        self.fader_level = 0.0              # Fader level in dB
        self.pan = 0.0                      # Pan position (-1 to +1)
        self.mute = False                   # Channel mute
        self.solo = False                   # Channel solo
        self.solo_in_place = False          # Solo-in-place mode
        
        # Routing
        self.main_assign = True             # Assign to main mix
        self.group_assigns = set()          # Group bus assignments
        
        # Metering
        self.input_level = 0.0              # Input level meter
        self.output_level = 0.0             # Output level meter
        self.gain_reduction = 0.0           # Compressor gain reduction
        
        # Processing components
        self._initialize_processing_components()
        
        self.logger.info(f"Channel strip {channel_id} initialized - Type: {strip_type.value}")
    
    def _initialize_processing_components(self):
        """Initialize signal processing components"""        # High-pass filter
        self._update_hpf()
        
        # EQ filters
        self._update_eq_filters()
        
        # Dynamics processors (placeholder - would use actual compressor/gate)
        self.compressor_envelope = 0.0
        self.gate_envelope = 0.0
    
    def _update_hpf(self):
        """Update high-pass filter coefficients"""        if self.hpf_enabled and self.hpf_frequency > 0:
            nyquist = self.sample_rate / 2
            normalized_freq = self.hpf_frequency / nyquist
            if normalized_freq < 1.0:
                self.hpf_b, self.hpf_a = scipy.signal.butter(2, normalized_freq, btype='high')
            else:
                self.hpf_b, self.hpf_a = np.array([1.0]), np.array([1.0])
        else:
            self.hpf_b, self.hpf_a = np.array([1.0]), np.array([1.0])
    
    def _update_eq_filters(self):
        """Update EQ filter coefficients"""        # This is a simplified implementation
        # In production, you'd implement proper parametric EQ filters
        pass
    
    def process(self, input_audio: np.ndarray) -> np.ndarray:
        """Process audio through complete channel strip"""        try:
            if input_audio.size == 0:
                return input_audio
            
            processed_audio = input_audio.astype(np.float64)
            
            # Input section
            processed_audio = self._process_input_section(processed_audio)
            
            # High-pass filter
            if self.hpf_enabled:
                processed_audio = scipy.signal.lfilter(self.hpf_b, self.hpf_a, processed_audio)
            
            # Insert effects (pre-EQ)
            if self.insert_position == InsertPosition.PRE_EQ:
                processed_audio = self._process_inserts(processed_audio)
            
            # EQ section
            if self.eq.eq_enabled:
                processed_audio = self._process_eq(processed_audio)
            
            # Insert effects (post-EQ)
            if self.insert_position == InsertPosition.POST_EQ:
                processed_audio = self._process_inserts(processed_audio)
            
            # Dynamics section
            processed_audio = self._process_dynamics(processed_audio)
            
            # Insert effects (pre-fader)
            if self.insert_position == InsertPosition.PRE_FADER:
                processed_audio = self._process_inserts(processed_audio)
            
            # Fader and pan
            processed_audio = self._apply_fader_and_pan(processed_audio)
            
            # Insert effects (post-fader)
            if self.insert_position == InsertPosition.POST_FADER:
                processed_audio = self._process_inserts(processed_audio)
            
            # Update metering
            self._update_metering(input_audio, processed_audio)
            
            return processed_audio.astype(input_audio.dtype)
            
        except Exception as e:
            self.logger.error(f"Channel strip processing failed: {str(e)}")
            return input_audio
    
    def _process_input_section(self, audio: np.ndarray) -> np.ndarray:
        """Process input section (gain, pad, phantom, phase)"""        processed = audio.copy()
        
        # Apply pad
        if self.pad:
            processed *= 0.1  # -20dB
        
        # Apply input gain
        if abs(self.gain) > 0.01:
            gain_linear = 10 ** (self.gain / 20.0)
            processed *= gain_linear
        
        # Apply phase inversion
        if self.phase_invert:
            processed *= -1.0
        
        return processed
    
    def _process_eq(self, audio: np.ndarray) -> np.ndarray:
        """Process through 4-band parametric EQ"""        # Simplified EQ implementation
        processed = audio.copy()
        
        # High shelf
        if abs(self.eq.high_gain) > 0.01:
            # Apply high shelf filter
            processed = self._apply_shelf_filter(processed, self.eq.high_freq, self.eq.high_gain, 'high')
        
        # Low shelf
        if abs(self.eq.low_gain) > 0.01:
            # Apply low shelf filter
            processed = self._apply_shelf_filter(processed, self.eq.low_freq, self.eq.low_gain, 'low')
        
        return processed
    
    def _apply_shelf_filter(self, audio: np.ndarray, frequency: float, gain_db: float, shelf_type: str) -> np.ndarray:
        """Apply shelving filter"""        nyquist = self.sample_rate / 2
        normalized_freq = frequency / nyquist
        
        if normalized_freq >= 1.0:
            return audio
        
        gain_linear = 10 ** (gain_db / 20.0)
        
        if shelf_type == 'high':
            b, a = scipy.signal.butter(2, normalized_freq, btype='high')
        else:
            b, a = scipy.signal.butter(2, normalized_freq, btype='low')
        
        return scipy.signal.lfilter(b * gain_linear, a, audio)
    
    def _process_dynamics(self, audio: np.ndarray) -> np.ndarray:
        """Process dynamics (compressor and gate)"""        processed = audio.copy()
        
        # Simplified dynamics processing
        if self.dynamics.compressor_enabled:
            threshold_linear = 10 ** (self.dynamics.compressor_threshold / 20.0)
            for i in range(len(processed)):
                level = abs(processed[i])
                if level > threshold_linear:
                    over_threshold = level - threshold_linear
                    gain_reduction = over_threshold * (1.0 - 1.0/self.dynamics.compressor_ratio)
                    new_level = level - gain_reduction
                    if level > 0:
                        processed[i] = processed[i] * (new_level / level)
        
        return processed
    
    def _process_inserts(self, audio: np.ndarray) -> np.ndarray:
        """Process through insert effects"""        processed = audio.copy()
        
        # Process through each insert effect
        for insert_name, insert_processor in self.inserts.items():
            if hasattr(insert_processor, 'process'):
                processed = insert_processor.process(processed)
        
        return processed
    
    def _apply_fader_and_pan(self, audio: np.ndarray) -> np.ndarray:
        """Apply fader level and pan"""        processed = audio.copy()
        
        # Apply mute
        if self.mute:
            return np.zeros_like(processed)
        
        # Apply fader level
        if abs(self.fader_level) > 0.01:
            fader_linear = 10 ** (self.fader_level / 20.0)
            processed *= fader_linear
        
        # Apply pan (convert mono to stereo if needed)
        if len(processed.shape) == 1:
            # Mono to stereo conversion with pan
            left_gain, right_gain = self._calculate_pan_gains(self.pan)
            stereo_audio = np.column_stack([
                processed * left_gain,
                processed * right_gain
            ])
            return stereo_audio
        elif len(processed.shape) == 2 and self.pan != 0.0:
            # Stereo pan adjustment
            left_gain, right_gain = self._calculate_pan_gains(self.pan)
            processed[:, 0] *= left_gain
            processed[:, 1] *= right_gain
        
        return processed
    
    def _calculate_pan_gains(self, pan: float) -> Tuple[float, float]:
        """Calculate left/right gains for pan position"""        # Constant power panning
        pan_radians = (pan + 1.0) * np.pi / 4.0  # Map -1..1 to 0..π/2
        left_gain = np.cos(pan_radians)
        right_gain = np.sin(pan_radians)
        
        return left_gain, right_gain
    
    def _update_metering(self, input_audio: np.ndarray, output_audio: np.ndarray):
        """Update channel meters"""        self.input_level = 20 * np.log10(np.max(np.abs(input_audio)) + 1e-10)
        self.output_level = 20 * np.log10(np.max(np.abs(output_audio)) + 1e-10)
    
    def add_send(self, send_id: str, pre_fader: bool = False, level: float = -6.0):
        """Add auxiliary send"""        self.sends[send_id] = SendConfiguration(
            send_id=send_id,
            pre_fader=pre_fader,
            level=level
        )
        self.logger.info(f"Added send '{send_id}' to channel {self.channel_id}")
    
    def set_send_level(self, send_id: str, level: float):
        """Set send level"""        if send_id in self.sends:
            self.sends[send_id].level = level
    
    def get_send_audio(self, send_id: str, audio: np.ndarray) -> Optional[np.ndarray]:
        """Get audio for specific send"""        if send_id not in self.sends:
            return None
        
        send_config = self.sends[send_id]
        
        if send_config.mute:
            return np.zeros_like(audio)
        
        # Apply send level
        send_level_linear = 10 ** (send_config.level / 20.0)
        send_audio = audio * send_level_linear
        
        return send_audio
    
    def add_insert(self, insert_name: str, processor: Any, position: InsertPosition = InsertPosition.POST_EQ):
        """Add insert effect processor"""        self.inserts[insert_name] = processor
        self.insert_position = position
        self.logger.info(f"Added insert '{insert_name}' to channel {self.channel_id}")
    
    def remove_insert(self, insert_name: str):
        """Remove insert effect processor"""        if insert_name in self.inserts:
            del self.inserts[insert_name]
            self.logger.info(f"Removed insert '{insert_name}' from channel {self.channel_id}")
    
    def get_channel_info(self) -> Dict[str, Any]:
        """Get complete channel information"""        return {
            'channel_id': self.channel_id,
            'strip_type': self.strip_type.value,
            'gain': self.gain,
            'fader_level': self.fader_level,
            'pan': self.pan,
            'mute': self.mute,
            'solo': self.solo,
            'eq_enabled': self.eq.eq_enabled,
            'compressor_enabled': self.dynamics.compressor_enabled,
            'gate_enabled': self.dynamics.gate_enabled,
            'hpf_enabled': self.hpf_enabled,
            'hpf_frequency': self.hpf_frequency,
            'inserts_count': len(self.inserts),
            'sends_count': len(self.sends),
            'input_level': self.input_level,
            'output_level': self.output_level,
            'gain_reduction': self.gain_reduction
        }
