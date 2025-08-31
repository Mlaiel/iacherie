"""🎛️ Audio Mixer Processor - Professional Multi-Channel Mixing Engine

Advanced audio mixing with multiple channels, routing, buses, sends/returns,
automation, and professional mixing console capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import copy


class PanLaw(Enum):
    """Pan law types for stereo positioning"""    LINEAR = "linear"
    CONSTANT_POWER = "constant_power"
    MINUS_3DB = "minus_3db"
    MINUS_4_5DB = "minus_4_5db"
    MINUS_6DB = "minus_6db"


class ChannelType(Enum):
    """Audio channel types"""    MONO = "mono"
    STEREO = "stereo"
    SURROUND_5_1 = "surround_5_1"
    SURROUND_7_1 = "surround_7_1"


@dataclass
class ChannelSettings:
    """Settings for individual mixer channel"""    gain: float = 1.0
    pan: float = 0.0  # -1.0 (left) to 1.0 (right)
    mute: bool = False
    solo: bool = False
    high_cut_freq: Optional[float] = None
    low_cut_freq: Optional[float] = None
    eq_high: float = 1.0
    eq_mid: float = 1.0
    eq_low: float = 1.0
    send_levels: Dict[str, float] = None
    
    def __post_init__(self):
        if self.send_levels is None:
            self.send_levels = {}


class MixerChannel:
    """Individual mixer channel"""    
    def __init__(self, channel_id: str, channel_type: ChannelType = ChannelType.MONO):
        self.channel_id = channel_id
        self.channel_type = channel_type
        self.settings = ChannelSettings()
        self.audio_buffer = np.array([])
        self.peak_meter = 0.0
        self.rms_meter = 0.0
        
        # Processing history for automation
        self.gain_history = []
        self.pan_history = []
        
        # Initialize filters
        self._init_filters()
    
    def _init_filters(self):
        """Initialize channel filters"""        self.high_cut_filter = None
        self.low_cut_filter = None
        self.eq_filters = {
            'high': None,
            'mid': None,
            'low': None
        }
    
    def process_audio(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Process audio through channel"""        processed = audio_data.copy()
        
        # Apply filters
        processed = self._apply_filters(processed, sample_rate)
        
        # Apply EQ
        processed = self._apply_eq(processed)
        
        # Apply gain
        processed *= self.settings.gain
        
        # Update meters
        self._update_meters(processed)
        
        # Check mute
        if self.settings.mute:
            processed = np.zeros_like(processed)
        
        return processed
    
    def _apply_filters(self, audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
        """Apply high/low cut filters"""        processed = audio_data
        
        # High cut (low-pass) filter
        if self.settings.high_cut_freq is not None:
            from scipy import signal
            nyquist = sample_rate / 2
            high_cut_normalized = self.settings.high_cut_freq / nyquist
            if high_cut_normalized < 1.0:
                b, a = signal.butter(2, high_cut_normalized, 'lowpass')
                processed = signal.filtfilt(b, a, processed)
        
        # Low cut (high-pass) filter
        if self.settings.low_cut_freq is not None:
            from scipy import signal
            nyquist = sample_rate / 2
            low_cut_normalized = self.settings.low_cut_freq / nyquist
            if low_cut_normalized > 0.0:
                b, a = signal.butter(2, low_cut_normalized, 'highpass')
                processed = signal.filtfilt(b, a, processed)
        
        return processed
    
    def _apply_eq(self, audio_data: np.ndarray) -> np.ndarray:
        """Apply 3-band EQ"""        # Simple gain-based EQ (would be more sophisticated in practice)
        processed = audio_data
        
        # This is a simplified implementation
        # Real EQ would use proper filter banks
        eq_factor = (self.settings.eq_high + self.settings.eq_mid + 
                    self.settings.eq_low) / 3.0
        processed *= eq_factor
        
        return processed
    
    def _update_meters(self, audio_data: np.ndarray):
        """Update peak and RMS meters"""        if len(audio_data) > 0:
            self.peak_meter = float(np.max(np.abs(audio_data)))
            self.rms_meter = float(np.sqrt(np.mean(audio_data**2)))


class AudioMixerProcessor:
    """Professional audio mixer processor"""    
    def __init__(self, sample_rate: int = 44100):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Mixer configuration
        self.channels: Dict[str, MixerChannel] = {}
        self.buses: Dict[str, np.ndarray] = {}
        self.sends: Dict[str, Dict[str, float]] = {}  # send_name -> {channel_id: level}
        self.returns: Dict[str, np.ndarray] = {}
        
        # Master section
        self.master_gain = 1.0
        self.master_mute = False
        self.master_peak = 0.0
        self.master_rms = 0.0
        
        # Pan law
        self.pan_law = PanLaw.CONSTANT_POWER
        
        # Solo system
        self.solo_active = False
        self.soloed_channels = set()
        
        # Automation
        self.automation_enabled = True
        self.automation_data = {}
        
        self.logger.info("AudioMixerProcessor initialized")
    
    def add_channel(self, channel_id: str, channel_type: ChannelType = ChannelType.MONO) -> bool:
        """Add new mixer channel"""        try:
            if channel_id in self.channels:
                self.logger.warning(f"Channel {channel_id} already exists")
                return False
            
            self.channels[channel_id] = MixerChannel(channel_id, channel_type)
            
            # Initialize sends for this channel
            for send_name in self.sends:
                self.sends[send_name][channel_id] = 0.0
            
            self.logger.info(f"Added channel: {channel_id} ({channel_type.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add channel {channel_id}: {e}")
            return False
    
    def remove_channel(self, channel_id: str) -> bool:
        """Remove mixer channel"""        try:
            if channel_id not in self.channels:
                self.logger.warning(f"Channel {channel_id} not found")
                return False
            
            # Remove from solo if active
            self.soloed_channels.discard(channel_id)
            
            # Remove from sends
            for send_name in self.sends:
                self.sends[send_name].pop(channel_id, None)
            
            # Remove channel
            del self.channels[channel_id]
            
            self.logger.info(f"Removed channel: {channel_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove channel {channel_id}: {e}")
            return False
    
    def add_send(self, send_name: str) -> bool:
        """Add auxiliary send"""        try:
            if send_name in self.sends:
                self.logger.warning(f"Send {send_name} already exists")
                return False
            
            # Initialize send levels for all channels
            self.sends[send_name] = {ch_id: 0.0 for ch_id in self.channels}
            self.returns[send_name] = np.array([])
            
            self.logger.info(f"Added send: {send_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add send {send_name}: {e}")
            return False
    
    def set_channel_gain(self, channel_id: str, gain: float):
        """Set channel gain (0.0 to 2.0)"""        if channel_id in self.channels:
            gain = max(0.0, min(2.0, gain))
            self.channels[channel_id].settings.gain = gain
            
            # Record for automation
            if self.automation_enabled:
                self.channels[channel_id].gain_history.append(gain)
    
    def set_channel_pan(self, channel_id: str, pan: float):
        """Set channel pan (-1.0 to 1.0)"""        if channel_id in self.channels:
            pan = max(-1.0, min(1.0, pan))
            self.channels[channel_id].settings.pan = pan
            
            # Record for automation
            if self.automation_enabled:
                self.channels[channel_id].pan_history.append(pan)
    
    def set_channel_mute(self, channel_id: str, mute: bool):
        """Set channel mute"""        if channel_id in self.channels:
            self.channels[channel_id].settings.mute = mute
    
    def set_channel_solo(self, channel_id: str, solo: bool):
        """Set channel solo"""        if channel_id in self.channels:
            self.channels[channel_id].settings.solo = solo
            
            if solo:
                self.soloed_channels.add(channel_id)
            else:
                self.soloed_channels.discard(channel_id)
            
            self.solo_active = len(self.soloed_channels) > 0
    
    def set_send_level(self, channel_id: str, send_name: str, level: float):
        """Set send level for channel"""        if channel_id in self.channels and send_name in self.sends:
            level = max(0.0, min(1.0, level))
            self.sends[send_name][channel_id] = level
            self.channels[channel_id].settings.send_levels[send_name] = level
    
    def process_mix(self, channel_inputs: Dict[str, np.ndarray]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Process complete mix"""        try:
            if not channel_inputs:
                return np.array([]), {}
            
            # Determine output length
            max_length = max(len(audio) for audio in channel_inputs.values())
            
            # Initialize mix busses
            main_mix = np.zeros(max_length)
            send_mixes = {send_name: np.zeros(max_length) for send_name in self.sends}
            
            # Process each channel
            for channel_id, audio_data in channel_inputs.items():
                if channel_id not in self.channels:
                    continue
                
                channel = self.channels[channel_id]
                
                # Skip if muted and not monitoring
                if channel.settings.mute and not self.solo_active:
                    continue
                
                # Skip if solo is active and this channel is not soloed
                if self.solo_active and channel_id not in self.soloed_channels:
                    continue
                
                # Pad audio to match max length
                if len(audio_data) < max_length:
                    padded_audio = np.pad(audio_data, (0, max_length - len(audio_data)))
                else:
                    padded_audio = audio_data[:max_length]
                
                # Process through channel
                processed_audio = channel.process_audio(padded_audio, self.sample_rate)
                
                # Apply panning for main mix
                left_gain, right_gain = self._calculate_pan_gains(channel.settings.pan)
                
                # Add to main mix (assuming stereo output)
                if len(main_mix.shape) == 1:
                    # Convert to stereo
                    stereo_mix = np.zeros((max_length, 2))
                    stereo_mix[:, 0] = main_mix
                    stereo_mix[:, 1] = main_mix
                    main_mix = stereo_mix
                
                if len(main_mix.shape) == 2:
                    main_mix[:, 0] += processed_audio * left_gain
                    main_mix[:, 1] += processed_audio * right_gain
                else:
                    main_mix += processed_audio
                
                # Add to send mixes
                for send_name, send_mix in send_mixes.items():
                    send_level = self.sends[send_name].get(channel_id, 0.0)
                    if send_level > 0:
                        send_mix += processed_audio * send_level
            
            # Apply master gain
            main_mix *= self.master_gain
            
            # Apply master mute
            if self.master_mute:
                main_mix = np.zeros_like(main_mix)
            
            # Update master meters
            if len(main_mix) > 0:
                if len(main_mix.shape) == 2:
                    # Stereo - get max of both channels
                    self.master_peak = float(np.max(np.abs(main_mix)))
                    self.master_rms = float(np.sqrt(np.mean(main_mix**2)))
                else:
                    self.master_peak = float(np.max(np.abs(main_mix)))
                    self.master_rms = float(np.sqrt(np.mean(main_mix**2)))
            
            self.logger.debug("Mix processing completed")
            return main_mix, send_mixes
            
        except Exception as e:
            self.logger.error(f"Mix processing failed: {e}")
            return np.array([]), {}
    
    def _calculate_pan_gains(self, pan: float) -> Tuple[float, float]:
        """Calculate left/right gains based on pan position"""        # Normalize pan from -1,1 to 0,1
        pan_normalized = (pan + 1.0) / 2.0
        
        if self.pan_law == PanLaw.LINEAR:
            left_gain = 1.0 - pan_normalized
            right_gain = pan_normalized
            
        elif self.pan_law == PanLaw.CONSTANT_POWER:
            # Constant power panning
            left_gain = np.cos(pan_normalized * np.pi / 2)
            right_gain = np.sin(pan_normalized * np.pi / 2)
            
        elif self.pan_law == PanLaw.MINUS_3DB:
            # -3dB pan law
            left_gain = np.sqrt(1.0 - pan_normalized)
            right_gain = np.sqrt(pan_normalized)
            
        elif self.pan_law == PanLaw.MINUS_4_5DB:
            # -4.5dB pan law
            center_gain = np.sqrt(2) / 2  # -3dB
            if pan_normalized <= 0.5:
                left_gain = 1.0
                right_gain = pan_normalized * 2 * center_gain
            else:
                left_gain = (1.0 - pan_normalized) * 2 * center_gain
                right_gain = 1.0
                
        elif self.pan_law == PanLaw.MINUS_6DB:
            # -6dB pan law
            left_gain = 1.0 - pan_normalized
            right_gain = pan_normalized
            
        else:
            # Default to constant power
            left_gain = np.cos(pan_normalized * np.pi / 2)
            right_gain = np.sin(pan_normalized * np.pi / 2)
        
        return left_gain, right_gain
    
    def get_channel_meters(self, channel_id: str) -> Dict[str, float]:
        """Get channel meter readings"""        if channel_id not in self.channels:
            return {"peak": 0.0, "rms": 0.0}
        
        channel = self.channels[channel_id]
        return {
            "peak": channel.peak_meter,
            "rms": channel.rms_meter,
            "peak_db": 20 * np.log10(channel.peak_meter + 1e-10),
            "rms_db": 20 * np.log10(channel.rms_meter + 1e-10)
        }
    
    def get_master_meters(self) -> Dict[str, float]:
        """Get master meter readings"""        return {
            "peak": self.master_peak,
            "rms": self.master_rms,
            "peak_db": 20 * np.log10(self.master_peak + 1e-10),
            "rms_db": 20 * np.log10(self.master_rms + 1e-10)
        }
    
    def save_mix_snapshot(self) -> Dict[str, Any]:
        """Save current mixer state"""        snapshot = {
            "master_gain": self.master_gain,
            "master_mute": self.master_mute,
            "pan_law": self.pan_law.value,
            "channels": {},
            "sends": copy.deepcopy(self.sends)
        }
        
        for channel_id, channel in self.channels.items():
            snapshot["channels"][channel_id] = {
                "gain": channel.settings.gain,
                "pan": channel.settings.pan,
                "mute": channel.settings.mute,
                "solo": channel.settings.solo,
                "eq_high": channel.settings.eq_high,
                "eq_mid": channel.settings.eq_mid,
                "eq_low": channel.settings.eq_low,
                "send_levels": copy.deepcopy(channel.settings.send_levels)
            }
        
        return snapshot
    
    def load_mix_snapshot(self, snapshot: Dict[str, Any]) -> bool:
        """Load mixer state from snapshot"""        try:
            self.master_gain = snapshot.get("master_gain", 1.0)
            self.master_mute = snapshot.get("master_mute", False)
            
            # Load pan law
            pan_law_str = snapshot.get("pan_law", "constant_power")
            try:
                self.pan_law = PanLaw(pan_law_str)
            except ValueError:
                self.pan_law = PanLaw.CONSTANT_POWER
            
            # Load channel settings
            for channel_id, settings in snapshot.get("channels", {}).items():
                if channel_id in self.channels:
                    channel = self.channels[channel_id]
                    channel.settings.gain = settings.get("gain", 1.0)
                    channel.settings.pan = settings.get("pan", 0.0)
                    channel.settings.mute = settings.get("mute", False)
                    channel.settings.solo = settings.get("solo", False)
                    channel.settings.eq_high = settings.get("eq_high", 1.0)
                    channel.settings.eq_mid = settings.get("eq_mid", 1.0)
                    channel.settings.eq_low = settings.get("eq_low", 1.0)
                    channel.settings.send_levels = settings.get("send_levels", {})
            
            # Load sends
            self.sends.update(snapshot.get("sends", {}))
            
            # Update solo state
            self.soloed_channels = {ch_id for ch_id, ch in self.channels.items() 
                                  if ch.settings.solo}
            self.solo_active = len(self.soloed_channels) > 0
            
            self.logger.info("Mix snapshot loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load mix snapshot: {e}")
            return False
