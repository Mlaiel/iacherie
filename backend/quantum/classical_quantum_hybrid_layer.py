"""
Classical-Quantum Hybrid Processing Layer

Hybrid classical-quantum processing optimization layer that intelligently
distributes workloads between classical and quantum processors for optimal performance.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import json
import math
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)


class ProcessingMode(Enum):
    """Processing mode selection"""
    CLASSICAL_ONLY = "classical_only"
    QUANTUM_ONLY = "quantum_only"
    HYBRID_PARALLEL = "hybrid_parallel"
    HYBRID_SEQUENTIAL = "hybrid_sequential"
    ADAPTIVE_SELECTION = "adaptive_selection"


class WorkloadType(Enum):
    """Types of computational workloads"""
    OPTIMIZATION_PROBLEM = "optimization_problem"
    MACHINE_LEARNING_TASK = "machine_learning_task"
    SEARCH_ALGORITHM = "search_algorithm"
    SIMULATION_TASK = "simulation_task"
    DATA_ANALYSIS = "data_analysis"
    PATTERN_RECOGNITION = "pattern_recognition"


@dataclass
class HybridProcessingRequest:
    """Request for hybrid classical-quantum processing"""
    task_id: str
    workload_type: WorkloadType
    processing_mode: ProcessingMode
    input_data: Dict[str, Any]
    performance_requirements: Dict[str, Any]
    cost_constraints: Optional[Dict[str, Any]] = None
    deadline_ms: Optional[int] = None


@dataclass
class ProcessingResult:
    """Result from classical or quantum processing"""
    processor_type: str  # 'classical' or 'quantum'
    success: bool
    processing_time_ms: int
    accuracy: float
    cost_units: float
    result_data: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class HybridProcessingResult:
    """Result from hybrid processing operation"""
    task_id: str
    processing_mode_used: ProcessingMode
    classical_result: Optional[ProcessingResult]
    quantum_result: Optional[ProcessingResult]
    final_result: Dict[str, Any]
    performance_comparison: Dict[str, Any]
    cost_analysis: Dict[str, Any]
    recommendations: List[str]
    total_processing_time_ms: int
    hybrid_advantage_score: float


class ClassicalQuantumHybridLayer:
    """
    Hybrid processing layer that optimally distributes workloads between
    classical and quantum processors based on performance requirements and constraints.
    """
    
    def __init__(self):
        self.classical_processors: Dict[str, Any] = {}
        self.quantum_processors: Dict[str, Any] = {}
        self.hybrid_strategies: Dict[WorkloadType, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        self.cost_models: Dict[str, Dict[str, Any]] = {}
        self.active_tasks: Dict[str, HybridProcessingRequest] = {}
        self.executor = ThreadPoolExecutor(max_workers=8)
        self.initialized = False
        
        logger.info("🔄 Classical-Quantum Hybrid Layer initialized")
    
    async def initialize(self):
        """Initialize hybrid processing capabilities"""
        try:
            await self._setup_classical_processors()
            await self._setup_quantum_processors()
            await self._configure_hybrid_strategies()
            await self._initialize_cost_models()
            await self._load_performance_history()
            self.initialized = True
            logger.info("✅ Hybrid processing layer ready")
        except Exception as e:
            logger.error(f"❌ Hybrid layer initialization failed: {e}")
            raise
    
    async def _setup_classical_processors(self):
        """Setup classical processing capabilities"""
        self.classical_processors = {
            "cpu_optimization": {
                "type": "classical_cpu",
                "capabilities": ["linear_programming", "gradient_descent", "heuristic_optimization"],
                "performance": {
                    "throughput_ops_per_sec": 10000,
                    "accuracy_range": [0.85, 0.95],
                    "memory_efficiency": 0.9,
                    "cost_per_operation": 0.001
                },
                "optimal_workloads": [WorkloadType.DATA_ANALYSIS, WorkloadType.PATTERN_RECOGNITION]
            },
            "gpu_acceleration": {
                "type": "classical_gpu",
                "capabilities": ["parallel_processing", "matrix_operations", "neural_networks"],
                "performance": {
                    "throughput_ops_per_sec": 50000,
                    "accuracy_range": [0.88, 0.96],
                    "memory_efficiency": 0.85,
                    "cost_per_operation": 0.002
                },
                "optimal_workloads": [WorkloadType.MACHINE_LEARNING_TASK, WorkloadType.SIMULATION_TASK]
            },
            "distributed_computing": {
                "type": "classical_distributed",
                "capabilities": ["large_scale_processing", "map_reduce", "distributed_optimization"],
                "performance": {
                    "throughput_ops_per_sec": 100000,
                    "accuracy_range": [0.82, 0.92],
                    "memory_efficiency": 0.95,
                    "cost_per_operation": 0.0005
                },
                "optimal_workloads": [WorkloadType.SEARCH_ALGORITHM, WorkloadType.DATA_ANALYSIS]
            }
        }
        logger.info("🖥️ Classical processors configured")
    
    async def _setup_quantum_processors(self):
        """Setup quantum processing capabilities"""
        self.quantum_processors = {
            "quantum_optimization": {
                "type": "quantum_optimization",
                "capabilities": ["qaoa", "vqe", "quantum_annealing"],
                "performance": {
                    "quantum_speedup_range": [2.0, 8.0],
                    "accuracy_range": [0.90, 0.98],
                    "coherence_time_ms": 100,
                    "cost_per_operation": 0.1
                },
                "optimal_workloads": [WorkloadType.OPTIMIZATION_PROBLEM, WorkloadType.SIMULATION_TASK],
                "hardware_requirements": {
                    "min_qubits": 10,
                    "gate_fidelity": 0.95,
                    "connectivity": "all_to_all"
                }
            },
            "quantum_ml": {
                "type": "quantum_ml",
                "capabilities": ["quantum_neural_networks", "quantum_svm", "quantum_clustering"],
                "performance": {
                    "quantum_speedup_range": [1.5, 6.0],
                    "accuracy_range": [0.92, 0.99],
                    "coherence_time_ms": 150,
                    "cost_per_operation": 0.15
                },
                "optimal_workloads": [WorkloadType.MACHINE_LEARNING_TASK, WorkloadType.PATTERN_RECOGNITION],
                "hardware_requirements": {
                    "min_qubits": 20,
                    "gate_fidelity": 0.98,
                    "connectivity": "nearest_neighbor"
                }
            },
            "quantum_search": {
                "type": "quantum_search",
                "capabilities": ["grovers_algorithm", "quantum_walk", "amplitude_amplification"],
                "performance": {
                    "quantum_speedup_range": [3.0, 12.0],
                    "accuracy_range": [0.95, 0.99],
                    "coherence_time_ms": 80,
                    "cost_per_operation": 0.08
                },
                "optimal_workloads": [WorkloadType.SEARCH_ALGORITHM, WorkloadType.DATA_ANALYSIS],
                "hardware_requirements": {
                    "min_qubits": 15,
                    "gate_fidelity": 0.96,
                    "connectivity": "linear"
                }
            }
        }
        logger.info("⚛️ Quantum processors configured")
    
    async def _configure_hybrid_strategies(self):
        """Configure hybrid processing strategies for different workload types"""
        self.hybrid_strategies = {
            WorkloadType.OPTIMIZATION_PROBLEM: {
                "recommended_mode": ProcessingMode.HYBRID_PARALLEL,
                "classical_contribution": 0.3,
                "quantum_contribution": 0.7,
                "decision_criteria": {
                    "problem_size_threshold": 1000,
                    "accuracy_requirement_threshold": 0.95,
                    "time_constraint_threshold_ms": 5000
                },
                "fallback_strategy": ProcessingMode.CLASSICAL_ONLY
            },
            WorkloadType.MACHINE_LEARNING_TASK: {
                "recommended_mode": ProcessingMode.HYBRID_SEQUENTIAL,
                "classical_contribution": 0.6,
                "quantum_contribution": 0.4,
                "decision_criteria": {
                    "dataset_size_threshold": 10000,
                    "feature_dimension_threshold": 100,
                    "training_time_threshold_ms": 30000
                },
                "fallback_strategy": ProcessingMode.CLASSICAL_ONLY
            },
            WorkloadType.SEARCH_ALGORITHM: {
                "recommended_mode": ProcessingMode.QUANTUM_ONLY,
                "classical_contribution": 0.2,
                "quantum_contribution": 0.8,
                "decision_criteria": {
                    "search_space_size_threshold": 1000000,
                    "accuracy_requirement_threshold": 0.90,
                    "speedup_requirement": 2.0
                },
                "fallback_strategy": ProcessingMode.HYBRID_PARALLEL
            },
            WorkloadType.SIMULATION_TASK: {
                "recommended_mode": ProcessingMode.ADAPTIVE_SELECTION,
                "classical_contribution": 0.5,
                "quantum_contribution": 0.5,
                "decision_criteria": {
                    "complexity_threshold": 500,
                    "precision_requirement": 0.92,
                    "computational_budget": 1000
                },
                "fallback_strategy": ProcessingMode.CLASSICAL_ONLY
            },
            WorkloadType.DATA_ANALYSIS: {
                "recommended_mode": ProcessingMode.CLASSICAL_ONLY,
                "classical_contribution": 0.8,
                "quantum_contribution": 0.2,
                "decision_criteria": {
                    "data_volume_threshold": 100000,
                    "analysis_complexity_threshold": 0.7,
                    "real_time_requirement": True
                },
                "fallback_strategy": ProcessingMode.CLASSICAL_ONLY
            },
            WorkloadType.PATTERN_RECOGNITION: {
                "recommended_mode": ProcessingMode.HYBRID_PARALLEL,
                "classical_contribution": 0.4,
                "quantum_contribution": 0.6,
                "decision_criteria": {
                    "pattern_complexity_threshold": 0.8,
                    "recognition_accuracy_threshold": 0.95,
                    "processing_speed_requirement": 2.0
                },
                "fallback_strategy": ProcessingMode.CLASSICAL_ONLY
            }
        }
        logger.info("🔧 Hybrid strategies configured")
    
    async def _initialize_cost_models(self):
        """Initialize cost models for different processing modes"""
        self.cost_models = {
            "classical_processing": {
                "base_cost_per_ms": 0.001,
                "memory_cost_per_mb": 0.0001,
                "storage_cost_per_gb": 0.01,
                "scaling_factor": 1.0
            },
            "quantum_processing": {
                "base_cost_per_ms": 0.1,
                "qubit_cost_per_operation": 0.01,
                "calibration_overhead_cost": 5.0,
                "scaling_factor": 2.0
            },
            "hybrid_processing": {
                "coordination_overhead_cost": 1.0,
                "data_transfer_cost_per_mb": 0.001,
                "synchronization_cost": 0.5,
                "optimization_benefit_factor": 0.85
            }
        }
        logger.info("💰 Cost models initialized")
    
    async def _load_performance_history(self):
        """Load historical performance data for optimization"""
        # Initialize empty performance history
        self.performance_history = {
            workload_type.value: [] for workload_type in WorkloadType
        }
        logger.info("📊 Performance history initialized")
    
    async def process_hybrid_request(self, request: HybridProcessingRequest) -> HybridProcessingResult:
        """Process hybrid classical-quantum request"""
        if not self.initialized:
            await self.initialize()
        
        start_time = time.time()
        logger.info(f"🔄 Processing hybrid request: {request.task_id}")
        
        try:
            # Add to active tasks
            self.active_tasks[request.task_id] = request
            
            # Determine optimal processing mode
            optimal_mode = await self._determine_processing_mode(request)
            
            # Execute processing based on mode
            classical_result, quantum_result = await self._execute_hybrid_processing(
                request, optimal_mode
            )
            
            # Combine results and perform analysis
            final_result = await self._combine_processing_results(
                classical_result, quantum_result, optimal_mode
            )
            
            # Generate performance comparison
            performance_comparison = await self._analyze_performance_comparison(
                classical_result, quantum_result
            )
            
            # Calculate cost analysis
            cost_analysis = await self._calculate_cost_analysis(
                request, classical_result, quantum_result
            )
            
            # Generate recommendations
            recommendations = await self._generate_hybrid_recommendations(
                request, classical_result, quantum_result, performance_comparison
            )
            
            # Calculate hybrid advantage score
            hybrid_advantage = await self._calculate_hybrid_advantage(
                performance_comparison, cost_analysis
            )
            
            total_time = int((time.time() - start_time) * 1000)
            
            result = HybridProcessingResult(
                task_id=request.task_id,
                processing_mode_used=optimal_mode,
                classical_result=classical_result,
                quantum_result=quantum_result,
                final_result=final_result,
                performance_comparison=performance_comparison,
                cost_analysis=cost_analysis,
                recommendations=recommendations,
                total_processing_time_ms=total_time,
                hybrid_advantage_score=hybrid_advantage
            )
            
            # Update performance history
            await self._update_performance_history(request, result)
            
            # Clean up
            del self.active_tasks[request.task_id]
            
            logger.info(f"✅ Hybrid processing completed: {request.task_id}")
            return result
            
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            logger.error(f"❌ Hybrid processing failed: {request.task_id} - {e}")
            
            # Return error result
            return HybridProcessingResult(
                task_id=request.task_id,
                processing_mode_used=ProcessingMode.CLASSICAL_ONLY,
                classical_result=None,
                quantum_result=None,
                final_result={"error": str(e)},
                performance_comparison={},
                cost_analysis={},
                recommendations=[f"Processing failed: {str(e)}"],
                total_processing_time_ms=total_time,
                hybrid_advantage_score=0.0
            )
    
    async def _determine_processing_mode(self, request: HybridProcessingRequest) -> ProcessingMode:
        """Determine optimal processing mode based on request characteristics"""
        workload_type = request.workload_type
        
        # Use specified mode if provided and not adaptive
        if request.processing_mode != ProcessingMode.ADAPTIVE_SELECTION:
            return request.processing_mode
        
        # Get strategy for this workload type
        strategy = self.hybrid_strategies.get(workload_type)
        if not strategy:
            return ProcessingMode.CLASSICAL_ONLY
        
        # Analyze request characteristics
        input_data = request.input_data
        performance_req = request.performance_requirements
        
        # Extract decision factors
        data_size = len(json.dumps(input_data))
        accuracy_requirement = performance_req.get("accuracy_target", 0.9)
        time_constraint = request.deadline_ms or 60000  # Default 60 seconds
        
        criteria = strategy["decision_criteria"]
        
        # Decision logic based on criteria
        quantum_favorable = 0
        classical_favorable = 0
        
        # Size/complexity check
        if workload_type == WorkloadType.OPTIMIZATION_PROBLEM:
            if data_size > criteria.get("problem_size_threshold", 1000):
                quantum_favorable += 2
            else:
                classical_favorable += 1
        
        # Accuracy requirement check
        if accuracy_requirement > criteria.get("accuracy_requirement_threshold", 0.95):
            quantum_favorable += 1
        else:
            classical_favorable += 1
        
        # Time constraint check
        if time_constraint > criteria.get("time_constraint_threshold_ms", 5000):
            quantum_favorable += 1
        else:
            classical_favorable += 2  # Classical often faster for simple tasks
        
        # Cost constraint check
        if request.cost_constraints and request.cost_constraints.get("max_cost", float('inf')) < 10.0:
            classical_favorable += 2
        
        # Determine mode based on scores
        if quantum_favorable > classical_favorable + 1:
            selected_mode = ProcessingMode.QUANTUM_ONLY
        elif classical_favorable > quantum_favorable + 1:
            selected_mode = ProcessingMode.CLASSICAL_ONLY
        else:
            selected_mode = strategy["recommended_mode"]
        
        logger.info(f"🎯 Selected processing mode: {selected_mode.value} (Q:{quantum_favorable}, C:{classical_favorable})")
        return selected_mode
    
    async def _execute_hybrid_processing(
        self, 
        request: HybridProcessingRequest, 
        mode: ProcessingMode
    ) -> Tuple[Optional[ProcessingResult], Optional[ProcessingResult]]:
        """Execute processing based on selected mode"""
        classical_result = None
        quantum_result = None
        
        if mode == ProcessingMode.CLASSICAL_ONLY:
            classical_result = await self._execute_classical_processing(request)
        
        elif mode == ProcessingMode.QUANTUM_ONLY:
            quantum_result = await self._execute_quantum_processing(request)
        
        elif mode == ProcessingMode.HYBRID_PARALLEL:
            # Execute both in parallel
            classical_task = asyncio.create_task(self._execute_classical_processing(request))
            quantum_task = asyncio.create_task(self._execute_quantum_processing(request))
            
            classical_result, quantum_result = await asyncio.gather(
                classical_task, quantum_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(classical_result, Exception):
                logger.warning(f"Classical processing failed: {classical_result}")
                classical_result = None
            if isinstance(quantum_result, Exception):
                logger.warning(f"Quantum processing failed: {quantum_result}")
                quantum_result = None
        
        elif mode == ProcessingMode.HYBRID_SEQUENTIAL:
            # Execute classical first, then quantum enhancement
            classical_result = await self._execute_classical_processing(request)
            if classical_result and classical_result.success:
                # Use classical result as input for quantum enhancement
                enhanced_request = self._create_enhancement_request(request, classical_result)
                quantum_result = await self._execute_quantum_processing(enhanced_request)
        
        return classical_result, quantum_result
    
    async def _execute_classical_processing(self, request: HybridProcessingRequest) -> ProcessingResult:
        """Execute classical processing"""
        start_time = time.time()
        workload_type = request.workload_type
        
        # Select optimal classical processor
        processor = await self._select_classical_processor(workload_type)
        
        try:
            # Simulate classical processing
            await asyncio.sleep(0.05)  # Simulated processing time
            
            # Generate realistic performance metrics
            performance = processor["performance"]
            processing_time = int((time.time() - start_time) * 1000)
            
            # Simulate accuracy based on workload complexity
            base_accuracy = (performance["accuracy_range"][0] + performance["accuracy_range"][1]) / 2
            workload_complexity = len(json.dumps(request.input_data)) / 10000
            accuracy = max(0.7, base_accuracy - workload_complexity * 0.1)
            
            cost = processing_time * processor["performance"]["cost_per_operation"]
            
            result_data = {
                "processor_used": processor["type"],
                "algorithm_applied": processor["capabilities"][0],
                "optimization_result": {"status": "converged", "iterations": 100},
                "performance_metrics": {
                    "throughput": performance["throughput_ops_per_sec"],
                    "memory_usage": 0.6,
                    "cpu_utilization": 0.8
                }
            }
            
            return ProcessingResult(
                processor_type="classical",
                success=True,
                processing_time_ms=processing_time,
                accuracy=accuracy,
                cost_units=cost,
                result_data=result_data,
                performance_metrics={
                    "throughput_ops_per_sec": performance["throughput_ops_per_sec"],
                    "memory_efficiency": performance["memory_efficiency"],
                    "energy_efficiency": 0.85
                }
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return ProcessingResult(
                processor_type="classical",
                success=False,
                processing_time_ms=processing_time,
                accuracy=0.0,
                cost_units=0.0,
                result_data={},
                performance_metrics={},
                error_message=str(e)
            )
    
    async def _execute_quantum_processing(self, request: HybridProcessingRequest) -> ProcessingResult:
        """Execute quantum processing"""
        start_time = time.time()
        workload_type = request.workload_type
        
        # Select optimal quantum processor
        processor = await self._select_quantum_processor(workload_type)
        
        try:
            # Simulate quantum processing
            await asyncio.sleep(0.02)  # Quantum processing often faster
            
            # Generate realistic quantum performance metrics
            performance = processor["performance"]
            processing_time = int((time.time() - start_time) * 1000)
            
            # Quantum accuracy often higher but depends on coherence
            base_accuracy = (performance["accuracy_range"][0] + performance["accuracy_range"][1]) / 2
            coherence_factor = min(1.0, performance["coherence_time_ms"] / 100)
            accuracy = base_accuracy * coherence_factor
            
            # Quantum speedup calculation
            speedup_range = performance["quantum_speedup_range"]
            achieved_speedup = (speedup_range[0] + speedup_range[1]) / 2
            
            cost = processing_time * processor["performance"]["cost_per_operation"]
            
            result_data = {
                "processor_used": processor["type"],
                "quantum_algorithm_applied": processor["capabilities"][0],
                "quantum_speedup_achieved": achieved_speedup,
                "qubit_usage": processor["hardware_requirements"]["min_qubits"],
                "gate_fidelity": processor["hardware_requirements"]["gate_fidelity"],
                "quantum_volume": 64,
                "optimization_result": {"status": "optimal", "quantum_advantage": True}
            }
            
            return ProcessingResult(
                processor_type="quantum",
                success=True,
                processing_time_ms=processing_time,
                accuracy=accuracy,
                cost_units=cost,
                result_data=result_data,
                performance_metrics={
                    "quantum_speedup": achieved_speedup,
                    "gate_fidelity": processor["hardware_requirements"]["gate_fidelity"],
                    "coherence_time_ms": performance["coherence_time_ms"],
                    "error_rate": 0.01
                }
            )
            
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return ProcessingResult(
                processor_type="quantum",
                success=False,
                processing_time_ms=processing_time,
                accuracy=0.0,
                cost_units=0.0,
                result_data={},
                performance_metrics={},
                error_message=str(e)
            )
    
    async def _select_classical_processor(self, workload_type: WorkloadType) -> Dict[str, Any]:
        """Select optimal classical processor for workload type"""
        # Find processors optimal for this workload
        suitable_processors = [
            processor for processor in self.classical_processors.values()
            if workload_type in processor["optimal_workloads"]
        ]
        
        if suitable_processors:
            # Select based on throughput (simple heuristic)
            return max(suitable_processors, 
                      key=lambda p: p["performance"]["throughput_ops_per_sec"])
        else:
            # Default to first available
            return list(self.classical_processors.values())[0]
    
    async def _select_quantum_processor(self, workload_type: WorkloadType) -> Dict[str, Any]:
        """Select optimal quantum processor for workload type"""
        # Find processors optimal for this workload
        suitable_processors = [
            processor for processor in self.quantum_processors.values()
            if workload_type in processor["optimal_workloads"]
        ]
        
        if suitable_processors:
            # Select based on quantum speedup (simple heuristic)
            return max(suitable_processors, 
                      key=lambda p: max(p["performance"]["quantum_speedup_range"]))
        else:
            # Default to first available
            return list(self.quantum_processors.values())[0]
    
    def _create_enhancement_request(
        self, 
        original_request: HybridProcessingRequest, 
        classical_result: ProcessingResult
    ) -> HybridProcessingRequest:
        """Create quantum enhancement request based on classical result"""
        enhanced_data = original_request.input_data.copy()
        enhanced_data["classical_preprocessing_result"] = classical_result.result_data
        
        return HybridProcessingRequest(
            task_id=f"{original_request.task_id}_quantum_enhancement",
            workload_type=original_request.workload_type,
            processing_mode=ProcessingMode.QUANTUM_ONLY,
            input_data=enhanced_data,
            performance_requirements=original_request.performance_requirements,
            cost_constraints=original_request.cost_constraints,
            deadline_ms=original_request.deadline_ms
        )
    
    async def _combine_processing_results(
        self, 
        classical_result: Optional[ProcessingResult], 
        quantum_result: Optional[ProcessingResult], 
        mode: ProcessingMode
    ) -> Dict[str, Any]:
        """Combine classical and quantum processing results"""
        combined_result = {
            "processing_mode": mode.value,
            "timestamp": time.time()
        }
        
        if mode == ProcessingMode.CLASSICAL_ONLY and classical_result:
            combined_result.update({
                "primary_result": classical_result.result_data,
                "accuracy": classical_result.accuracy,
                "processing_approach": "classical_optimization"
            })
        
        elif mode == ProcessingMode.QUANTUM_ONLY and quantum_result:
            combined_result.update({
                "primary_result": quantum_result.result_data,
                "accuracy": quantum_result.accuracy,
                "processing_approach": "quantum_enhanced",
                "quantum_advantage": quantum_result.result_data.get("quantum_speedup_achieved", 1.0)
            })
        
        elif mode in [ProcessingMode.HYBRID_PARALLEL, ProcessingMode.HYBRID_SEQUENTIAL]:
            # Combine both results
            if classical_result and quantum_result:
                # Use quantum result as primary if more accurate
                if quantum_result.accuracy > classical_result.accuracy:
                    primary_result = quantum_result.result_data
                    primary_accuracy = quantum_result.accuracy
                    approach = "quantum_primary_hybrid"
                else:
                    primary_result = classical_result.result_data
                    primary_accuracy = classical_result.accuracy
                    approach = "classical_primary_hybrid"
                
                combined_result.update({
                    "primary_result": primary_result,
                    "secondary_result": quantum_result.result_data if quantum_result.accuracy <= classical_result.accuracy else classical_result.result_data,
                    "accuracy": primary_accuracy,
                    "processing_approach": approach,
                    "hybrid_confidence": (classical_result.accuracy + quantum_result.accuracy) / 2,
                    "consensus_metrics": {
                        "agreement_score": self._calculate_result_agreement(classical_result, quantum_result),
                        "combined_confidence": min(classical_result.accuracy, quantum_result.accuracy)
                    }
                })
            elif classical_result:
                combined_result.update({
                    "primary_result": classical_result.result_data,
                    "accuracy": classical_result.accuracy,
                    "processing_approach": "classical_fallback"
                })
            elif quantum_result:
                combined_result.update({
                    "primary_result": quantum_result.result_data,
                    "accuracy": quantum_result.accuracy,
                    "processing_approach": "quantum_fallback"
                })
        
        return combined_result
    
    def _calculate_result_agreement(
        self, 
        classical_result: ProcessingResult, 
        quantum_result: ProcessingResult
    ) -> float:
        """Calculate agreement score between classical and quantum results"""
        # Simple agreement calculation based on accuracy similarity
        accuracy_agreement = 1.0 - abs(classical_result.accuracy - quantum_result.accuracy)
        
        # Time efficiency agreement
        time_ratio = min(classical_result.processing_time_ms, quantum_result.processing_time_ms) / max(classical_result.processing_time_ms, quantum_result.processing_time_ms)
        
        # Overall agreement score
        agreement_score = (accuracy_agreement + time_ratio) / 2
        return round(agreement_score, 3)
    
    async def _analyze_performance_comparison(
        self, 
        classical_result: Optional[ProcessingResult], 
        quantum_result: Optional[ProcessingResult]
    ) -> Dict[str, Any]:
        """Analyze performance comparison between classical and quantum results"""
        comparison = {
            "comparison_available": classical_result is not None and quantum_result is not None
        }
        
        if comparison["comparison_available"]:
            # Speed comparison
            speed_ratio = classical_result.processing_time_ms / quantum_result.processing_time_ms
            comparison["quantum_speedup"] = round(speed_ratio, 2)
            
            # Accuracy comparison
            accuracy_improvement = quantum_result.accuracy - classical_result.accuracy
            comparison["accuracy_improvement"] = round(accuracy_improvement, 3)
            
            # Cost comparison
            cost_ratio = quantum_result.cost_units / classical_result.cost_units if classical_result.cost_units > 0 else float('inf')
            comparison["cost_ratio_quantum_vs_classical"] = round(cost_ratio, 2)
            
            # Overall advantage calculation
            if speed_ratio > 1.2 and accuracy_improvement > 0.05:
                comparison["quantum_advantage"] = "significant"
            elif speed_ratio > 1.0 or accuracy_improvement > 0.02:
                comparison["quantum_advantage"] = "moderate"
            else:
                comparison["quantum_advantage"] = "minimal"
            
            # Performance metrics
            comparison["performance_summary"] = {
                "classical_performance": {
                    "time_ms": classical_result.processing_time_ms,
                    "accuracy": classical_result.accuracy,
                    "cost": classical_result.cost_units
                },
                "quantum_performance": {
                    "time_ms": quantum_result.processing_time_ms,
                    "accuracy": quantum_result.accuracy,
                    "cost": quantum_result.cost_units,
                    "speedup": speed_ratio
                }
            }
        
        return comparison
    
    async def _calculate_cost_analysis(
        self, 
        request: HybridProcessingRequest, 
        classical_result: Optional[ProcessingResult], 
        quantum_result: Optional[ProcessingResult]
    ) -> Dict[str, Any]:
        """Calculate comprehensive cost analysis"""
        cost_analysis = {
            "total_processing_cost": 0.0,
            "cost_breakdown": {},
            "cost_efficiency_metrics": {}
        }
        
        if classical_result:
            classical_cost = classical_result.cost_units
            cost_analysis["cost_breakdown"]["classical_processing"] = classical_cost
            cost_analysis["total_processing_cost"] += classical_cost
        
        if quantum_result:
            quantum_cost = quantum_result.cost_units
            # Add quantum overhead costs
            overhead_cost = self.cost_models["quantum_processing"]["calibration_overhead_cost"]
            total_quantum_cost = quantum_cost + overhead_cost
            
            cost_analysis["cost_breakdown"]["quantum_processing"] = quantum_cost
            cost_analysis["cost_breakdown"]["quantum_overhead"] = overhead_cost
            cost_analysis["total_processing_cost"] += total_quantum_cost
        
        # Add hybrid coordination costs if both processors used
        if classical_result and quantum_result:
            hybrid_cost = self.cost_models["hybrid_processing"]["coordination_overhead_cost"]
            cost_analysis["cost_breakdown"]["hybrid_coordination"] = hybrid_cost
            cost_analysis["total_processing_cost"] += hybrid_cost
        
        # Cost efficiency metrics
        if classical_result and quantum_result:
            classical_efficiency = classical_result.accuracy / classical_result.cost_units if classical_result.cost_units > 0 else 0
            quantum_efficiency = quantum_result.accuracy / quantum_result.cost_units if quantum_result.cost_units > 0 else 0
            
            cost_analysis["cost_efficiency_metrics"] = {
                "classical_accuracy_per_cost": round(classical_efficiency, 4),
                "quantum_accuracy_per_cost": round(quantum_efficiency, 4),
                "hybrid_efficiency_advantage": round((quantum_efficiency - classical_efficiency) / max(classical_efficiency, 0.001), 3)
            }
        
        # Budget compliance check
        if request.cost_constraints:
            max_budget = request.cost_constraints.get("max_cost", float('inf'))
            cost_analysis["budget_compliance"] = {
                "budget_limit": max_budget,
                "actual_cost": cost_analysis["total_processing_cost"],
                "budget_utilization": cost_analysis["total_processing_cost"] / max_budget,
                "within_budget": cost_analysis["total_processing_cost"] <= max_budget
            }
        
        return cost_analysis
    
    async def _generate_hybrid_recommendations(
        self, 
        request: HybridProcessingRequest, 
        classical_result: Optional[ProcessingResult], 
        quantum_result: Optional[ProcessingResult], 
        performance_comparison: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for future hybrid processing"""
        recommendations = []
        
        # Performance-based recommendations
        if performance_comparison.get("comparison_available"):
            quantum_advantage = performance_comparison.get("quantum_advantage", "minimal")
            speedup = performance_comparison.get("quantum_speedup", 1.0)
            
            if quantum_advantage == "significant":
                recommendations.append("Strong quantum advantage demonstrated - prioritize quantum processing for similar workloads")
                recommendations.append(f"Quantum speedup of {speedup}x achieved - consider expanding quantum resource allocation")
            elif quantum_advantage == "moderate":
                recommendations.append("Moderate quantum benefit - hybrid approach recommended for optimal cost-performance balance")
            else:
                recommendations.append("Limited quantum advantage - consider classical optimization or workload restructuring")
        
        # Workload-specific recommendations
        workload_type = request.workload_type
        if workload_type == WorkloadType.OPTIMIZATION_PROBLEM and quantum_result:
            if quantum_result.accuracy > 0.95:
                recommendations.append("High-accuracy quantum optimization achieved - suitable for critical optimization tasks")
        
        elif workload_type == WorkloadType.MACHINE_LEARNING_TASK:
            if classical_result and quantum_result:
                if quantum_result.accuracy > classical_result.accuracy + 0.05:
                    recommendations.append("Quantum ML enhancement effective - consider quantum feature enhancement")
                else:
                    recommendations.append("Classical ML sufficient - use quantum for preprocessing or ensemble methods")
        
        # Cost optimization recommendations
        if classical_result and quantum_result:
            if quantum_result.cost_units > classical_result.cost_units * 5:
                recommendations.append("Quantum processing cost-intensive - optimize for high-value use cases only")
            elif quantum_result.cost_units < classical_result.cost_units * 2:
                recommendations.append("Quantum processing cost-effective - consider broader quantum adoption")
        
        # Resource utilization recommendations
        if quantum_result and quantum_result.success:
            coherence_time = quantum_result.performance_metrics.get("coherence_time_ms", 0)
            if coherence_time > 100:
                recommendations.append("Good quantum coherence - suitable for complex quantum algorithms")
            else:
                recommendations.append("Limited coherence time - focus on short-duration quantum algorithms")
        
        return recommendations
    
    async def _calculate_hybrid_advantage(
        self, 
        performance_comparison: Dict[str, Any], 
        cost_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall hybrid processing advantage score"""
        advantage_score = 0.0
        
        if performance_comparison.get("comparison_available"):
            # Performance advantage component
            speedup = performance_comparison.get("quantum_speedup", 1.0)
            accuracy_improvement = performance_comparison.get("accuracy_improvement", 0.0)
            
            speedup_score = min((speedup - 1.0) * 2.0, 3.0)  # Max 3 points for speedup
            accuracy_score = accuracy_improvement * 10.0  # Max 3 points for 30% improvement
            
            performance_score = (speedup_score + accuracy_score) / 2
            
            # Cost efficiency component
            cost_efficiency = cost_analysis.get("cost_efficiency_metrics", {})
            efficiency_advantage = cost_efficiency.get("hybrid_efficiency_advantage", 0.0)
            cost_score = max(0, min(efficiency_advantage * 2.0, 2.0))  # Max 2 points
            
            # Overall advantage score (max 5.0)
            advantage_score = (performance_score + cost_score) / 1.5
        
        return round(min(advantage_score, 5.0), 2)
    
    async def _update_performance_history(
        self, 
        request: HybridProcessingRequest, 
        result: HybridProcessingResult
    ):
        """Update performance history for learning and optimization"""
        workload_type = request.workload_type.value
        
        history_entry = {
            "timestamp": time.time(),
            "processing_mode": result.processing_mode_used.value,
            "total_time_ms": result.total_processing_time_ms,
            "hybrid_advantage_score": result.hybrid_advantage_score,
            "cost_total": result.cost_analysis.get("total_processing_cost", 0.0),
            "performance_comparison": result.performance_comparison,
            "success": result.classical_result.success if result.classical_result else True
        }
        
        if workload_type in self.performance_history:
            self.performance_history[workload_type].append(history_entry)
            
            # Keep only recent history (last 100 entries)
            if len(self.performance_history[workload_type]) > 100:
                self.performance_history[workload_type] = self.performance_history[workload_type][-100:]
    
    async def get_hybrid_processing_capabilities(self) -> Dict[str, Any]:
        """Get hybrid processing system capabilities"""
        return {
            "processing_modes": [mode.value for mode in ProcessingMode],
            "workload_types": [workload.value for workload in WorkloadType],
            "classical_processors": {
                name: {
                    "type": processor["type"],
                    "capabilities": processor["capabilities"],
                    "optimal_workloads": [w.value for w in processor["optimal_workloads"]]
                }
                for name, processor in self.classical_processors.items()
            },
            "quantum_processors": {
                name: {
                    "type": processor["type"],
                    "capabilities": processor["capabilities"],
                    "optimal_workloads": [w.value for w in processor["optimal_workloads"]],
                    "hardware_requirements": processor["hardware_requirements"]
                }
                for name, processor in self.quantum_processors.items()
            },
            "hybrid_strategies": {
                workload.value: {
                    "recommended_mode": strategy["recommended_mode"].value,
                    "classical_contribution": strategy["classical_contribution"],
                    "quantum_contribution": strategy["quantum_contribution"]
                }
                for workload, strategy in self.hybrid_strategies.items()
            },
            "active_tasks": len(self.active_tasks)
        }
    
    async def get_performance_analytics(self) -> Dict[str, Any]:
        """Get performance analytics from historical data"""
        analytics = {
            "overall_statistics": {
                "total_tasks_processed": sum(len(history) for history in self.performance_history.values()),
                "average_hybrid_advantage": 0.0,
                "processing_modes_usage": {},
                "cost_efficiency_trends": {}
            },
            "workload_analytics": {}
        }
        
        # Calculate overall statistics
        all_entries = [entry for history in self.performance_history.values() for entry in history]
        
        if all_entries:
            analytics["overall_statistics"]["average_hybrid_advantage"] = sum(
                entry["hybrid_advantage_score"] for entry in all_entries
            ) / len(all_entries)
            
            # Processing modes usage
            mode_counts = {}
            for entry in all_entries:
                mode = entry["processing_mode"]
                mode_counts[mode] = mode_counts.get(mode, 0) + 1
            
            total_tasks = len(all_entries)
            analytics["overall_statistics"]["processing_modes_usage"] = {
                mode: count / total_tasks for mode, count in mode_counts.items()
            }
        
        # Workload-specific analytics
        for workload_type, history in self.performance_history.items():
            if history:
                analytics["workload_analytics"][workload_type] = {
                    "total_tasks": len(history),
                    "average_processing_time_ms": sum(entry["total_time_ms"] for entry in history) / len(history),
                    "average_hybrid_advantage": sum(entry["hybrid_advantage_score"] for entry in history) / len(history),
                    "success_rate": sum(1 for entry in history if entry["success"]) / len(history),
                    "preferred_processing_mode": max(
                        set(entry["processing_mode"] for entry in history),
                        key=lambda mode: sum(1 for entry in history if entry["processing_mode"] == mode)
                    )
                }
        
        return analytics


# Singleton instance
_hybrid_layer: Optional[ClassicalQuantumHybridLayer] = None

def get_hybrid_layer() -> ClassicalQuantumHybridLayer:
    """Get singleton hybrid processing layer instance"""
    global _hybrid_layer
    if _hybrid_layer is None:
        _hybrid_layer = ClassicalQuantumHybridLayer()
    return _hybrid_layer


# Convenience functions
async def process_optimization_hybrid(
    optimization_data: Dict[str, Any],
    performance_requirements: Dict[str, Any],
    mode: ProcessingMode = ProcessingMode.ADAPTIVE_SELECTION
) -> HybridProcessingResult:
    """Convenience function for hybrid optimization processing"""
    layer = get_hybrid_layer()
    
    request = HybridProcessingRequest(
        task_id=f"optimization_{int(time.time())}",
        workload_type=WorkloadType.OPTIMIZATION_PROBLEM,
        processing_mode=mode,
        input_data=optimization_data,
        performance_requirements=performance_requirements
    )
    
    return await layer.process_hybrid_request(request)


async def process_ml_hybrid(
    ml_data: Dict[str, Any],
    performance_requirements: Dict[str, Any],
    mode: ProcessingMode = ProcessingMode.ADAPTIVE_SELECTION
) -> HybridProcessingResult:
    """Convenience function for hybrid machine learning processing"""
    layer = get_hybrid_layer()
    
    request = HybridProcessingRequest(
        task_id=f"ml_{int(time.time())}",
        workload_type=WorkloadType.MACHINE_LEARNING_TASK,
        processing_mode=mode,
        input_data=ml_data,
        performance_requirements=performance_requirements
    )
    
    return await layer.process_hybrid_request(request)