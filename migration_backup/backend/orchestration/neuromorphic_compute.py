"""
Neuromorphic Computing Module - Brain-Inspired Computing

Advanced neuromorphic processing system with spike-based neural networks,
synaptic plasticity, and brain-inspired computing architectures.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import numpy as np
import math
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import json
import threading
from collections import defaultdict, deque
import weakref

logger = logging.getLogger(__name__)


class NeuronModel(Enum):
    """Neuromorphic neuron models"""
    LEAKY_INTEGRATE_FIRE = "leaky_integrate_fire"
    IZHIKEVICH = "izhikevich"
    HODGKIN_HUXLEY = "hodgkin_huxley"
    ADAPTIVE_EXPONENTIAL = "adaptive_exponential"
    SPIKING_NEURAL_NETWORK = "spiking_neural_network"


class PlasticityType(Enum):
    """Synaptic plasticity types"""
    STDP = "spike_timing_dependent_plasticity"
    LTP = "long_term_potentiation"
    LTD = "long_term_depression"
    HOMEOSTATIC = "homeostatic_plasticity"
    METAPLASTICITY = "metaplasticity"


class ProcessingMode(Enum):
    """Neuromorphic processing modes"""
    EVENT_DRIVEN = "event_driven"
    TIME_STEPPED = "time_stepped"
    HYBRID = "hybrid"
    ASYNCHRONOUS = "asynchronous"


@dataclass
class NeuromorphicConfig:
    """Configuration for neuromorphic computing"""
    neuron_model: NeuronModel = NeuronModel.LEAKY_INTEGRATE_FIRE
    plasticity_type: PlasticityType = PlasticityType.STDP
    processing_mode: ProcessingMode = ProcessingMode.EVENT_DRIVEN
    time_step_ms: float = 1.0
    membrane_time_constant_ms: float = 20.0
    refractory_period_ms: float = 2.0
    threshold_voltage: float = 1.0
    reset_voltage: float = 0.0
    synaptic_delay_ms: float = 1.0
    learning_rate: float = 0.01
    enable_plasticity: bool = True
    enable_adaptation: bool = True
    noise_level: float = 0.01
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "neuron_model": self.neuron_model.value,
            "plasticity_type": self.plasticity_type.value,
            "processing_mode": self.processing_mode.value,
            "time_step_ms": self.time_step_ms,
            "membrane_time_constant_ms": self.membrane_time_constant_ms,
            "refractory_period_ms": self.refractory_period_ms,
            "threshold_voltage": self.threshold_voltage,
            "reset_voltage": self.reset_voltage,
            "synaptic_delay_ms": self.synaptic_delay_ms,
            "learning_rate": self.learning_rate,
            "enable_plasticity": self.enable_plasticity,
            "enable_adaptation": self.enable_adaptation,
            "noise_level": self.noise_level
        }


@dataclass
class SpikeEvent:
    """Represents a spike event"""
    neuron_id: str
    timestamp: float
    amplitude: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "neuron_id": self.neuron_id,
            "timestamp": self.timestamp,
            "amplitude": self.amplitude,
            "metadata": self.metadata
        }


@dataclass
class Synapse:
    """Neuromorphic synapse"""
    pre_neuron_id: str
    post_neuron_id: str
    weight: float
    delay_ms: float
    last_update_time: float = 0.0
    spike_history: deque = field(default_factory=lambda: deque(maxlen=1000))
    
    def update_weight(self, delta_weight: float, max_weight: float = 10.0):
        """Update synaptic weight"""
        self.weight = np.clip(self.weight + delta_weight, -max_weight, max_weight)
        self.last_update_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pre_neuron_id": self.pre_neuron_id,
            "post_neuron_id": self.post_neuron_id,
            "weight": self.weight,
            "delay_ms": self.delay_ms,
            "last_update_time": self.last_update_time,
            "spike_count": len(self.spike_history)
        }


class SpikingNeuron:
    """Spiking neuron implementation"""
    
    def __init__(self, neuron_id: str, config: NeuromorphicConfig):
        self.neuron_id = neuron_id
        self.config = config
        
        # Neuron state
        self.membrane_potential = config.reset_voltage
        self.threshold = config.threshold_voltage
        self.last_spike_time = -float('inf')
        self.refractory_until = 0.0
        
        # Spike history
        self.spike_times: deque = deque(maxlen=1000)
        self.input_history: deque = deque(maxlen=1000)
        
        # Adaptation variables
        self.adaptation_current = 0.0
        self.adaptation_conductance = 0.0
        
        logger.debug(f"Created spiking neuron {neuron_id}")
    
    def integrate(self, input_current: float, dt: float) -> Optional[SpikeEvent]:
        """Integrate neuron dynamics"""
        current_time = time.time()
        
        # Check refractory period
        if current_time < self.refractory_until:
            return None
        
        # Apply neuron model
        if self.config.neuron_model == NeuronModel.LEAKY_INTEGRATE_FIRE:
            return self._lif_dynamics(input_current, dt, current_time)
        elif self.config.neuron_model == NeuronModel.IZHIKEVICH:
            return self._izhikevich_dynamics(input_current, dt, current_time)
        else:
            # Default to LIF
            return self._lif_dynamics(input_current, dt, current_time)
    
    def _lif_dynamics(self, input_current: float, dt: float, current_time: float) -> Optional[SpikeEvent]:
        """Leaky Integrate-and-Fire neuron dynamics"""
        tau_m = self.config.membrane_time_constant_ms
        
        # Add noise
        noise = np.random.normal(0, self.config.noise_level)
        total_current = input_current + noise
        
        # Update membrane potential
        decay = np.exp(-dt / tau_m)
        self.membrane_potential = (
            self.membrane_potential * decay + 
            total_current * (1 - decay)
        )
        
        # Store input history
        self.input_history.append({
            'time': current_time,
            'current': input_current,
            'membrane_potential': self.membrane_potential
        })
        
        # Check for spike
        if self.membrane_potential >= self.threshold:
            # Generate spike
            spike = SpikeEvent(
                neuron_id=self.neuron_id,
                timestamp=current_time,
                amplitude=1.0,
                metadata={'membrane_potential': self.membrane_potential}
            )
            
            # Reset neuron
            self.membrane_potential = self.config.reset_voltage
            self.last_spike_time = current_time
            self.refractory_until = current_time + self.config.refractory_period_ms / 1000.0
            
            # Store spike time
            self.spike_times.append(current_time)
            
            return spike
        
        return None
    
    def _izhikevich_dynamics(self, input_current: float, dt: float, current_time: float) -> Optional[SpikeEvent]:
        """Izhikevich neuron model dynamics"""
        # Izhikevich model parameters
        a, b, c, d = 0.02, 0.2, -65, 8
        
        v = self.membrane_potential
        u = self.adaptation_current
        
        # Izhikevich equations
        dv = 0.04 * v * v + 5 * v + 140 - u + input_current
        du = a * (b * v - u)
        
        # Update state
        self.membrane_potential += dv * dt
        self.adaptation_current += du * dt
        
        # Check for spike
        if self.membrane_potential >= 30:  # Izhikevich spike threshold
            spike = SpikeEvent(
                neuron_id=self.neuron_id,
                timestamp=current_time,
                amplitude=1.0,
                metadata={'membrane_potential': self.membrane_potential}
            )
            
            # Reset
            self.membrane_potential = c
            self.adaptation_current += d
            self.last_spike_time = current_time
            self.spike_times.append(current_time)
            
            return spike
        
        return None
    
    def get_firing_rate(self, window_ms: float = 1000.0) -> float:
        """Calculate firing rate over time window"""
        current_time = time.time()
        window_start = current_time - window_ms / 1000.0
        
        recent_spikes = [t for t in self.spike_times if t >= window_start]
        return len(recent_spikes) / (window_ms / 1000.0)
    
    def get_neuron_state(self) -> Dict[str, Any]:
        """Get neuron state information"""
        return {
            'neuron_id': self.neuron_id,
            'membrane_potential': self.membrane_potential,
            'threshold': self.threshold,
            'last_spike_time': self.last_spike_time,
            'refractory_until': self.refractory_until,
            'spike_count': len(self.spike_times),
            'firing_rate_hz': self.get_firing_rate(),
            'adaptation_current': self.adaptation_current
        }


class NeuralPlasticity:
    """Synaptic plasticity implementation"""
    
    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.plasticity_rules = {
            PlasticityType.STDP: self._stdp_rule,
            PlasticityType.LTP: self._ltp_rule,
            PlasticityType.LTD: self._ltd_rule,
            PlasticityType.HOMEOSTATIC: self._homeostatic_rule
        }
    
    async def update_synapse(self, synapse: Synapse, pre_spike_time: float, 
                           post_spike_time: float) -> float:
        """Update synapse based on plasticity rules"""
        if not self.config.enable_plasticity:
            return 0.0
        
        plasticity_rule = self.plasticity_rules.get(
            self.config.plasticity_type,
            self._stdp_rule
        )
        
        return await plasticity_rule(synapse, pre_spike_time, post_spike_time)
    
    async def _stdp_rule(self, synapse: Synapse, pre_spike_time: float, 
                        post_spike_time: float) -> float:
        """Spike-Timing Dependent Plasticity"""
        dt = post_spike_time - pre_spike_time
        
        if abs(dt) > 0.1:  # 100ms window
            return 0.0
        
        # STDP parameters
        tau_plus = 0.02  # 20ms
        tau_minus = 0.02  # 20ms
        A_plus = 0.01
        A_minus = 0.01
        
        if dt > 0:  # Pre before post (LTP)
            delta_w = A_plus * np.exp(-dt / tau_plus)
        else:  # Post before pre (LTD)
            delta_w = -A_minus * np.exp(dt / tau_minus)
        
        delta_w *= self.config.learning_rate
        synapse.update_weight(delta_w)
        
        return delta_w
    
    async def _ltp_rule(self, synapse: Synapse, pre_spike_time: float, 
                       post_spike_time: float) -> float:
        """Long-Term Potentiation"""
        dt = abs(post_spike_time - pre_spike_time)
        
        if dt < 0.05:  # Coincident spikes within 50ms
            delta_w = self.config.learning_rate * 0.1
            synapse.update_weight(delta_w)
            return delta_w
        
        return 0.0
    
    async def _ltd_rule(self, synapse: Synapse, pre_spike_time: float, 
                       post_spike_time: float) -> float:
        """Long-Term Depression"""
        dt = abs(post_spike_time - pre_spike_time)
        
        if dt > 0.05 and dt < 0.2:  # Decorrelated spikes
            delta_w = -self.config.learning_rate * 0.05
            synapse.update_weight(delta_w)
            return delta_w
        
        return 0.0
    
    async def _homeostatic_rule(self, synapse: Synapse, pre_spike_time: float, 
                               post_spike_time: float) -> float:
        """Homeostatic plasticity"""
        # Simple homeostatic scaling
        target_firing_rate = 10.0  # Hz
        current_rate = len(synapse.spike_history) / 1.0  # Approximate rate
        
        if current_rate > target_firing_rate:
            delta_w = -self.config.learning_rate * 0.01
        elif current_rate < target_firing_rate:
            delta_w = self.config.learning_rate * 0.01
        else:
            delta_w = 0.0
        
        synapse.update_weight(delta_w)
        return delta_w


class SynapticComputing:
    """Synaptic computing and connectivity management"""
    
    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.synapses: Dict[Tuple[str, str], Synapse] = {}
        self.connectivity_matrix: Dict[str, List[str]] = defaultdict(list)
        self.plasticity_engine = NeuralPlasticity(config)
        self._lock = threading.RLock()
    
    def create_synapse(self, pre_neuron_id: str, post_neuron_id: str, 
                      initial_weight: float = 0.5, delay_ms: float = None) -> Synapse:
        """Create new synapse"""
        delay = delay_ms or self.config.synaptic_delay_ms
        
        synapse = Synapse(
            pre_neuron_id=pre_neuron_id,
            post_neuron_id=post_neuron_id,
            weight=initial_weight,
            delay_ms=delay
        )
        
        with self._lock:
            self.synapses[(pre_neuron_id, post_neuron_id)] = synapse
            self.connectivity_matrix[pre_neuron_id].append(post_neuron_id)
        
        logger.debug(f"Created synapse {pre_neuron_id} -> {post_neuron_id}")
        return synapse
    
    def remove_synapse(self, pre_neuron_id: str, post_neuron_id: str) -> bool:
        """Remove synapse"""
        with self._lock:
            synapse_key = (pre_neuron_id, post_neuron_id)
            if synapse_key in self.synapses:
                del self.synapses[synapse_key]
                self.connectivity_matrix[pre_neuron_id].remove(post_neuron_id)
                return True
        return False
    
    def get_postsynaptic_neurons(self, pre_neuron_id: str) -> List[str]:
        """Get list of postsynaptic neurons"""
        with self._lock:
            return self.connectivity_matrix[pre_neuron_id].copy()
    
    async def propagate_spike(self, spike_event: SpikeEvent) -> List[Tuple[str, float]]:
        """Propagate spike through synaptic connections"""
        postsynaptic_inputs = []
        
        with self._lock:
            post_neurons = self.connectivity_matrix.get(spike_event.neuron_id, [])
        
        for post_neuron_id in post_neurons:
            synapse_key = (spike_event.neuron_id, post_neuron_id)
            synapse = self.synapses.get(synapse_key)
            
            if synapse:
                # Calculate delayed input
                delayed_time = spike_event.timestamp + synapse.delay_ms / 1000.0
                synaptic_input = spike_event.amplitude * synapse.weight
                
                postsynaptic_inputs.append((post_neuron_id, synaptic_input))
                
                # Store spike in synapse history
                synapse.spike_history.append({
                    'pre_spike_time': spike_event.timestamp,
                    'weight': synapse.weight
                })
        
        return postsynaptic_inputs
    
    async def update_synapses(self, pre_spike_events: List[SpikeEvent], 
                            post_spike_events: List[SpikeEvent]):
        """Update all synapses based on spike events"""
        for pre_spike in pre_spike_events:
            for post_spike in post_spike_events:
                synapse_key = (pre_spike.neuron_id, post_spike.neuron_id)
                synapse = self.synapses.get(synapse_key)
                
                if synapse:
                    await self.plasticity_engine.update_synapse(
                        synapse, pre_spike.timestamp, post_spike.timestamp
                    )
    
    def get_connectivity_stats(self) -> Dict[str, Any]:
        """Get connectivity statistics"""
        with self._lock:
            total_synapses = len(self.synapses)
            neurons_with_outputs = len([k for k, v in self.connectivity_matrix.items() if v])
            
            weights = [s.weight for s in self.synapses.values()]
            
            return {
                'total_synapses': total_synapses,
                'neurons_with_outputs': neurons_with_outputs,
                'average_weight': np.mean(weights) if weights else 0.0,
                'weight_std': np.std(weights) if weights else 0.0,
                'max_weight': np.max(weights) if weights else 0.0,
                'min_weight': np.min(weights) if weights else 0.0
            }


class SpikeNetworkOrchestrator:
    """Orchestrator for spike-based neural networks"""
    
    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.neurons: Dict[str, SpikingNeuron] = {}
        self.synaptic_computer = SynapticComputing(config)
        self.spike_buffer: deque = deque(maxlen=10000)
        self.is_running = False
        self.simulation_time = 0.0
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("SpikeNetworkOrchestrator initialized")
    
    def add_neuron(self, neuron_id: str) -> SpikingNeuron:
        """Add neuron to network"""
        if neuron_id in self.neurons:
            raise ValueError(f"Neuron {neuron_id} already exists")
        
        neuron = SpikingNeuron(neuron_id, self.config)
        self.neurons[neuron_id] = neuron
        
        logger.debug(f"Added neuron {neuron_id} to network")
        return neuron
    
    def remove_neuron(self, neuron_id: str) -> bool:
        """Remove neuron from network"""
        if neuron_id not in self.neurons:
            return False
        
        # Remove all synapses involving this neuron
        synapses_to_remove = []
        for (pre_id, post_id) in self.synaptic_computer.synapses.keys():
            if pre_id == neuron_id or post_id == neuron_id:
                synapses_to_remove.append((pre_id, post_id))
        
        for pre_id, post_id in synapses_to_remove:
            self.synaptic_computer.remove_synapse(pre_id, post_id)
        
        del self.neurons[neuron_id]
        return True
    
    def connect_neurons(self, pre_neuron_id: str, post_neuron_id: str, 
                       weight: float = 0.5, delay_ms: float = None) -> Synapse:
        """Connect two neurons with a synapse"""
        if pre_neuron_id not in self.neurons or post_neuron_id not in self.neurons:
            raise ValueError("Both neurons must exist in the network")
        
        return self.synaptic_computer.create_synapse(
            pre_neuron_id, post_neuron_id, weight, delay_ms
        )
    
    async def simulate_step(self, dt: float, external_inputs: Dict[str, float] = None) -> List[SpikeEvent]:
        """Simulate one time step"""
        external_inputs = external_inputs or {}
        spike_events = []
        
        # Simulate each neuron
        simulation_tasks = []
        for neuron_id, neuron in self.neurons.items():
            input_current = external_inputs.get(neuron_id, 0.0)
            
            # Add synaptic inputs
            # (This would be calculated from previous spike propagation)
            
            task = asyncio.get_event_loop().run_in_executor(
                self._executor,
                neuron.integrate,
                input_current,
                dt
            )
            simulation_tasks.append((neuron_id, task))
        
        # Collect spike events
        for neuron_id, task in simulation_tasks:
            try:
                spike = await task
                if spike:
                    spike_events.append(spike)
                    self.spike_buffer.append(spike)
            except Exception as e:
                logger.error(f"Simulation error for neuron {neuron_id}: {e}")
        
        # Propagate spikes through synapses
        for spike in spike_events:
            await self.synaptic_computer.propagate_spike(spike)
        
        # Update synapses with plasticity
        if len(spike_events) > 1:
            await self.synaptic_computer.update_synapses(spike_events, spike_events)
        
        self.simulation_time += dt
        return spike_events
    
    async def run_simulation(self, duration_ms: float, dt: float = None):
        """Run network simulation for specified duration"""
        dt = dt or self.config.time_step_ms / 1000.0
        steps = int(duration_ms / (dt * 1000))
        
        self.is_running = True
        logger.info(f"Starting simulation for {duration_ms}ms ({steps} steps)")
        
        try:
            for step in range(steps):
                spike_events = await self.simulate_step(dt)
                
                if step % 100 == 0:  # Log every 100 steps
                    logger.debug(f"Step {step}/{steps}, spikes: {len(spike_events)}")
                
                if not self.is_running:
                    break
        
        finally:
            self.is_running = False
        
        logger.info("Simulation completed")
    
    def stop_simulation(self):
        """Stop running simulation"""
        self.is_running = False
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get comprehensive network statistics"""
        neuron_states = {
            neuron_id: neuron.get_neuron_state()
            for neuron_id, neuron in self.neurons.items()
        }
        
        connectivity_stats = self.synaptic_computer.get_connectivity_stats()
        
        # Calculate network activity
        recent_spikes = [spike for spike in self.spike_buffer 
                        if spike.timestamp > self.simulation_time - 1.0]
        
        return {
            'network_config': self.config.to_dict(),
            'total_neurons': len(self.neurons),
            'total_synapses': connectivity_stats['total_synapses'],
            'simulation_time': self.simulation_time,
            'is_running': self.is_running,
            'recent_spike_count': len(recent_spikes),
            'network_firing_rate': len(recent_spikes) / max(len(self.neurons), 1),
            'connectivity_stats': connectivity_stats,
            'neuron_states': neuron_states
        }


class BrainInspiredCompute:
    """Brain-inspired computing algorithms and patterns"""
    
    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.memory_networks: Dict[str, Any] = {}
        self.attention_mechanisms: Dict[str, Any] = {}
        self.pattern_recognizers: Dict[str, Any] = {}
    
    async def create_memory_network(self, network_id: str, 
                                  capacity: int = 1000) -> Dict[str, Any]:
        """Create brain-inspired memory network"""
        memory_network = {
            'network_id': network_id,
            'capacity': capacity,
            'stored_patterns': {},
            'pattern_count': 0,
            'retrieval_threshold': 0.8,
            'created_at': datetime.utcnow()
        }
        
        self.memory_networks[network_id] = memory_network
        logger.info(f"Created memory network {network_id} with capacity {capacity}")
        
        return memory_network
    
    async def store_pattern(self, network_id: str, pattern_id: str, 
                          pattern_data: np.ndarray) -> bool:
        """Store pattern in memory network"""
        if network_id not in self.memory_networks:
            return False
        
        memory_network = self.memory_networks[network_id]
        
        if memory_network['pattern_count'] >= memory_network['capacity']:
            # Implement forgetting mechanism
            await self._forget_oldest_pattern(network_id)
        
        # Store pattern with associative encoding
        encoded_pattern = await self._encode_pattern(pattern_data)
        
        memory_network['stored_patterns'][pattern_id] = {
            'pattern_data': pattern_data,
            'encoded_pattern': encoded_pattern,
            'storage_time': datetime.utcnow(),
            'access_count': 0,
            'last_access': datetime.utcnow()
        }
        
        memory_network['pattern_count'] += 1
        
        logger.debug(f"Stored pattern {pattern_id} in memory network {network_id}")
        return True
    
    async def retrieve_pattern(self, network_id: str, query_pattern: np.ndarray) -> Optional[str]:
        """Retrieve pattern from memory network"""
        if network_id not in self.memory_networks:
            return None
        
        memory_network = self.memory_networks[network_id]
        query_encoded = await self._encode_pattern(query_pattern)
        
        best_match = None
        best_similarity = 0.0
        
        for pattern_id, pattern_info in memory_network['stored_patterns'].items():
            similarity = await self._calculate_similarity(
                query_encoded, 
                pattern_info['encoded_pattern']
            )
            
            if similarity > best_similarity and similarity >= memory_network['retrieval_threshold']:
                best_similarity = similarity
                best_match = pattern_id
        
        if best_match:
            # Update access statistics
            memory_network['stored_patterns'][best_match]['access_count'] += 1
            memory_network['stored_patterns'][best_match]['last_access'] = datetime.utcnow()
            
            logger.debug(f"Retrieved pattern {best_match} with similarity {best_similarity:.3f}")
        
        return best_match
    
    async def create_attention_mechanism(self, mechanism_id: str, 
                                       focus_dimensions: int = 128) -> Dict[str, Any]:
        """Create brain-inspired attention mechanism"""
        attention_mechanism = {
            'mechanism_id': mechanism_id,
            'focus_dimensions': focus_dimensions,
            'attention_weights': np.ones(focus_dimensions),
            'attention_history': deque(maxlen=1000),
            'focus_threshold': 0.5,
            'created_at': datetime.utcnow()
        }
        
        self.attention_mechanisms[mechanism_id] = attention_mechanism
        logger.info(f"Created attention mechanism {mechanism_id}")
        
        return attention_mechanism
    
    async def apply_attention(self, mechanism_id: str, input_data: np.ndarray) -> np.ndarray:
        """Apply attention mechanism to input data"""
        if mechanism_id not in self.attention_mechanisms:
            return input_data
        
        attention_mechanism = self.attention_mechanisms[mechanism_id]
        attention_weights = attention_mechanism['attention_weights']
        
        # Apply attention weights
        attended_data = input_data * attention_weights[:len(input_data)]
        
        # Update attention history
        attention_strength = np.mean(attention_weights)
        attention_mechanism['attention_history'].append({
            'timestamp': datetime.utcnow(),
            'attention_strength': attention_strength,
            'input_norm': np.linalg.norm(input_data)
        })
        
        # Adaptive attention (simplified)
        if attention_strength < attention_mechanism['focus_threshold']:
            # Increase attention on high-activation regions
            high_activation_mask = input_data > np.mean(input_data)
            attention_mechanism['attention_weights'][high_activation_mask] *= 1.1
            attention_mechanism['attention_weights'] = np.clip(
                attention_mechanism['attention_weights'], 0.1, 2.0
            )
        
        return attended_data
    
    async def _encode_pattern(self, pattern_data: np.ndarray) -> np.ndarray:
        """Encode pattern for storage (simplified sparse coding)"""
        # Simple sparse coding simulation
        threshold = np.percentile(np.abs(pattern_data), 90)
        sparse_pattern = np.where(np.abs(pattern_data) > threshold, pattern_data, 0)
        return sparse_pattern
    
    async def _calculate_similarity(self, pattern1: np.ndarray, pattern2: np.ndarray) -> float:
        """Calculate similarity between patterns"""
        # Cosine similarity
        dot_product = np.dot(pattern1.flatten(), pattern2.flatten())
        norm1 = np.linalg.norm(pattern1)
        norm2 = np.linalg.norm(pattern2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    async def _forget_oldest_pattern(self, network_id: str):
        """Forget oldest pattern in memory network"""
        memory_network = self.memory_networks[network_id]
        
        if not memory_network['stored_patterns']:
            return
        
        # Find oldest pattern
        oldest_pattern = min(
            memory_network['stored_patterns'].items(),
            key=lambda x: x[1]['storage_time']
        )
        
        pattern_id = oldest_pattern[0]
        del memory_network['stored_patterns'][pattern_id]
        memory_network['pattern_count'] -= 1
        
        logger.debug(f"Forgot oldest pattern {pattern_id} from memory network {network_id}")


class NeuromorphicProcessor:
    """Main neuromorphic processor orchestrating all components"""
    
    def __init__(self, config: NeuromorphicConfig):
        self.config = config
        self.spike_orchestrator = SpikeNetworkOrchestrator(config)
        self.brain_computer = BrainInspiredCompute(config)
        self.processing_stats = {
            'total_computations': 0,
            'total_spikes_processed': 0,
            'average_latency_ms': 0.0,
            'start_time': datetime.utcnow()
        }
        
        logger.info("NeuromorphicProcessor initialized")
    
    async def process_input(self, input_data: np.ndarray, 
                          processing_duration_ms: float = 100.0) -> Dict[str, Any]:
        """Process input through neuromorphic computation"""
        start_time = time.time()
        
        # Convert input to spike patterns
        spike_pattern = await self._encode_input_to_spikes(input_data)
        
        # Apply brain-inspired attention if available
        if self.brain_computer.attention_mechanisms:
            mechanism_id = list(self.brain_computer.attention_mechanisms.keys())[0]
            input_data = await self.brain_computer.apply_attention(mechanism_id, input_data)
        
        # Create temporary input neurons
        input_neuron_ids = []
        for i in range(len(input_data)):
            neuron_id = f"input_{i}"
            self.spike_orchestrator.add_neuron(neuron_id)
            input_neuron_ids.append(neuron_id)
        
        # Create processing network
        processing_neuron_ids = []
        for i in range(min(32, len(input_data) * 2)):  # Adaptive size
            neuron_id = f"processing_{i}"
            self.spike_orchestrator.add_neuron(neuron_id)
            processing_neuron_ids.append(neuron_id)
        
        # Connect input to processing neurons
        for input_id in input_neuron_ids:
            for proc_id in processing_neuron_ids:
                if np.random.random() < 0.3:  # Sparse connectivity
                    weight = np.random.uniform(0.1, 1.0)
                    self.spike_orchestrator.connect_neurons(input_id, proc_id, weight)
        
        # Run neuromorphic simulation
        await self.spike_orchestrator.run_simulation(processing_duration_ms)
        
        # Collect results
        network_stats = self.spike_orchestrator.get_network_stats()
        
        # Clean up temporary neurons
        for neuron_id in input_neuron_ids + processing_neuron_ids:
            self.spike_orchestrator.remove_neuron(neuron_id)
        
        # Update processing statistics
        processing_time = (time.time() - start_time) * 1000  # Convert to ms
        self.processing_stats['total_computations'] += 1
        self.processing_stats['total_spikes_processed'] += network_stats['recent_spike_count']
        self.processing_stats['average_latency_ms'] = (
            (self.processing_stats['average_latency_ms'] * (self.processing_stats['total_computations'] - 1) + 
             processing_time) / self.processing_stats['total_computations']
        )
        
        result = {
            'input_shape': input_data.shape,
            'processing_time_ms': processing_time,
            'spike_activity': network_stats['recent_spike_count'],
            'network_firing_rate': network_stats['network_firing_rate'],
            'neuromorphic_output': self._extract_output_patterns(network_stats),
            'computation_metadata': {
                'config': self.config.to_dict(),
                'network_stats': network_stats
            }
        }
        
        logger.info(f"Neuromorphic processing completed in {processing_time:.2f}ms "
                   f"with {network_stats['recent_spike_count']} spikes")
        
        return result
    
    async def _encode_input_to_spikes(self, input_data: np.ndarray) -> List[float]:
        """Encode input data to spike timing patterns"""
        # Rate coding: higher values = higher spike frequency
        normalized_data = (input_data - np.min(input_data)) / (np.max(input_data) - np.min(input_data) + 1e-8)
        
        # Convert to spike times (inverse relationship: higher value = earlier spike)
        max_delay = 50.0  # ms
        spike_times = max_delay * (1.0 - normalized_data)
        
        return spike_times.tolist()
    
    def _extract_output_patterns(self, network_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Extract meaningful patterns from network activity"""
        output_patterns = {
            'dominant_firing_rate': network_stats['network_firing_rate'],
            'synchrony_measure': self._calculate_synchrony(network_stats),
            'complexity_measure': self._calculate_complexity(network_stats),
            'pattern_classification': self._classify_patterns(network_stats)
        }
        
        return output_patterns
    
    def _calculate_synchrony(self, network_stats: Dict[str, Any]) -> float:
        """Calculate network synchrony measure"""
        # Simplified synchrony calculation
        spike_count = network_stats['recent_spike_count']
        neuron_count = network_stats['total_neurons']
        
        if neuron_count == 0:
            return 0.0
        
        # Higher synchrony if more neurons fire together
        synchrony = spike_count / max(neuron_count, 1)
        return min(synchrony, 1.0)
    
    def _calculate_complexity(self, network_stats: Dict[str, Any]) -> float:
        """Calculate network complexity measure"""
        # Simplified complexity based on connectivity and activity
        connectivity_stats = network_stats.get('connectivity_stats', {})
        synapses = connectivity_stats.get('total_synapses', 0)
        neurons = network_stats['total_neurons']
        
        if neurons == 0:
            return 0.0
        
        # Normalized complexity
        max_possible_synapses = neurons * (neurons - 1)
        complexity = synapses / max(max_possible_synapses, 1)
        
        return min(complexity, 1.0)
    
    def _classify_patterns(self, network_stats: Dict[str, Any]) -> str:
        """Classify network activity patterns"""
        firing_rate = network_stats['network_firing_rate']
        
        if firing_rate < 0.1:
            return "quiet"
        elif firing_rate < 0.5:
            return "sparse"
        elif firing_rate < 1.0:
            return "moderate"
        else:
            return "burst"
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get comprehensive processor statistics"""
        return {
            'config': self.config.to_dict(),
            'processing_stats': self.processing_stats.copy(),
            'spike_network_stats': self.spike_orchestrator.get_network_stats(),
            'memory_networks': len(self.brain_computer.memory_networks),
            'attention_mechanisms': len(self.brain_computer.attention_mechanisms),
            'uptime_seconds': (datetime.utcnow() - self.processing_stats['start_time']).total_seconds()
        }