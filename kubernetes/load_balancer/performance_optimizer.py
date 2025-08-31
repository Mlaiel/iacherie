"""Performance Optimizer for Load Balancer - IA Influencer Agent Platform

Advanced performance optimization and auto-tuning for load balancing components,
providing intelligent resource allocation and dynamic scaling capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""
import asyncio
import logging
import time
import psutil
import statistics
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import deque, defaultdict
import json
import subprocess
import re
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pickle

logger = logging.getLogger(__name__)


class OptimizationType(Enum):
    """Performance optimization types"""
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    RESOURCE_EFFICIENCY = "resource_efficiency"
    COST_OPTIMIZATION = "cost_optimization"
    BALANCED = "balanced"


class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    STABLE = "stable"


@dataclass
class PerformanceMetrics:
    """Performance metrics for optimization"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    network_io: float
    disk_io: float
    requests_per_second: float
    avg_response_time: float
    error_rate: float
    active_connections: int
    queue_length: int
    throughput_mbps: float


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    component: str
    optimization_type: OptimizationType
    current_value: Any
    recommended_value: Any
    expected_improvement: float
    confidence_score: float
    priority: int  # 1 = highest, 10 = lowest
    reason: str
    implementation_complexity: str  # low, medium, high


@dataclass
class ScalingRecommendation:
    """Service scaling recommendation"""
    service_name: str
    current_instances: int
    recommended_instances: int
    scaling_direction: ScalingDirection
    urgency: int  # 1 = immediate, 10 = low priority
    reason: str
    expected_load_change: float
    cost_impact: float


class PerformanceOptimizer:
    """
    Enterprise Performance Optimizer for Load Balancer
    
    Provides intelligent performance optimization, auto-tuning,
    and predictive scaling for the IA Influencer Agent platform's
    load balancing infrastructure.
    """
    
    def __init__(self, optimization_type: OptimizationType = OptimizationType.BALANCED):
        self.optimization_type = optimization_type
        
        # Performance monitoring
        self.metrics_history: deque = deque(maxlen=2880)  # 48 hours @ 1min intervals
        self.service_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1440))
        
        # Machine learning models
        self.load_predictor = None
        self.scaler = StandardScaler()
        self.model_trained = False
        
        # Optimization state
        self.current_recommendations: List[OptimizationRecommendation] = []
        self.scaling_recommendations: List[ScalingRecommendation] = []
        self.optimization_history: deque = deque(maxlen=100)
        
        # Configuration
        self.optimization_interval = 300  # 5 minutes
        self.prediction_window = 3600  # 1 hour ahead
        self.min_data_points = 60  # Minimum data for predictions
        
        # Thresholds
        self.cpu_high_threshold = 0.8
        self.cpu_low_threshold = 0.3
        self.memory_high_threshold = 0.85
        self.memory_low_threshold = 0.4
        self.response_time_threshold = 2.0  # seconds
        self.error_rate_threshold = 0.05  # 5%
        
        # Background tasks
        self.optimizer_task = None
        self.predictor_task = None
        self.is_optimizing = False
        
        logger.info(f"Performance Optimizer initialized with {optimization_type.value} mode")
    
    async def initialize(self) -> None:
        """Initialize performance optimizer"""
        try:
            logger.info("Initializing Performance Optimizer...")
            
            # Load historical data if available
            await self._load_historical_data()
            
            # Initialize ML models
            await self._initialize_ml_models()
            
            # Configure optimization parameters
            await self._configure_optimization_parameters()
            
            logger.info("Performance Optimizer initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Performance Optimizer: {e}")
            raise
    
    async def _load_historical_data(self) -> None:
        """Load historical performance data"""
        try:
            # Try to load from file
            data_file = "/var/lib/ia-influencer/performance_data.json"
            try:
                with open(data_file, 'r') as f:
                    historical_data = json.load(f)
                
                # Convert to metrics objects
                for entry in historical_data.get("metrics", []):
                    metrics = PerformanceMetrics(
                        timestamp=datetime.fromisoformat(entry["timestamp"]),
                        cpu_usage=entry["cpu_usage"],
                        memory_usage=entry["memory_usage"],
                        network_io=entry["network_io"],
                        disk_io=entry["disk_io"],
                        requests_per_second=entry["requests_per_second"],
                        avg_response_time=entry["avg_response_time"],
                        error_rate=entry["error_rate"],
                        active_connections=entry["active_connections"],
                        queue_length=entry["queue_length"],
                        throughput_mbps=entry["throughput_mbps"]
                    )
                    self.metrics_history.append(metrics)
                
                logger.info(f"Loaded {len(self.metrics_history)} historical data points")
                
            except FileNotFoundError:
                logger.info("No historical data found, starting fresh")
            except Exception as e:
                logger.warning(f"Failed to load historical data: {e}")
                
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
    
    async def _initialize_ml_models(self) -> None:
        """Initialize machine learning models"""
        try:
            # Initialize load prediction model
            self.load_predictor = LinearRegression()
            
            # Try to load pre-trained model
            model_file = "/var/lib/ia-influencer/load_predictor.pkl"
            try:
                with open(model_file, 'rb') as f:
                    model_data = pickle.load(f)
                    self.load_predictor = model_data['model']
                    self.scaler = model_data['scaler']
                    self.model_trained = True
                    logger.info("Loaded pre-trained load prediction model")
            except FileNotFoundError:
                logger.info("No pre-trained model found, will train with new data")
            except Exception as e:
                logger.warning(f"Failed to load pre-trained model: {e}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ML models: {e}")
    
    async def _configure_optimization_parameters(self) -> None:
        """Configure optimization parameters based on type"""
        if self.optimization_type == OptimizationType.THROUGHPUT:
            # Prioritize throughput over latency
            self.cpu_high_threshold = 0.9
            self.response_time_threshold = 5.0
            
        elif self.optimization_type == OptimizationType.LATENCY:
            # Prioritize low latency
            self.cpu_high_threshold = 0.6
            self.response_time_threshold = 1.0
            
        elif self.optimization_type == OptimizationType.RESOURCE_EFFICIENCY:
            # Maximize resource utilization
            self.cpu_high_threshold = 0.85
            self.cpu_low_threshold = 0.5
            
        elif self.optimization_type == OptimizationType.COST_OPTIMIZATION:
            # Minimize resource usage
            self.cpu_high_threshold = 0.7
            self.cpu_low_threshold = 0.2
            
        # BALANCED mode uses default values
        
        logger.info(f"Optimization parameters configured for {self.optimization_type.value}")
    
    async def start_optimization(self) -> None:
        """Start performance optimization"""
        if self.is_optimizing:
            logger.warning("Performance optimization already running")
            return
        
        self.is_optimizing = True
        self.optimizer_task = asyncio.create_task(self._optimization_loop())
        self.predictor_task = asyncio.create_task(self._prediction_loop())
        
        logger.info("Performance optimization started")
    
    async def stop_optimization(self) -> None:
        """Stop performance optimization"""
        self.is_optimizing = False
        
        if self.optimizer_task:
            self.optimizer_task.cancel()
            try:
                await self.optimizer_task
            except asyncio.CancelledError:
                pass
        
        if self.predictor_task:
            self.predictor_task.cancel()
            try:
                await self.predictor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Performance optimization stopped")
    
    async def _optimization_loop(self) -> None:
        """Main optimization loop"""
        while self.is_optimizing:
            try:
                # Collect current metrics
                await self._collect_metrics()
                
                # Generate optimization recommendations
                await self._generate_recommendations()
                
                # Apply automatic optimizations
                await self._apply_optimizations()
                
                # Train ML models with new data
                await self._train_models()
                
                # Save performance data
                await self._save_performance_data()
                
                # Sleep for optimization interval
                await asyncio.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(self.optimization_interval)
    
    async def _prediction_loop(self) -> None:
        """Predictive analysis loop"""
        while self.is_optimizing:
            try:
                # Generate load predictions
                predictions = await self._predict_future_load()
                
                # Generate scaling recommendations
                await self._generate_scaling_recommendations(predictions)
                
                # Sleep for longer interval (predictions are less frequent)
                await asyncio.sleep(self.optimization_interval * 2)
                
            except Exception as e:
                logger.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(self.optimization_interval * 2)
    
    async def _collect_metrics(self) -> None:
        """Collect current performance metrics"""
        try:
            current_time = datetime.now()
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            network = psutil.net_io_counters()
            disk = psutil.disk_io_counters()
            
            # Calculate network I/O rate
            network_io = 0.0
            if hasattr(self, '_last_network_bytes'):
                time_diff = 1.0  # 1 second interval
                bytes_diff = (network.bytes_sent + network.bytes_recv) - self._last_network_bytes
                network_io = bytes_diff / (1024 * 1024) / time_diff  # MB/s
            
            self._last_network_bytes = network.bytes_sent + network.bytes_recv
            
            # Calculate disk I/O rate
            disk_io = 0.0
            if hasattr(self, '_last_disk_bytes'):
                bytes_diff = (disk.read_bytes + disk.write_bytes) - self._last_disk_bytes
                disk_io = bytes_diff / (1024 * 1024) / 1.0  # MB/s
            
            self._last_disk_bytes = disk.read_bytes + disk.write_bytes
            
            # Application metrics (would be collected from monitoring system)
            # For now, using synthetic data
            requests_per_second = self._estimate_requests_per_second()
            avg_response_time = self._estimate_response_time()
            error_rate = self._estimate_error_rate()
            active_connections = self._estimate_active_connections()
            queue_length = self._estimate_queue_length()
            throughput_mbps = network_io * 8  # Convert to Mbps
            
            # Create metrics object
            metrics = PerformanceMetrics(
                timestamp=current_time,
                cpu_usage=cpu_percent / 100.0,
                memory_usage=memory.percent / 100.0,
                network_io=network_io,
                disk_io=disk_io,
                requests_per_second=requests_per_second,
                avg_response_time=avg_response_time,
                error_rate=error_rate,
                active_connections=active_connections,
                queue_length=queue_length,
                throughput_mbps=throughput_mbps
            )
            
            # Store metrics
            self.metrics_history.append(metrics)
            
            logger.debug(f"Collected metrics: CPU={cpu_percent:.1f}%, Mem={memory.percent:.1f}%, RPS={requests_per_second:.1f}")
            
        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")
    
    def _estimate_requests_per_second(self) -> float:
        """Estimate current requests per second"""
        # This would integrate with actual monitoring system
        # For now, using CPU-based estimation
        if len(self.metrics_history) > 0:
            latest = self.metrics_history[-1]
            base_rps = 100.0
            cpu_factor = latest.cpu_usage * 2.0
            return max(10.0, base_rps + cpu_factor)
        return 50.0
    
    def _estimate_response_time(self) -> float:
        """Estimate current average response time"""
        # This would integrate with actual monitoring system
        if len(self.metrics_history) > 0:
            latest = self.metrics_history[-1]
            base_time = 0.5
            cpu_penalty = latest.cpu_usage * 2.0
            memory_penalty = latest.memory_usage * 1.0
            return base_time + cpu_penalty + memory_penalty
        return 1.0
    
    def _estimate_error_rate(self) -> float:
        """Estimate current error rate"""
        # This would integrate with actual monitoring system
        if len(self.metrics_history) > 0:
            latest = self.metrics_history[-1]
            base_error_rate = 0.01
            resource_stress = (latest.cpu_usage + latest.memory_usage) / 2
            if resource_stress > 0.8:
                return base_error_rate + (resource_stress - 0.8) * 0.1
            return base_error_rate
        return 0.01
    
    def _estimate_active_connections(self) -> int:
        """Estimate current active connections"""
        try:
            # Get network connections
            connections = psutil.net_connections(kind='inet')
            established = len([c for c in connections if c.status == 'ESTABLISHED'])
            return established
        except Exception:
            return 100  # Default estimate
    
    def _estimate_queue_length(self) -> int:
        """Estimate current queue length"""
        # This would integrate with actual load balancer metrics
        if len(self.metrics_history) > 0:
            latest = self.metrics_history[-1]
            if latest.cpu_usage > 0.8:
                return int(latest.requests_per_second * 0.1)  # 10% of RPS in queue
        return 0
    
    async def _generate_recommendations(self) -> None:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            if len(self.metrics_history) < 10:  # Need minimum data
                return
            
            latest_metrics = list(self.metrics_history)[-10:]  # Last 10 minutes
            
            # CPU optimization
            avg_cpu = statistics.mean([m.cpu_usage for m in latest_metrics])
            if avg_cpu > self.cpu_high_threshold:
                recommendations.append(OptimizationRecommendation(
                    component="nginx",
                    optimization_type=OptimizationType.RESOURCE_EFFICIENCY,
                    current_value=f"worker_processes=auto",
                    recommended_value=f"worker_processes={psutil.cpu_count()}",
                    expected_improvement=0.15,
                    confidence_score=0.8,
                    priority=2,
                    reason="High CPU usage detected",
                    implementation_complexity="low"
                ))
            
            # Memory optimization
            avg_memory = statistics.mean([m.memory_usage for m in latest_metrics])
            if avg_memory > self.memory_high_threshold:
                recommendations.append(OptimizationRecommendation(
                    component="nginx",
                    optimization_type=OptimizationType.RESOURCE_EFFICIENCY,
                    current_value="worker_connections=4096",
                    recommended_value="worker_connections=2048",
                    expected_improvement=0.1,
                    confidence_score=0.7,
                    priority=3,
                    reason="High memory usage detected",
                    implementation_complexity="low"
                ))
            
            # Response time optimization
            avg_response_time = statistics.mean([m.avg_response_time for m in latest_metrics])
            if avg_response_time > self.response_time_threshold:
                recommendations.append(OptimizationRecommendation(
                    component="haproxy",
                    optimization_type=OptimizationType.LATENCY,
                    current_value="maxconn=2000",
                    recommended_value="maxconn=1500",
                    expected_improvement=0.2,
                    confidence_score=0.75,
                    priority=1,
                    reason="High response time detected",
                    implementation_complexity="medium"
                ))
            
            # Throughput optimization
            avg_throughput = statistics.mean([m.throughput_mbps for m in latest_metrics])
            if avg_throughput < 100 and avg_cpu < 0.6:  # Low throughput with available CPU
                recommendations.append(OptimizationRecommendation(
                    component="nginx",
                    optimization_type=OptimizationType.THROUGHPUT,
                    current_value="keepalive_timeout=65",
                    recommended_value="keepalive_timeout=30",
                    expected_improvement=0.1,
                    confidence_score=0.6,
                    priority=4,
                    reason="Low throughput with available resources",
                    implementation_complexity="low"
                ))
            
            # Error rate optimization
            avg_error_rate = statistics.mean([m.error_rate for m in latest_metrics])
            if avg_error_rate > self.error_rate_threshold:
                recommendations.append(OptimizationRecommendation(
                    component="circuit_breaker",
                    optimization_type=OptimizationType.RESOURCE_EFFICIENCY,
                    current_value="failure_threshold=5",
                    recommended_value="failure_threshold=3",
                    expected_improvement=0.3,
                    confidence_score=0.9,
                    priority=1,
                    reason="High error rate detected",
                    implementation_complexity="low"
                ))
            
            # Sort by priority
            recommendations.sort(key=lambda x: x.priority)
            
            self.current_recommendations = recommendations
            
            if recommendations:
                logger.info(f"Generated {len(recommendations)} optimization recommendations")
                for rec in recommendations[:3]:  # Log top 3
                    logger.info(f"  {rec.component}: {rec.reason} (Priority: {rec.priority})")
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
    
    async def _apply_optimizations(self) -> None:
        """Apply automatic optimizations"""
        try:
            applied_count = 0
            
            for recommendation in self.current_recommendations:
                # Only apply low-complexity, high-confidence optimizations automatically
                if (recommendation.implementation_complexity == "low" and 
                    recommendation.confidence_score > 0.8 and
                    recommendation.priority <= 3):
                    
                    # Apply the optimization
                    success = await self._apply_single_optimization(recommendation)
                    
                    if success:
                        applied_count += 1
                        
                        # Store optimization history
                        self.optimization_history.append({
                            "timestamp": datetime.now(),
                            "recommendation": recommendation,
                            "applied": True
                        })
                        
                        logger.info(f"Applied optimization: {recommendation.component} - {recommendation.reason}")
                    
                    # Limit to 3 optimizations per cycle to avoid instability
                    if applied_count >= 3:
                        break
            
            if applied_count > 0:
                logger.info(f"Applied {applied_count} automatic optimizations")
                
        except Exception as e:
            logger.error(f"Failed to apply optimizations: {e}")
    
    async def _apply_single_optimization(self, recommendation: OptimizationRecommendation) -> bool:
        """Apply a single optimization"""
        try:
            # This would implement actual configuration changes
            # For now, just log the action
            
            logger.info(f"Applying optimization to {recommendation.component}")
            logger.info(f"  Change: {recommendation.current_value} -> {recommendation.recommended_value}")
            logger.info(f"  Expected improvement: {recommendation.expected_improvement:.1%}")
            
            # Simulate applying the change
            await asyncio.sleep(0.1)  # Simulate configuration update
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply optimization {recommendation.component}: {e}")
            return False
    
    async def _predict_future_load(self) -> Dict[str, float]:
        """Predict future load using ML models"""
        try:
            if len(self.metrics_history) < self.min_data_points:
                return {}
            
            # Prepare data for prediction
            data = []
            for metrics in list(self.metrics_history)[-self.min_data_points:]:
                features = [
                    metrics.cpu_usage,
                    metrics.memory_usage,
                    metrics.network_io,
                    metrics.requests_per_second,
                    metrics.avg_response_time,
                    metrics.active_connections
                ]
                data.append(features)
            
            # Convert to numpy array
            X = np.array(data)
            
            # Train model if not trained
            if not self.model_trained and len(data) >= self.min_data_points:
                await self._train_models()
            
            predictions = {}
            
            if self.model_trained:
                # Prepare features for prediction
                recent_features = X[-1].reshape(1, -1)
                scaled_features = self.scaler.transform(recent_features)
                
                # Predict next hour's load
                prediction = self.load_predictor.predict(scaled_features)[0]
                
                predictions = {
                    "cpu_usage": max(0.0, min(1.0, prediction * 1.1)),  # Slight increase expected
                    "memory_usage": max(0.0, min(1.0, prediction * 1.05)),
                    "requests_per_second": max(0.0, prediction * 100),
                    "response_time": max(0.1, prediction * 2.0)
                }
                
                logger.debug(f"Load predictions: CPU={predictions['cpu_usage']:.1%}, RPS={predictions['requests_per_second']:.1f}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to predict future load: {e}")
            return {}
    
    async def _generate_scaling_recommendations(self, predictions: Dict[str, float]) -> None:
        """Generate scaling recommendations based on predictions"""
        try:
            recommendations = []
            
            if not predictions:
                return
            
            # Service scaling logic
            services = ["fingerprinting", "protection", "monetization", "ai_agent", "crawlers"]
            
            for service in services:
                current_instances = self._get_current_instances(service)
                
                # Determine scaling needs based on predicted load
                predicted_cpu = predictions.get("cpu_usage", 0.5)
                predicted_rps = predictions.get("requests_per_second", 100)
                
                # Calculate recommended instances
                if predicted_cpu > 0.8 or predicted_rps > 200:
                    # Scale up
                    recommended_instances = min(current_instances + 1, 5)  # Max 5 instances
                    scaling_direction = ScalingDirection.UP
                    urgency = 1 if predicted_cpu > 0.9 else 3
                    reason = f"High predicted load: CPU={predicted_cpu:.1%}, RPS={predicted_rps:.0f}"
                    
                elif predicted_cpu < 0.3 and predicted_rps < 50:
                    # Scale down
                    recommended_instances = max(current_instances - 1, 1)  # Min 1 instance
                    scaling_direction = ScalingDirection.DOWN
                    urgency = 5
                    reason = f"Low predicted load: CPU={predicted_cpu:.1%}, RPS={predicted_rps:.0f}"
                    
                else:
                    # Stay stable
                    recommended_instances = current_instances
                    scaling_direction = ScalingDirection.STABLE
                    urgency = 10
                    reason = "Predicted load within normal range"
                
                if recommended_instances != current_instances:
                    recommendations.append(ScalingRecommendation(
                        service_name=service,
                        current_instances=current_instances,
                        recommended_instances=recommended_instances,
                        scaling_direction=scaling_direction,
                        urgency=urgency,
                        reason=reason,
                        expected_load_change=predicted_rps - 100,  # Baseline 100 RPS
                        cost_impact=self._calculate_cost_impact(current_instances, recommended_instances)
                    ))
            
            # Sort by urgency
            recommendations.sort(key=lambda x: x.urgency)
            
            self.scaling_recommendations = recommendations
            
            if recommendations:
                logger.info(f"Generated {len(recommendations)} scaling recommendations")
                for rec in recommendations[:3]:  # Log top 3
                    logger.info(f"  {rec.service_name}: {rec.scaling_direction.value} to {rec.recommended_instances} instances")
            
        except Exception as e:
            logger.error(f"Failed to generate scaling recommendations: {e}")
    
    def _get_current_instances(self, service_name: str) -> int:
        """Get current number of instances for a service"""
        # This would integrate with orchestration system (Kubernetes, Docker Swarm, etc.)
        # Default values based on service type
        defaults = {
            "fingerprinting": 3,
            "protection": 2,
            "monetization": 2,
            "ai_agent": 2,
            "crawlers": 2
        }
        return defaults.get(service_name, 2)
    
    def _calculate_cost_impact(self, current_instances: int, recommended_instances: int) -> float:
        """Calculate cost impact of scaling change"""
        instance_cost = 50.0  # $50 per instance per month
        change = recommended_instances - current_instances
        return change * instance_cost
    
    async def _train_models(self) -> None:
        """Train machine learning models with available data"""
        try:
            if len(self.metrics_history) < self.min_data_points:
                return
            
            # Prepare training data
            features = []
            targets = []
            
            metrics_list = list(self.metrics_history)
            
            for i in range(len(metrics_list) - 1):
                current = metrics_list[i]
                next_metrics = metrics_list[i + 1]
                
                # Features: current state
                feature_vector = [
                    current.cpu_usage,
                    current.memory_usage,
                    current.network_io,
                    current.requests_per_second,
                    current.avg_response_time,
                    current.active_connections
                ]
                
                # Target: next period's CPU usage (simplified target)
                target = next_metrics.cpu_usage
                
                features.append(feature_vector)
                targets.append(target)
            
            if len(features) >= self.min_data_points:
                X = np.array(features)
                y = np.array(targets)
                
                # Scale features
                X_scaled = self.scaler.fit_transform(X)
                
                # Train model
                self.load_predictor.fit(X_scaled, y)
                self.model_trained = True
                
                # Save model
                await self._save_model()
                
                logger.info(f"Trained ML model with {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Failed to train models: {e}")
    
    async def _save_model(self) -> None:
        """Save trained ML model"""
        try:
            model_file = "/var/lib/ia-influencer/load_predictor.pkl"
            model_data = {
                'model': self.load_predictor,
                'scaler': self.scaler
            }
            
            with open(model_file, 'wb') as f:
                pickle.dump(model_data, f)
                
            logger.debug("ML model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save ML model: {e}")
    
    async def _save_performance_data(self) -> None:
        """Save performance data for persistence"""
        try:
            data_file = "/var/lib/ia-influencer/performance_data.json"
            
            # Convert last 100 metrics to JSON
            metrics_data = []
            for metrics in list(self.metrics_history)[-100:]:
                metrics_data.append({
                    "timestamp": metrics.timestamp.isoformat(),
                    "cpu_usage": metrics.cpu_usage,
                    "memory_usage": metrics.memory_usage,
                    "network_io": metrics.network_io,
                    "disk_io": metrics.disk_io,
                    "requests_per_second": metrics.requests_per_second,
                    "avg_response_time": metrics.avg_response_time,
                    "error_rate": metrics.error_rate,
                    "active_connections": metrics.active_connections,
                    "queue_length": metrics.queue_length,
                    "throughput_mbps": metrics.throughput_mbps
                })
            
            data = {
                "metrics": metrics_data,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(data_file, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.error(f"Failed to save performance data: {e}")
    
    async def get_optimization_status(self) -> Dict[str, Any]:
        """Get comprehensive optimization status"""
        try:
            # Calculate recent performance
            recent_metrics = list(self.metrics_history)[-10:] if self.metrics_history else []
            
            if recent_metrics:
                avg_cpu = statistics.mean([m.cpu_usage for m in recent_metrics])
                avg_memory = statistics.mean([m.memory_usage for m in recent_metrics])
                avg_response_time = statistics.mean([m.avg_response_time for m in recent_metrics])
                avg_error_rate = statistics.mean([m.error_rate for m in recent_metrics])
                avg_throughput = statistics.mean([m.throughput_mbps for m in recent_metrics])
            else:
                avg_cpu = avg_memory = avg_response_time = avg_error_rate = avg_throughput = 0.0
            
            return {
                "is_optimizing": self.is_optimizing,
                "optimization_type": self.optimization_type.value,
                "model_trained": self.model_trained,
                "data_points": len(self.metrics_history),
                "current_performance": {
                    "avg_cpu_usage": avg_cpu,
                    "avg_memory_usage": avg_memory,
                    "avg_response_time": avg_response_time,
                    "avg_error_rate": avg_error_rate,
                    "avg_throughput_mbps": avg_throughput
                },
                "current_recommendations": [
                    {
                        "component": rec.component,
                        "type": rec.optimization_type.value,
                        "priority": rec.priority,
                        "reason": rec.reason,
                        "expected_improvement": rec.expected_improvement,
                        "confidence_score": rec.confidence_score
                    } for rec in self.current_recommendations
                ],
                "scaling_recommendations": [
                    {
                        "service": rec.service_name,
                        "current_instances": rec.current_instances,
                        "recommended_instances": rec.recommended_instances,
                        "direction": rec.scaling_direction.value,
                        "urgency": rec.urgency,
                        "reason": rec.reason,
                        "cost_impact": rec.cost_impact
                    } for rec in self.scaling_recommendations
                ],
                "optimization_history_count": len(self.optimization_history),
                "optimization_interval": self.optimization_interval,
                "thresholds": {
                    "cpu_high": self.cpu_high_threshold,
                    "cpu_low": self.cpu_low_threshold,
                    "memory_high": self.memory_high_threshold,
                    "memory_low": self.memory_low_threshold,
                    "response_time": self.response_time_threshold,
                    "error_rate": self.error_rate_threshold
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get optimization status: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    async def manual_optimization(self, component: str, parameter: str, value: Any) -> bool:
        """Apply manual optimization"""
        try:
            logger.info(f"Applying manual optimization: {component}.{parameter} = {value}")
            
            # This would implement actual configuration changes
            # For now, just simulate and record
            
            recommendation = OptimizationRecommendation(
                component=component,
                optimization_type=OptimizationType.BALANCED,
                current_value="unknown",
                recommended_value=value,
                expected_improvement=0.0,
                confidence_score=1.0,  # Manual override
                priority=1,
                reason="Manual optimization",
                implementation_complexity="manual"
            )
            
            # Record in optimization history
            self.optimization_history.append({
                "timestamp": datetime.now(),
                "recommendation": recommendation,
                "applied": True,
                "manual": True
            })
            
            logger.info(f"Manual optimization applied: {component}.{parameter}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply manual optimization: {e}")
            return False
    
    async def shutdown(self) -> None:
        """Shutdown performance optimizer"""
        try:
            logger.info("Shutting down Performance Optimizer...")
            
            await self.stop_optimization()
            
            # Save final state
            await self._save_performance_data()
            if self.model_trained:
                await self._save_model()
            
            logger.info("Performance Optimizer shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during Performance Optimizer shutdown: {e}")
