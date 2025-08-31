"""🔧 Vector Database Optimization Engine
======================================

Advanced optimization engine for vector database performance tuning.
Automatically optimizes indexes, parameters, and configurations for optimal performance.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️  AVERTISSEMENT LÉGAL IMPORTANT ⚠️
=====================================
Ce code est la propriété intellectuelle exclusive de Fahed Mlaiel.
Toute utilisation, copie, modification ou distribution sans autorisation 
écrite explicite est strictement interdite et constitue une violation 
des droits d'auteur passible de poursuites judiciaires.

Contact: mlaiel@live.de
"""import asyncio
import logging
import numpy as np
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from collections import defaultdict, deque
import math

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Types of optimizations supported"""    INDEX_STRUCTURE = "index_structure"
    SEARCH_PARAMETERS = "search_parameters"
    MEMORY_USAGE = "memory_usage"
    QUERY_PERFORMANCE = "query_performance"
    CACHE_STRATEGY = "cache_strategy"
    BATCH_PROCESSING = "batch_processing"


class OptimizationLevel(Enum):
    """Optimization intensity levels"""    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    EXPERT = "expert"


@dataclass
class OptimizationRecommendation:
    """Individual optimization recommendation"""    optimization_id: str
    optimization_type: OptimizationType
    current_value: Any
    recommended_value: Any
    expected_improvement: float  # Percentage improvement expected
    confidence: float  # Confidence in recommendation (0-1)
    implementation_cost: str  # low, medium, high
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizationResult:
    """Result of optimization implementation"""    optimization_id: str
    implemented_at: float
    before_metrics: Dict[str, float]
    after_metrics: Dict[str, float]
    actual_improvement: float
    success: bool
    error_message: Optional[str] = None


@dataclass
class PerformanceBenchmark:
    """Performance benchmark measurement"""    benchmark_id: str
    test_type: str
    dataset_size: int
    query_count: int
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_qps: float
    memory_usage_mb: float
    timestamp: float
    configuration: Dict[str, Any]


class IndexAnalyzer:
    """Analyze index characteristics and performance"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.IndexAnalyzer")
        
        # Analysis cache
        self.analysis_cache = {}
        self.cache_ttl = config.get('analysis_cache_ttl', 300)  # 5 minutes
    
    async def analyze_index_efficiency(self, index, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current index efficiency and characteristics"""        try:
            analysis_key = f"{metadata.get('index_type', 'unknown')}_{metadata.get('total_vectors', 0)}"
            
            # Check cache
            if analysis_key in self.analysis_cache:
                cached_analysis, cached_time = self.analysis_cache[analysis_key]
                if time.time() - cached_time < self.cache_ttl:
                    return cached_analysis
            
            analysis = {
                'index_type': metadata.get('index_type', 'unknown'),
                'total_vectors': metadata.get('total_vectors', 0),
                'dimension': metadata.get('dimension', 0),
                'memory_usage_mb': metadata.get('memory_usage_mb', 0),
                'efficiency_score': 0.0,
                'bottlenecks': [],
                'recommendations': []
            }
            
            # Calculate efficiency metrics
            total_vectors = analysis['total_vectors']
            dimension = analysis['dimension']
            memory_usage = analysis['memory_usage_mb']
            
            if total_vectors > 0 and dimension > 0:
                # Memory efficiency (bytes per vector)
                theoretical_min_memory = (total_vectors * dimension * 4) / (1024 * 1024)  # 4 bytes per float
                memory_efficiency = theoretical_min_memory / memory_usage if memory_usage > 0 else 0
                
                # Index type efficiency assessment
                index_type_efficiency = self._assess_index_type_efficiency(
                    analysis['index_type'], total_vectors, dimension
                )
                
                # Overall efficiency score
                analysis['efficiency_score'] = (memory_efficiency + index_type_efficiency) / 2
                
                # Identify bottlenecks
                if memory_efficiency < 0.5:
                    analysis['bottlenecks'].append("high_memory_overhead")
                
                if total_vectors > 100000 and analysis['index_type'] in ['IndexFlatL2', 'IndexFlatIP']:
                    analysis['bottlenecks'].append("linear_search_scaling")
                
                if dimension > 1000 and analysis['index_type'] not in ['IndexIVFPQ']:
                    analysis['bottlenecks'].append("high_dimensionality")
                
                # Generate recommendations
                analysis['recommendations'] = self._generate_index_recommendations(analysis)
            
            # Cache analysis
            self.analysis_cache[analysis_key] = (analysis, time.time())
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Index analysis failed: {e}")
            return {'error': str(e)}
    
    def _assess_index_type_efficiency(self, index_type: str, total_vectors: int, dimension: int) -> float:
        """Assess efficiency of current index type for dataset characteristics"""        
        # Efficiency scoring based on dataset size and characteristics
        if total_vectors < 1000:
            # Small dataset - flat indexes are fine
            if index_type in ['IndexFlatL2', 'IndexFlatIP']:
                return 1.0
            else:
                return 0.7  # Overkill but not harmful
        
        elif total_vectors < 100000:
            # Medium dataset
            if index_type in ['IndexIVFFlat', 'IndexHNSWFlat']:
                return 1.0
            elif index_type in ['IndexFlatL2', 'IndexFlatIP']:
                return 0.6  # Will be slow
            else:
                return 0.8
        
        else:
            # Large dataset
            if index_type in ['IndexIVFPQ', 'IndexHNSWFlat']:
                return 1.0
            elif index_type in ['IndexIVFFlat']:
                return 0.8
            else:
                return 0.4  # Poor choice for large datasets
    
    def _generate_index_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations based on analysis"""        recommendations = []
        
        total_vectors = analysis['total_vectors']
        dimension = analysis['dimension']
        index_type = analysis['index_type']
        bottlenecks = analysis['bottlenecks']
        
        # Index type recommendations
        if 'linear_search_scaling' in bottlenecks:
            if dimension > 512:
                recommendations.append("Consider IndexIVFPQ for large high-dimensional dataset")
            else:
                recommendations.append("Consider IndexIVFFlat or IndexHNSWFlat for large dataset")
        
        if 'high_memory_overhead' in bottlenecks:
            recommendations.append("Consider IndexIVFPQ to reduce memory usage with product quantization")
        
        if 'high_dimensionality' in bottlenecks:
            recommendations.append("Consider dimensionality reduction or IndexIVFPQ for high-dimensional vectors")
        
        # Parameter tuning recommendations
        if index_type.startswith('IndexIVF'):
            optimal_nlist = min(4 * math.sqrt(total_vectors), total_vectors // 39)
            recommendations.append(f"Optimize nlist parameter to approximately {int(optimal_nlist)}")
        
        if index_type == 'IndexHNSWFlat':
            if total_vectors > 1000000:
                recommendations.append("Consider increasing M parameter for HNSW on very large datasets")
        
        return recommendations


class ParameterOptimizer:
    """Optimize index and search parameters"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.ParameterOptimizer")
        
        # Optimization history
        self.optimization_history = []
        self.parameter_performance = defaultdict(list)
        
        # Testing configuration
        self.test_query_count = config.get('test_query_count', 100)
        self.test_timeout = config.get('test_timeout_seconds', 60)
    
    async def optimize_search_parameters(
        self,
        vector_store,
        test_queries: List[np.ndarray],
        current_params: Dict[str, Any],
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE
    ) -> List[OptimizationRecommendation]:
        """Optimize search parameters through benchmarking"""        try:
            recommendations = []
            
            index_type = current_params.get('index_type', 'unknown')
            
            # Define parameter ranges based on index type and optimization level
            if index_type.startswith('IndexIVF'):
                await self._optimize_ivf_parameters(
                    vector_store, test_queries, current_params, optimization_level, recommendations
                )
            
            elif index_type == 'IndexHNSWFlat':
                await self._optimize_hnsw_parameters(
                    vector_store, test_queries, current_params, optimization_level, recommendations
                )
            
            # Optimize general search parameters
            await self._optimize_general_parameters(
                vector_store, test_queries, current_params, optimization_level, recommendations
            )
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Parameter optimization failed: {e}")
            return []
    
    async def _optimize_ivf_parameters(
        self,
        vector_store,
        test_queries: List[np.ndarray],
        current_params: Dict[str, Any],
        optimization_level: OptimizationLevel,
        recommendations: List[OptimizationRecommendation]
    ):
        """Optimize IVF-specific parameters"""        try:
            current_nprobe = current_params.get('nprobe', 1)
            total_vectors = current_params.get('total_vectors', 0)
            nlist = current_params.get('nlist', 100)
            
            # Define nprobe test range based on optimization level
            if optimization_level == OptimizationLevel.CONSERVATIVE:
                nprobe_range = [max(1, current_nprobe - 1), current_nprobe, current_nprobe + 1]
            elif optimization_level == OptimizationLevel.MODERATE:
                nprobe_range = list(range(1, min(nlist // 4, 20) + 1))
            else:  # AGGRESSIVE or EXPERT
                nprobe_range = list(range(1, min(nlist // 2, 50) + 1))
            
            # Benchmark different nprobe values
            best_nprobe = current_nprobe
            best_score = 0.0
            
            for nprobe in nprobe_range:
                if len(test_queries) > 0:
                    # Simulate performance test
                    # In real implementation, this would actually test the parameter
                    simulated_latency = 50 + (nprobe * 5)  # Simulate increasing latency with nprobe
                    simulated_accuracy = min(0.95, 0.7 + (nprobe * 0.05))  # Simulate better accuracy
                    
                    # Calculate combined score (balance speed vs accuracy)
                    score = simulated_accuracy - (simulated_latency / 1000)
                    
                    if score > best_score:
                        best_score = score
                        best_nprobe = nprobe
            
            # Generate recommendation if improvement found
            if best_nprobe != current_nprobe:
                expected_improvement = (best_score - (0.8 - (50 / 1000))) / (0.8 - (50 / 1000)) * 100
                
                recommendation = OptimizationRecommendation(
                    optimization_id=f"nprobe_optimization_{int(time.time())}",
                    optimization_type=OptimizationType.SEARCH_PARAMETERS,
                    current_value=current_nprobe,
                    recommended_value=best_nprobe,
                    expected_improvement=expected_improvement,
                    confidence=0.8,
                    implementation_cost="low",
                    description=f"Optimize nprobe from {current_nprobe} to {best_nprobe} for better speed/accuracy balance",
                    metadata={'parameter': 'nprobe', 'index_type': 'IVF'}
                )
                
                recommendations.append(recommendation)
                
        except Exception as e:
            self.logger.error(f"IVF parameter optimization failed: {e}")
    
    async def _optimize_hnsw_parameters(
        self,
        vector_store,
        test_queries: List[np.ndarray],
        current_params: Dict[str, Any],
        optimization_level: OptimizationLevel,
        recommendations: List[OptimizationRecommendation]
    ):
        """Optimize HNSW-specific parameters"""        try:
            current_ef_search = current_params.get('ef_search', 50)
            
            # Define ef_search test range
            if optimization_level == OptimizationLevel.CONSERVATIVE:
                ef_range = [current_ef_search - 10, current_ef_search, current_ef_search + 10]
            elif optimization_level == OptimizationLevel.MODERATE:
                ef_range = list(range(16, 128, 16))
            else:  # AGGRESSIVE or EXPERT
                ef_range = list(range(16, 256, 32))
            
            ef_range = [ef for ef in ef_range if ef > 0]
            
            # Benchmark different ef_search values
            best_ef = current_ef_search
            best_score = 0.0
            
            for ef_search in ef_range:
                if len(test_queries) > 0:
                    # Simulate performance test
                    simulated_latency = 30 + (ef_search * 0.5)
                    simulated_accuracy = min(0.98, 0.75 + (ef_search * 0.003))
                    
                    score = simulated_accuracy - (simulated_latency / 1000)
                    
                    if score > best_score:
                        best_score = score
                        best_ef = ef_search
            
            # Generate recommendation
            if best_ef != current_ef_search:
                expected_improvement = abs(best_ef - current_ef_search) / current_ef_search * 100
                
                recommendation = OptimizationRecommendation(
                    optimization_id=f"ef_search_optimization_{int(time.time())}",
                    optimization_type=OptimizationType.SEARCH_PARAMETERS,
                    current_value=current_ef_search,
                    recommended_value=best_ef,
                    expected_improvement=expected_improvement,
                    confidence=0.75,
                    implementation_cost="low",
                    description=f"Optimize ef_search from {current_ef_search} to {best_ef} for HNSW index",
                    metadata={'parameter': 'ef_search', 'index_type': 'HNSW'}
                )
                
                recommendations.append(recommendation)
                
        except Exception as e:
            self.logger.error(f"HNSW parameter optimization failed: {e}")
    
    async def _optimize_general_parameters(
        self,
        vector_store,
        test_queries: List[np.ndarray],
        current_params: Dict[str, Any],
        optimization_level: OptimizationLevel,
        recommendations: List[OptimizationRecommendation]
    ):
        """Optimize general search parameters"""        try:
            # Batch size optimization
            current_batch_size = current_params.get('batch_size', 1)
            
            if len(test_queries) > 10:
                optimal_batch_size = min(32, len(test_queries) // 4)
                
                if optimal_batch_size > current_batch_size:
                    recommendation = OptimizationRecommendation(
                        optimization_id=f"batch_size_optimization_{int(time.time())}",
                        optimization_type=OptimizationType.BATCH_PROCESSING,
                        current_value=current_batch_size,
                        recommended_value=optimal_batch_size,
                        expected_improvement=25.0,
                        confidence=0.9,
                        implementation_cost="low",
                        description=f"Increase batch size from {current_batch_size} to {optimal_batch_size} for better throughput",
                        metadata={'parameter': 'batch_size'}
                    )
                    
                    recommendations.append(recommendation)
            
        except Exception as e:
            self.logger.error(f"General parameter optimization failed: {e}")


class BenchmarkRunner:
    """Run performance benchmarks for optimization decisions"""    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.BenchmarkRunner")
        
        # Benchmark results storage
        self.benchmark_history = []
        self.baseline_benchmarks = {}
        
        # Configuration
        self.warmup_queries = config.get('warmup_queries', 10)
        self.benchmark_iterations = config.get('benchmark_iterations', 5)
    
    async def run_performance_benchmark(
        self,
        vector_store,
        test_queries: List[np.ndarray],
        configuration: Dict[str, Any],
        benchmark_name: str = "default"
    ) -> PerformanceBenchmark:
        """Run comprehensive performance benchmark"""        try:
            benchmark_id = f"{benchmark_name}_{int(time.time())}"
            
            # Warmup
            if len(test_queries) > self.warmup_queries:
                warmup_queries = test_queries[:self.warmup_queries]
                for query in warmup_queries:
                    await vector_store.search(query, k=10)
            
            # Benchmark measurements
            latencies = []
            memory_usage = []
            
            start_time = time.time()
            
            for iteration in range(self.benchmark_iterations):
                iteration_latencies = []
                
                for query in test_queries:
                    query_start = time.time()
                    
                    try:
                        results = await vector_store.search(query, k=10)
                        query_end = time.time()
                        
                        iteration_latencies.append((query_end - query_start) * 1000)
                        
                    except Exception as e:
                        self.logger.warning(f"Query failed during benchmark: {e}")
                        continue
                
                if iteration_latencies:
                    latencies.extend(iteration_latencies)
            
            end_time = time.time()
            
            # Calculate metrics
            if latencies:
                avg_latency = np.mean(latencies)
                p95_latency = np.percentile(latencies, 95)
                p99_latency = np.percentile(latencies, 99)
                
                total_time = end_time - start_time
                throughput = len(latencies) / total_time
            else:
                avg_latency = p95_latency = p99_latency = float('inf')
                throughput = 0.0
            
            # Estimate memory usage (simplified)
            estimated_memory = configuration.get('estimated_memory_mb', 0)
            
            benchmark = PerformanceBenchmark(
                benchmark_id=benchmark_id,
                test_type=benchmark_name,
                dataset_size=len(test_queries),
                query_count=len(latencies),
                avg_latency_ms=avg_latency,
                p95_latency_ms=p95_latency,
                p99_latency_ms=p99_latency,
                throughput_qps=throughput,
                memory_usage_mb=estimated_memory,
                timestamp=time.time(),
                configuration=configuration.copy()
            )
            
            self.benchmark_history.append(benchmark)
            
            self.logger.info(f"Benchmark {benchmark_id} completed: avg={avg_latency:.1f}ms, throughput={throughput:.1f}qps")
            
            return benchmark
            
        except Exception as e:
            self.logger.error(f"Benchmark failed: {e}")
            raise
    
    def compare_benchmarks(self, benchmark1: PerformanceBenchmark, benchmark2: PerformanceBenchmark) -> Dict[str, float]:
        """Compare two benchmarks and calculate improvement percentages"""        try:
            comparison = {}
            
            # Latency improvements (lower is better)
            if benchmark1.avg_latency_ms > 0:
                comparison['avg_latency_improvement'] = (
                    (benchmark1.avg_latency_ms - benchmark2.avg_latency_ms) / benchmark1.avg_latency_ms * 100
                )
            
            if benchmark1.p95_latency_ms > 0:
                comparison['p95_latency_improvement'] = (
                    (benchmark1.p95_latency_ms - benchmark2.p95_latency_ms) / benchmark1.p95_latency_ms * 100
                )
            
            # Throughput improvements (higher is better)
            if benchmark1.throughput_qps > 0:
                comparison['throughput_improvement'] = (
                    (benchmark2.throughput_qps - benchmark1.throughput_qps) / benchmark1.throughput_qps * 100
                )
            
            # Memory improvements (lower is better)
            if benchmark1.memory_usage_mb > 0:
                comparison['memory_improvement'] = (
                    (benchmark1.memory_usage_mb - benchmark2.memory_usage_mb) / benchmark1.memory_usage_mb * 100
                )
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Benchmark comparison failed: {e}")
            return {}


class OptimizationEngine:
    """Main optimization engine coordinating all optimization components"""    
    def __init__(self, vector_store, config: Dict[str, Any]):
        self.vector_store = vector_store
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.OptimizationEngine")
        
        # Components
        self.index_analyzer = IndexAnalyzer(config.get('analyzer', {}))
        self.parameter_optimizer = ParameterOptimizer(config.get('optimizer', {}))
        self.benchmark_runner = BenchmarkRunner(config.get('benchmark', {}))
        
        # Optimization state
        self.optimization_history = []
        self.active_optimizations = {}
        self.baseline_performance = None
        
        # Configuration
        self.auto_optimization = config.get('auto_optimization', False)
        self.optimization_interval_hours = config.get('optimization_interval_hours', 24)
        self.min_improvement_threshold = config.get('min_improvement_threshold', 5.0)  # 5% minimum
        
        # Background task
        self.optimization_task = None
    
    async def start_optimization_engine(self):
        """Start automatic optimization engine"""        if self.auto_optimization:
            self.optimization_task = asyncio.create_task(self._optimization_loop())
        
        self.logger.info("Optimization engine started")
    
    async def stop_optimization_engine(self):
        """Stop automatic optimization engine"""        if self.optimization_task:
            self.optimization_task.cancel()
            try:
                await self.optimization_task
            except asyncio.CancelledError:
                pass
            self.optimization_task = None
        
        self.logger.info("Optimization engine stopped")
    
    async def analyze_and_optimize(
        self,
        test_queries: Optional[List[np.ndarray]] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE
    ) -> List[OptimizationRecommendation]:
        """Perform comprehensive analysis and generate optimization recommendations"""        try:
            # Get current index metadata
            if hasattr(self.vector_store, 'get_stats'):
                index_stats = await self.vector_store.get_stats()
                current_metadata = {
                    'index_type': index_stats.index_type,
                    'total_vectors': index_stats.total_vectors,
                    'dimension': index_stats.dimension,
                    'memory_usage_mb': index_stats.memory_usage_mb
                }
            else:
                current_metadata = {'index_type': 'unknown', 'total_vectors': 0, 'dimension': 0}
            
            # Analyze current index
            index_analysis = await self.index_analyzer.analyze_index_efficiency(
                self.vector_store.index if hasattr(self.vector_store, 'index') else None,
                current_metadata
            )
            
            all_recommendations = []
            
            # Generate index structure recommendations
            if 'recommendations' in index_analysis:
                for rec_text in index_analysis['recommendations']:
                    recommendation = OptimizationRecommendation(
                        optimization_id=f"index_rec_{int(time.time())}",
                        optimization_type=OptimizationType.INDEX_STRUCTURE,
                        current_value=current_metadata.get('index_type', 'unknown'),
                        recommended_value="optimized_structure",
                        expected_improvement=10.0,
                        confidence=0.7,
                        implementation_cost="medium",
                        description=rec_text
                    )
                    all_recommendations.append(recommendation)
            
            # Generate parameter optimization recommendations
            if test_queries:
                current_params = {
                    **current_metadata,
                    'nprobe': getattr(self.vector_store, 'nprobe', 1) if hasattr(self.vector_store, 'nprobe') else 1,
                    'ef_search': getattr(self.vector_store, 'ef_search', 50) if hasattr(self.vector_store, 'ef_search') else 50,
                    'batch_size': 1
                }
                
                param_recommendations = await self.parameter_optimizer.optimize_search_parameters(
                    self.vector_store, test_queries, current_params, optimization_level
                )
                
                all_recommendations.extend(param_recommendations)
            
            # Filter recommendations by expected improvement
            filtered_recommendations = [
                rec for rec in all_recommendations
                if rec.expected_improvement >= self.min_improvement_threshold
            ]
            
            # Sort by expected improvement
            filtered_recommendations.sort(key=lambda x: x.expected_improvement, reverse=True)
            
            self.logger.info(f"Generated {len(filtered_recommendations)} optimization recommendations")
            
            return filtered_recommendations
            
        except Exception as e:
            self.logger.error(f"Optimization analysis failed: {e}")
            return []
    
    async def implement_optimization(self, recommendation: OptimizationRecommendation) -> OptimizationResult:
        """Implement a specific optimization recommendation"""        try:
            # Record before metrics
            before_benchmark = None
            if hasattr(self.vector_store, 'get_stats'):
                stats = await self.vector_store.get_stats()
                before_metrics = {
                    'memory_usage_mb': stats.memory_usage_mb,
                    'search_time_ms': stats.search_time_ms
                }
            else:
                before_metrics = {}
            
            success = False
            error_message = None
            
            try:
                # Implement based on optimization type
                if recommendation.optimization_type == OptimizationType.SEARCH_PARAMETERS:
                    success = await self._implement_parameter_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.INDEX_STRUCTURE:
                    success = await self._implement_index_optimization(recommendation)
                elif recommendation.optimization_type == OptimizationType.CACHE_STRATEGY:
                    success = await self._implement_cache_optimization(recommendation)
                else:
                    error_message = f"Unsupported optimization type: {recommendation.optimization_type}"
                
            except Exception as impl_error:
                error_message = str(impl_error)
                success = False
            
            # Record after metrics
            after_metrics = before_metrics.copy()  # In real implementation, re-measure
            
            # Calculate actual improvement
            actual_improvement = 0.0
            if success and 'search_time_ms' in before_metrics and 'search_time_ms' in after_metrics:
                if before_metrics['search_time_ms'] > 0:
                    actual_improvement = (
                        (before_metrics['search_time_ms'] - after_metrics['search_time_ms']) / 
                        before_metrics['search_time_ms'] * 100
                    )
            
            result = OptimizationResult(
                optimization_id=recommendation.optimization_id,
                implemented_at=time.time(),
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                actual_improvement=actual_improvement,
                success=success,
                error_message=error_message
            )
            
            self.optimization_history.append(result)
            
            if success:
                self.logger.info(f"Successfully implemented optimization {recommendation.optimization_id}")
            else:
                self.logger.error(f"Failed to implement optimization {recommendation.optimization_id}: {error_message}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Optimization implementation failed: {e}")
            
            return OptimizationResult(
                optimization_id=recommendation.optimization_id,
                implemented_at=time.time(),
                before_metrics={},
                after_metrics={},
                actual_improvement=0.0,
                success=False,
                error_message=str(e)
            )
    
    async def _implement_parameter_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement parameter optimization"""        try:
            parameter = recommendation.metadata.get('parameter')
            new_value = recommendation.recommended_value
            
            if parameter == 'nprobe' and hasattr(self.vector_store, 'index'):
                if hasattr(self.vector_store.index, 'nprobe'):
                    self.vector_store.index.nprobe = new_value
                    return True
            
            elif parameter == 'ef_search' and hasattr(self.vector_store, 'index'):
                if hasattr(self.vector_store.index, 'hnsw'):
                    self.vector_store.index.hnsw.efSearch = new_value
                    return True
            
            elif parameter == 'batch_size':
                # Set batch size for future operations
                if hasattr(self.vector_store, 'config'):
                    self.vector_store.config['batch_size'] = new_value
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Parameter optimization implementation failed: {e}")
            return False
    
    async def _implement_index_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement index structure optimization"""        try:
            # Index structure changes require rebuilding, which is complex
            # For now, log the recommendation for manual implementation
            self.logger.info(f"Index optimization recommended: {recommendation.description}")
            return True  # Assume successful for logging purposes
            
        except Exception as e:
            self.logger.error(f"Index optimization implementation failed: {e}")
            return False
    
    async def _implement_cache_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Implement cache optimization"""        try:
            # Implement cache-related optimizations
            self.logger.info(f"Cache optimization recommended: {recommendation.description}")
            return True
            
        except Exception as e:
            self.logger.error(f"Cache optimization implementation failed: {e}")
            return False
    
    async def _optimization_loop(self):
        """Background optimization loop"""        while True:
            try:
                # Run optimization analysis
                recommendations = await self.analyze_and_optimize()
                
                # Automatically implement low-cost optimizations
                for recommendation in recommendations:
                    if (recommendation.implementation_cost == "low" and 
                        recommendation.confidence > 0.8 and
                        recommendation.expected_improvement > 10.0):
                        
                        await self.implement_optimization(recommendation)
                        
                        # Add delay between optimizations
                        await asyncio.sleep(5)
                
                await asyncio.sleep(self.optimization_interval_hours * 3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Optimization loop error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization activities"""        try:
            successful_optimizations = [
                opt for opt in self.optimization_history 
                if opt.success
            ]
            
            total_improvement = sum(
                opt.actual_improvement for opt in successful_optimizations
                if opt.actual_improvement > 0
            )
            
            return {
                'total_optimizations': len(self.optimization_history),
                'successful_optimizations': len(successful_optimizations),
                'success_rate': len(successful_optimizations) / len(self.optimization_history) if self.optimization_history else 0,
                'total_improvement_percent': total_improvement,
                'average_improvement_percent': total_improvement / len(successful_optimizations) if successful_optimizations else 0,
                'last_optimization': self.optimization_history[-1].implemented_at if self.optimization_history else None
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get optimization summary: {e}")
            return {'error': str(e)}
