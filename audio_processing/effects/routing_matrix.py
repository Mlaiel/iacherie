"""
🔀 Professional Audio Routing Matrix

Industrial-grade audio routing system with flexible signal flow,
bus management, and professional console routing capabilities.

Created by: Fahed Mlaiel (mlaiel@live.de)
© 2025 Fahed Mlaiel. All rights reserved.
"""

import numpy as np
import logging
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod


class BusType(Enum):
    """Audio bus types"""
    MAIN_MIX = "main_mix"           # Main stereo mix
    GROUP = "group"                 # Group/subgroup bus
    AUX_SEND = "aux_send"          # Auxiliary send bus
    AUX_RETURN = "aux_return"      # Auxiliary return bus
    MONITOR = "monitor"            # Monitor/cue bus
    RECORD = "record"              # Recording bus
    MATRIX = "matrix"              # Matrix output


class RoutingMode(Enum):
    """Routing operation modes"""
    NORMAL = "normal"              # Normal operation
    PFL = "pfl"                    # Pre-fader listen
    AFL = "afl"                    # After-fader listen
    SOLO_IN_PLACE = "solo_in_place"  # Solo-in-place


@dataclass
class BusConfiguration:
    """Bus configuration settings"""
    bus_id: str
    bus_type: BusType
    channel_count: int = 2         # Mono=1, Stereo=2, etc.
    master_level: float = 0.0      # Master level in dB
    master_mute: bool = False      # Master mute
    insert_sends: List[str] = field(default_factory=list)
    routing_destinations: Set[str] = field(default_factory=set)
    eq_enabled: bool = False       # Bus EQ
    compressor_enabled: bool = False  # Bus compression


class AudioRoutingMatrix:
    """Professional audio routing matrix"""
    
    def __init__(self, sample_rate: int):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.sample_rate = sample_rate
        
        # Bus management
        self.buses: Dict[str, BusConfiguration] = {}
        self.bus_audio: Dict[str, np.ndarray] = {}
        
        # Routing connections
        self.routing_matrix: Dict[str, Set[str]] = {}  # source -> destinations
        self.routing_gains: Dict[Tuple[str, str], float] = {}  # (source, dest) -> gain
        
        # Solo/mute system
        self.solo_channels: Set[str] = set()
        self.mute_channels: Set[str] = set()
        self.routing_mode = RoutingMode.NORMAL
        self.pfl_bus_active = False
        self.afl_bus_active = False
        
        # Monitoring
        self.monitor_source = "main_mix"
        self.monitor_level = 0.0
        self.dim_level = -15.0         # Dim attenuation in dB
        self.dim_active = False
        
        # Talkback
        self.talkback_active = False
        self.talkback_level = -6.0
        self.talkback_destinations: Set[str] = set()
        
        # Initialize standard buses
        self._create_standard_buses()
        
        self.logger.info("Audio routing matrix initialized")
    
    def _create_standard_buses(self):
        """Create standard audio buses"""
        # Main mix bus
        self.create_bus("main_mix", BusType.MAIN_MIX, channel_count=2)
        
        # Monitor bus
        self.create_bus("monitor", BusType.MONITOR, channel_count=2)
        
        # PFL/AFL buses
        self.create_bus("pfl", BusType.MONITOR, channel_count=2)
        self.create_bus("afl", BusType.MONITOR, channel_count=2)
        
        # Create default group buses
        for i in range(1, 9):  # 8 group buses
            self.create_bus(f"group_{i}", BusType.GROUP, channel_count=2)
        
        # Create auxiliary sends
        for i in range(1, 7):  # 6 aux sends
            self.create_bus(f"aux_send_{i}", BusType.AUX_SEND, channel_count=2)
            self.create_bus(f"aux_return_{i}", BusType.AUX_RETURN, channel_count=2)
    
    def create_bus(self, bus_id: str, bus_type: BusType, channel_count: int = 2) -> bool:
        """Create new audio bus"""
        try:
            if bus_id in self.buses:
                self.logger.warning(f"Bus '{bus_id}' already exists")
                return False
            
            bus_config = BusConfiguration(
                bus_id=bus_id,
                bus_type=bus_type,
                channel_count=channel_count
            )
            
            self.buses[bus_id] = bus_config
            self.routing_matrix[bus_id] = set()
            
            self.logger.info(f"Created bus '{bus_id}' - Type: {bus_type.value}, Channels: {channel_count}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create bus '{bus_id}': {str(e)}")
            return False
    
    def delete_bus(self, bus_id: str) -> bool:
        """Delete audio bus"""
        try:
            if bus_id not in self.buses:
                self.logger.warning(f"Bus '{bus_id}' does not exist")
                return False
            
            # Remove all routing connections
            self._disconnect_all_from_bus(bus_id)
            
            # Remove bus
            del self.buses[bus_id]
            if bus_id in self.routing_matrix:
                del self.routing_matrix[bus_id]
            if bus_id in self.bus_audio:
                del self.bus_audio[bus_id]
            
            self.logger.info(f"Deleted bus '{bus_id}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete bus '{bus_id}': {str(e)}")
            return False
    
    def connect(self, source_id: str, destination_id: str, gain_db: float = 0.0) -> bool:
        """Connect source to destination with optional gain"""
        try:
            if source_id not in self.routing_matrix:
                self.routing_matrix[source_id] = set()
            
            if destination_id not in self.buses:
                self.logger.warning(f"Destination bus '{destination_id}' does not exist")
                return False
            
            self.routing_matrix[source_id].add(destination_id)
            self.routing_gains[(source_id, destination_id)] = gain_db
            
            self.logger.debug(f"Connected '{source_id}' -> '{destination_id}' (gain: {gain_db}dB)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect '{source_id}' -> '{destination_id}': {str(e)}")
            return False
    
    def disconnect(self, source_id: str, destination_id: str) -> bool:
        """Disconnect source from destination"""
        try:
            if source_id in self.routing_matrix:
                self.routing_matrix[source_id].discard(destination_id)
            
            if (source_id, destination_id) in self.routing_gains:
                del self.routing_gains[(source_id, destination_id)]
            
            self.logger.debug(f"Disconnected '{source_id}' -> '{destination_id}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect '{source_id}' -> '{destination_id}': {str(e)}")
            return False
    
    def _disconnect_all_from_bus(self, bus_id: str):
        """Disconnect all sources from a bus"""
        for source_id in list(self.routing_matrix.keys()):
            if bus_id in self.routing_matrix[source_id]:
                self.disconnect(source_id, bus_id)
    
    def set_routing_gain(self, source_id: str, destination_id: str, gain_db: float):
        """Set routing gain for connection"""
        if (source_id, destination_id) in self.routing_gains:
            self.routing_gains[(source_id, destination_id)] = gain_db
            self.logger.debug(f"Set routing gain '{source_id}' -> '{destination_id}': {gain_db}dB")
    
    def route_audio(self, source_id: str, audio_data: np.ndarray) -> Dict[str, np.ndarray]:
        """Route audio from source to connected destinations"""
        routed_audio = {}
        
        if source_id not in self.routing_matrix:
            return routed_audio
        
        try:
            # Handle solo system
            if self.solo_channels and source_id not in self.solo_channels:
                # Source is not soloed, mute it
                audio_data = np.zeros_like(audio_data)
            elif source_id in self.mute_channels:
                # Source is muted
                audio_data = np.zeros_like(audio_data)
            
            # Route to each destination
            for destination_id in self.routing_matrix[source_id]:
                if destination_id not in self.buses:
                    continue
                
                destination_bus = self.buses[destination_id]
                
                # Skip if destination is muted
                if destination_bus.master_mute:
                    continue
                
                # Calculate routing gain
                routing_gain_db = self.routing_gains.get((source_id, destination_id), 0.0)
                master_gain_db = destination_bus.master_level
                total_gain_db = routing_gain_db + master_gain_db
                
                if abs(total_gain_db) > 0.01:
                    gain_linear = 10 ** (total_gain_db / 20.0)
                    routed_audio_data = audio_data * gain_linear
                else:
                    routed_audio_data = audio_data.copy()
                
                # Format audio for destination bus
                routed_audio_data = self._format_audio_for_bus(routed_audio_data, destination_bus)
                
                routed_audio[destination_id] = routed_audio_data
            
            return routed_audio
            
        except Exception as e:
            self.logger.error(f"Failed to route audio from '{source_id}': {str(e)}")
            return {}
    
    def _format_audio_for_bus(self, audio_data: np.ndarray, bus_config: BusConfiguration) -> np.ndarray:
        """Format audio data for destination bus channel configuration"""
        try:
            if bus_config.channel_count == 1:
                # Convert to mono
                if len(audio_data.shape) == 2:
                    return np.mean(audio_data, axis=1)
                else:
                    return audio_data
            
            elif bus_config.channel_count == 2:
                # Convert to stereo
                if len(audio_data.shape) == 1:
                    return np.column_stack([audio_data, audio_data])
                else:
                    return audio_data
            
            else:
                # Multi-channel (future implementation)
                return audio_data
            
        except Exception as e:
            self.logger.error(f"Failed to format audio for bus: {str(e)}")
            return audio_data
    
    def mix_bus_inputs(self, bus_id: str, input_audio_dict: Dict[str, np.ndarray]) -> np.ndarray:
        """Mix multiple audio inputs for a bus"""
        if not input_audio_dict:
            return np.array([])
        
        try:
            bus_config = self.buses.get(bus_id)
            if not bus_config:
                return np.array([])
            
            # Get first audio to determine shape
            first_audio = next(iter(input_audio_dict.values()))
            mixed_audio = np.zeros_like(first_audio)
            
            # Sum all inputs
            for source_id, audio_data in input_audio_dict.items():
                if audio_data.shape == mixed_audio.shape:
                    mixed_audio += audio_data
                else:
                    # Format mismatch, try to fix
                    formatted_audio = self._format_audio_for_bus(audio_data, bus_config)
                    if formatted_audio.shape == mixed_audio.shape:
                        mixed_audio += formatted_audio
            
            # Store mixed audio for bus
            self.bus_audio[bus_id] = mixed_audio
            
            return mixed_audio
            
        except Exception as e:
            self.logger.error(f"Failed to mix bus inputs for '{bus_id}': {str(e)}")
            return np.array([])
    
    def set_solo(self, source_id: str, solo_state: bool):
        """Set solo state for source"""
        if solo_state:
            self.solo_channels.add(source_id)
        else:
            self.solo_channels.discard(source_id)
        
        self.logger.debug(f"Set solo for '{source_id}': {solo_state}")
    
    def set_mute(self, source_id: str, mute_state: bool):
        """Set mute state for source"""
        if mute_state:
            self.mute_channels.add(source_id)
        else:
            self.mute_channels.discard(source_id)
        
        self.logger.debug(f"Set mute for '{source_id}': {mute_state}")
    
    def clear_all_solos(self):
        """Clear all solo states"""
        self.solo_channels.clear()
        self.logger.info("Cleared all solos")
    
    def clear_all_mutes(self):
        """Clear all mute states"""
        self.mute_channels.clear()
        self.logger.info("Cleared all mutes")
    
    def set_monitor_source(self, source_id: str):
        """Set monitor source"""
        if source_id in self.buses:
            self.monitor_source = source_id
            self.logger.info(f"Set monitor source to '{source_id}'")
        else:
            self.logger.warning(f"Monitor source '{source_id}' does not exist")
    
    def set_monitor_level(self, level_db: float):
        """Set monitor level"""
        self.monitor_level = level_db
        self.logger.debug(f"Set monitor level to {level_db}dB")
    
    def set_dim(self, dim_active: bool):
        """Set monitor dim state"""
        self.dim_active = dim_active
        self.logger.debug(f"Set dim: {dim_active}")
    
    def get_monitor_audio(self) -> Optional[np.ndarray]:
        """Get current monitor audio"""
        if self.monitor_source not in self.bus_audio:
            return None
        
        monitor_audio = self.bus_audio[self.monitor_source].copy()
        
        # Apply monitor level
        if abs(self.monitor_level) > 0.01:
            monitor_gain = 10 ** (self.monitor_level / 20.0)
            monitor_audio *= monitor_gain
        
        # Apply dim
        if self.dim_active:
            dim_gain = 10 ** (self.dim_level / 20.0)
            monitor_audio *= dim_gain
        
        return monitor_audio
    
    def activate_talkback(self, active: bool):
        """Activate/deactivate talkback"""
        self.talkback_active = active
        self.logger.info(f"Talkback {'activated' if active else 'deactivated'}")
    
    def set_talkback_destinations(self, destinations: Set[str]):
        """Set talkback destination buses"""
        self.talkback_destinations = destinations
        self.logger.info(f"Set talkback destinations: {destinations}")
    
    def route_talkback(self, talkback_audio: np.ndarray) -> Dict[str, np.ndarray]:
        """Route talkback audio to destinations"""
        if not self.talkback_active or not self.talkback_destinations:
            return {}
        
        talkback_gain = 10 ** (self.talkback_level / 20.0)
        routed_talkback = {}
        
        for dest_id in self.talkback_destinations:
            if dest_id in self.buses:
                routed_talkback[dest_id] = talkback_audio * talkback_gain
        
        return routed_talkback
    
    def get_routing_info(self) -> Dict[str, Any]:
        """Get complete routing information"""
        return {
            'buses': {bus_id: {
                'type': bus_config.bus_type.value,
                'channels': bus_config.channel_count,
                'master_level': bus_config.master_level,
                'master_mute': bus_config.master_mute
            } for bus_id, bus_config in self.buses.items()},
            
            'connections': {
                source_id: list(destinations) 
                for source_id, destinations in self.routing_matrix.items()
            },
            
            'gains': {
                f"{source}->{dest}": gain 
                for (source, dest), gain in self.routing_gains.items()
            },
            
            'solo_channels': list(self.solo_channels),
            'mute_channels': list(self.mute_channels),
            'monitor_source': self.monitor_source,
            'monitor_level': self.monitor_level,
            'dim_active': self.dim_active,
            'talkback_active': self.talkback_active,
            'talkback_destinations': list(self.talkback_destinations)
        }
    
    def get_bus_levels(self) -> Dict[str, float]:
        """Get current levels for all buses"""
        levels = {}
        
        for bus_id, audio_data in self.bus_audio.items():
            if audio_data.size > 0:
                level_db = 20 * np.log10(np.max(np.abs(audio_data)) + 1e-10)
                levels[bus_id] = level_db
            else:
                levels[bus_id] = -70.0  # Silence
        
        return levels
