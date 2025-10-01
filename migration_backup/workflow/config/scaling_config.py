"""
📈 SCALING CONFIGURATION - IA CHÉRIES ENTERPRISE PLATFORM

Ultra-advanced auto-scaling configuration with intelligent resource management
Performance Target: < 5ms scaling decisions

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIETARY SOFTWARE - COMMERCIAL USE PROHIBITED WITHOUT LICENSE
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import os
import psutil

logger = logging.getLogger(__name__)

class ScalingStrategy(Enum):
    """Scaling strategies"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    SCHEDULED = "scheduled"
    HYBRID = "hybrid"

class ResourceType(Enum):
    """Resource types for scaling"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    WORKERS = "workers"
    CONTAINERS = "containers"

@dataclass
class HorizontalScalingConfig:
    """Horizontal scaling configuration"""
    min_instances: int = 2
    max_instances: int = 20
    target_cpu_percent: float = 70.0
    target_memory_percent: float = 75.0
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 30.0
    scale_up_cooldown: int = 300  # seconds
    scale_down_cooldown: int = 600  # seconds
    scaling_factor: float = 1.5
    enable_predictive_scaling: bool = True

@dataclass
class VerticalScalingConfig:
    """Vertical scaling configuration"""
    min_cpu_cores: int = 1
    max_cpu_cores: int = 16
    min_memory_gb: int = 2
    max_memory_gb: int = 64
    cpu_step_size: int = 1
    memory_step_size_gb: int = 2
    enable_auto_resize: bool = True
    resize_cooldown: int = 900  # seconds
    cpu_utilization_threshold: float = 85.0
    memory_utilization_threshold: float = 90.0

@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration"""
    enable_auto_scaling: bool = True
    scaling_strategy: ScalingStrategy = ScalingStrategy.HYBRID
    monitoring_interval: int = 60  # seconds
    decision_interval: int = 300  # seconds
    metrics_window: int = 900  # seconds
    confidence_threshold: float = 0.8
    enable_cost_optimization: bool = True
    max_hourly_cost: float = 100.0

class ScalingConfig:
    """
    Enterprise scaling configuration manager
    Performance target: < 5ms scaling decisions
    """
    
    def __init__(self):
        self.horizontal_scaling = HorizontalScalingConfig()
        self.vertical_scaling = VerticalScalingConfig()
        self.auto_scaling = AutoScalingConfig()
        self._scaling_history: List[Dict[str, Any]] = []
        self._resource_predictions: Dict[str, Any] = {}
        self._cost_tracking: Dict[str, float] = {}
        self._current_instances: int = 2
        self._current_resources: Dict[str, float] = {}
        
        # Load configuration from environment
        self._load_from_environment()
        
        # Initialize resource monitoring
        self._initialize_resource_monitoring()
    
    def _load_from_environment(self):
        """Load scaling configuration from environment variables"""
        
        # Horizontal scaling
        self.horizontal_scaling.min_instances = int(os.getenv('SCALING_MIN_INSTANCES', self.horizontal_scaling.min_instances))
        self.horizontal_scaling.max_instances = int(os.getenv('SCALING_MAX_INSTANCES', self.horizontal_scaling.max_instances))
        self.horizontal_scaling.target_cpu_percent = float(os.getenv('SCALING_TARGET_CPU', self.horizontal_scaling.target_cpu_percent))
        
        # Auto-scaling
        self.auto_scaling.enable_auto_scaling = os.getenv('ENABLE_AUTO_SCALING', 'true').lower() == 'true'
        self.auto_scaling.monitoring_interval = int(os.getenv('SCALING_MONITOR_INTERVAL', self.auto_scaling.monitoring_interval))
        
        # Cost limits
        self.auto_scaling.max_hourly_cost = float(os.getenv('MAX_HOURLY_COST', self.auto_scaling.max_hourly_cost))
    
    def _initialize_resource_monitoring(self):
        """Initialize current resource state"""
        try:
            self._current_resources = {
                'cpu_cores': psutil.cpu_count(),
                'memory_gb': round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
                'cpu_percent': 0.0,
                'memory_percent': 0.0
            }
            self._current_instances = self.horizontal_scaling.min_instances
        except Exception as e:
            logger.error(f"Failed to initialize resource monitoring: {e}")
    
    async def configure_scaling_policies(self) -> Dict[str, Any]:
        """
        Configure comprehensive scaling policies
        Performance target: < 5ms
        """
        start_time = time.perf_counter()
        
        try:
            scaling_policies = {
                "horizontal_scaling": {
                    "instances": {
                        "min": self.horizontal_scaling.min_instances,
                        "max": self.horizontal_scaling.max_instances,
                        "current": self._current_instances
                    },
                    "thresholds": {
                        "cpu_scale_up": self.horizontal_scaling.scale_up_threshold,
                        "cpu_scale_down": self.horizontal_scaling.scale_down_threshold,
                        "memory_scale_up": 85.0,
                        "memory_scale_down": 40.0
                    },
                    "cooldown_periods": {
                        "scale_up": self.horizontal_scaling.scale_up_cooldown,
                        "scale_down": self.horizontal_scaling.scale_down_cooldown
                    },
                    "scaling_factor": self.horizontal_scaling.scaling_factor
                },
                "vertical_scaling": {
                    "cpu": {
                        "min_cores": self.vertical_scaling.min_cpu_cores,
                        "max_cores": self.vertical_scaling.max_cpu_cores,
                        "current_cores": self._current_resources.get('cpu_cores', 4),
                        "step_size": self.vertical_scaling.cpu_step_size
                    },
                    "memory": {
                        "min_gb": self.vertical_scaling.min_memory_gb,
                        "max_gb": self.vertical_scaling.max_memory_gb,
                        "current_gb": self._current_resources.get('memory_gb', 8),
                        "step_size_gb": self.vertical_scaling.memory_step_size_gb
                    },
                    "auto_resize": self.vertical_scaling.enable_auto_resize,
                    "thresholds": {
                        "cpu_utilization": self.vertical_scaling.cpu_utilization_threshold,
                        "memory_utilization": self.vertical_scaling.memory_utilization_threshold
                    }
                },
                "auto_scaling": {
                    "enabled": self.auto_scaling.enable_auto_scaling,
                    "strategy": self.auto_scaling.scaling_strategy.value,
                    "monitoring_interval": self.auto_scaling.monitoring_interval,
                    "decision_interval": self.auto_scaling.decision_interval,
                    "predictive_scaling": self.horizontal_scaling.enable_predictive_scaling
                },
                "cost_optimization": {
                    "enabled": self.auto_scaling.enable_cost_optimization,
                    "max_hourly_cost": self.auto_scaling.max_hourly_cost,
                    "current_hourly_cost": self._calculate_current_cost(),
                    "cost_efficiency_score": self._calculate_cost_efficiency()
                },
                "creator_economy_scaling": {
                    "content_processing": {
                        "scale_on_uploads": True,
                        "upload_threshold": 100,  # uploads per minute
                        "processing_queue_threshold": 500
                    },
                    "ai_processing": {
                        "scale_on_ai_load": True,
                        "ai_queue_threshold": 50,
                        "model_warm_up": True
                    },
                    "collaboration": {
                        "scale_on_active_sessions": True,
                        "session_threshold": 200,
                        "real_time_scaling": True
                    }
                }
            }
            
            duration = (time.perf_counter() - start_time) * 1000
            logger.info(f"Scaling policies configured in {duration:.2f}ms")
            
            return scaling_policies
            
        except Exception as e:
            logger.error(f"Failed to configure scaling policies: {e}")
            raise
    
    async def manage_auto_scaling_rules(self) -> Dict[str, Any]:
        """
        Manage comprehensive auto-scaling rules
        Performance target: < 8ms rule management
        """
        try:
            current_metrics = await self._collect_current_metrics()
            
            scaling_rules = {
                "cpu_based_rules": {
                    "scale_up": {
                        "condition": f"avg_cpu_percent > {self.horizontal_scaling.scale_up_threshold}",
                        "duration": "5m",
                        "action": "add_instance",
                        "max_instances": self.horizontal_scaling.max_instances,
                        "cooldown": self.horizontal_scaling.scale_up_cooldown
                    },
                    "scale_down": {
                        "condition": f"avg_cpu_percent < {self.horizontal_scaling.scale_down_threshold}",
                        "duration": "10m",
                        "action": "remove_instance",
                        "min_instances": self.horizontal_scaling.min_instances,
                        "cooldown": self.horizontal_scaling.scale_down_cooldown
                    }
                },
                "memory_based_rules": {
                    "scale_up": {
                        "condition": "avg_memory_percent > 85",
                        "duration": "3m",
                        "action": "add_instance",
                        "priority": "high"
                    },
                    "scale_down": {
                        "condition": "avg_memory_percent < 40",
                        "duration": "15m",
                        "action": "remove_instance",
                        "priority": "low"
                    }
                },
                "business_metric_rules": {
                    "content_upload_surge": {
                        "condition": "upload_rate > 100 per minute",
                        "action": "scale_processing_workers",
                        "scaling_factor": 2.0,
                        "max_workers": 20
                    },
                    "ai_processing_backlog": {
                        "condition": "ai_queue_size > 50",
                        "action": "scale_ai_workers",
                        "scaling_factor": 1.5,
                        "enable_gpu_scaling": True
                    },
                    "collaboration_activity": {
                        "condition": "active_sessions > 200",
                        "action": "scale_real_time_workers",
                        "scaling_factor": 1.3,
                        "enable_edge_scaling": True
                    }
                },
                "time_based_rules": {
                    "peak_hours": {
                        "schedule": "08:00-18:00 UTC",
                        "min_instances": self.horizontal_scaling.min_instances + 2,
                        "pre_scale": True,
                        "pre_scale_minutes": 15
                    },
                    "weekend_scaling": {
                        "schedule": "Saturday-Sunday",
                        "scaling_factor": 0.7,
                        "min_instances": max(1, self.horizontal_scaling.min_instances - 1)
                    }
                },
                "predictive_rules": {
                    "trend_based": {
                        "enabled": self.horizontal_scaling.enable_predictive_scaling,
                        "prediction_window": "1h",
                        "confidence_threshold": self.auto_scaling.confidence_threshold,
                        "lead_time": "10m"
                    },
                    "seasonal_patterns": {
                        "enabled": True,
                        "learning_period": "30d",
                        "pattern_confidence": 0.85
                    }
                }
            }
            
            # Add current rule states
            scaling_rules["current_state"] = {
                "cpu_percent": current_metrics.get("cpu_percent", 0),
                "memory_percent": current_metrics.get("memory_percent", 0),
                "active_instances": self._current_instances,
                "scaling_actions_today": len([
                    h for h in self._scaling_history 
                    if h.get("timestamp", 0) > time.time() - 86400
                ])
            }
            
            return scaling_rules
            
        except Exception as e:
            logger.error(f"Auto-scaling rules management failed: {e}")
            return {"error": str(e)}
    
    async def resource_demand_prediction(self) -> Dict[str, Any]:
        """
        Predict resource demand using ML-like algorithms
        Performance target: < 15ms prediction
        """
        try:
            historical_data = self._get_historical_metrics()
            
            # Simple trend analysis (in production, would use ML models)
            predictions = {
                "cpu_demand": {
                    "next_hour": self._predict_cpu_demand(historical_data, 3600),
                    "next_6_hours": self._predict_cpu_demand(historical_data, 21600),
                    "next_24_hours": self._predict_cpu_demand(historical_data, 86400),
                    "confidence": 0.85
                },
                "memory_demand": {
                    "next_hour": self._predict_memory_demand(historical_data, 3600),
                    "next_6_hours": self._predict_memory_demand(historical_data, 21600),
                    "next_24_hours": self._predict_memory_demand(historical_data, 86400),
                    "confidence": 0.82
                },
                "instance_demand": {
                    "next_hour": self._predict_instance_demand(historical_data, 3600),
                    "next_6_hours": self._predict_instance_demand(historical_data, 21600),
                    "next_24_hours": self._predict_instance_demand(historical_data, 86400),
                    "confidence": 0.78
                },
                "business_predictions": {
                    "content_upload_surge": {
                        "probability": 0.15,
                        "expected_time": "14:00-16:00 UTC",
                        "impact": "medium",
                        "recommended_action": "pre_scale_processing"
                    },
                    "collaboration_peak": {
                        "probability": 0.25,
                        "expected_time": "10:00-12:00 UTC",
                        "impact": "high",
                        "recommended_action": "pre_scale_real_time"
                    },
                    "ai_processing_load": {
                        "probability": 0.30,
                        "expected_time": "09:00-11:00 UTC",
                        "impact": "high",
                        "recommended_action": "warm_up_models"
                    }
                },
                "seasonal_patterns": {
                    "weekday_pattern": "Morning peak (09:00-11:00), Afternoon surge (14:00-16:00)",
                    "weekend_pattern": "Steady moderate load, 30% lower than weekdays",
                    "monthly_pattern": "Higher activity in first and last weeks",
                    "creator_activity_pattern": "Peak content creation on weekends"
                }
            }
            
            self._resource_predictions = predictions
            return predictions
            
        except Exception as e:
            logger.error(f"Resource demand prediction failed: {e}")
            return {"error": str(e)}
    
    def _predict_cpu_demand(self, historical_data: List[Dict], time_horizon: int) -> float:
        """Predict CPU demand for given time horizon"""
        if not historical_data:
            return 50.0  # Default prediction
        
        # Simple trend calculation
        recent_data = historical_data[-10:]  # Last 10 data points
        avg_cpu = sum(d.get("cpu_percent", 50) for d in recent_data) / len(recent_data)
        
        # Add some seasonality (simplified)
        current_hour = time.localtime().tm_hour
        if 9 <= current_hour <= 17:  # Business hours
            avg_cpu *= 1.2
        
        return min(100.0, avg_cpu)
    
    def _predict_memory_demand(self, historical_data: List[Dict], time_horizon: int) -> float:
        """Predict memory demand for given time horizon"""
        if not historical_data:
            return 45.0  # Default prediction
        
        recent_data = historical_data[-10:]
        avg_memory = sum(d.get("memory_percent", 45) for d in recent_data) / len(recent_data)
        
        # Memory tends to grow over time in long-running applications
        growth_factor = 1.05 if time_horizon > 3600 else 1.0
        
        return min(100.0, avg_memory * growth_factor)
    
    def _predict_instance_demand(self, historical_data: List[Dict], time_horizon: int) -> int:
        """Predict instance demand for given time horizon"""
        cpu_prediction = self._predict_cpu_demand(historical_data, time_horizon)
        memory_prediction = self._predict_memory_demand(historical_data, time_horizon)
        
        # Simple capacity planning
        required_instances = max(
            int(cpu_prediction / self.horizontal_scaling.target_cpu_percent),
            int(memory_prediction / 75.0),  # Target 75% memory usage
            self.horizontal_scaling.min_instances
        )
        
        return min(required_instances, self.horizontal_scaling.max_instances)
    
    async def scaling_performance_optimization(self) -> Dict[str, Any]:
        """
        Optimize scaling performance and efficiency
        Performance target: < 12ms optimization
        """
        try:
            optimization_results = {
                "scaling_efficiency": {
                    "average_scale_time": self._calculate_average_scale_time(),
                    "scaling_accuracy": self._calculate_scaling_accuracy(),
                    "resource_utilization": self._calculate_resource_utilization(),
                    "cost_efficiency": self._calculate_cost_efficiency()
                },
                "optimization_recommendations": {
                    "scaling_thresholds": self._recommend_threshold_adjustments(),
                    "cooldown_periods": self._recommend_cooldown_adjustments(),
                    "instance_types": self._recommend_instance_types(),
                    "cost_optimizations": self._recommend_cost_optimizations()
                },
                "performance_improvements": {
                    "faster_scaling": {
                        "pre_warmed_instances": True,
                        "instance_templates": True,
                        "container_optimization": True,
                        "parallel_scaling": True
                    },
                    "better_predictions": {
                        "ml_model_tuning": True,
                        "feature_engineering": True,
                        "ensemble_methods": True,
                        "feedback_loops": True
                    },
                    "resource_optimization": {
                        "right_sizing": True,
                        "spot_instances": True,
                        "reserved_capacity": True,
                        "auto_shutdown": True
                    }
                },
                "creator_economy_optimizations": {
                    "content_processing": {
                        "batch_optimization": True,
                        "queue_prioritization": True,
                        "format_specific_scaling": True,
                        "creator_tier_scaling": True
                    },
                    "ai_processing": {
                        "model_specific_scaling": True,
                        "gpu_optimization": True,
                        "batch_inference": True,
                        "model_caching": True
                    },
                    "collaboration": {
                        "session_aware_scaling": True,
                        "region_based_scaling": True,
                        "real_time_optimization": True,
                        "connection_pooling": True
                    }
                }
            }
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Scaling performance optimization failed: {e}")
            return {"error": str(e)}
    
    async def cost_aware_scaling(self) -> Dict[str, Any]:
        """
        Implement cost-aware scaling decisions
        Performance target: < 6ms cost calculation
        """
        try:
            current_cost = self._calculate_current_cost()
            
            cost_optimization = {
                "current_costs": {
                    "hourly_cost": current_cost,
                    "daily_projected": current_cost * 24,
                    "monthly_projected": current_cost * 24 * 30,
                    "cost_per_request": self._calculate_cost_per_request()
                },
                "cost_thresholds": {
                    "warning_threshold": self.auto_scaling.max_hourly_cost * 0.8,
                    "critical_threshold": self.auto_scaling.max_hourly_cost,
                    "budget_utilization": (current_cost / self.auto_scaling.max_hourly_cost) * 100
                },
                "cost_optimization_strategies": {
                    "spot_instances": {
                        "enabled": True,
                        "max_spot_percentage": 70,
                        "fallback_on_demand": True,
                        "estimated_savings": "40-60%"
                    },
                    "reserved_instances": {
                        "enabled": True,
                        "reservation_percentage": 30,
                        "term": "1_year",
                        "estimated_savings": "30-50%"
                    },
                    "right_sizing": {
                        "enabled": True,
                        "cpu_target_utilization": 70,
                        "memory_target_utilization": 75,
                        "estimated_savings": "15-25%"
                    },
                    "auto_shutdown": {
                        "enabled": True,
                        "idle_threshold": "10m",
                        "dev_environment_shutdown": True,
                        "estimated_savings": "20-40%"
                    }
                },
                "cost_aware_decisions": {
                    "prefer_vertical_scaling": current_cost > self.auto_scaling.max_hourly_cost * 0.7,
                    "enable_aggressive_downscaling": True,
                    "delay_non_critical_scaling": current_cost > self.auto_scaling.max_hourly_cost * 0.9,
                    "use_spot_instances": True
                },
                "budget_alerts": {
                    "50_percent_budget": current_cost > self.auto_scaling.max_hourly_cost * 0.5,
                    "80_percent_budget": current_cost > self.auto_scaling.max_hourly_cost * 0.8,
                    "100_percent_budget": current_cost >= self.auto_scaling.max_hourly_cost,
                    "projected_overspend": self._predict_budget_overspend()
                }
            }
            
            return cost_optimization
            
        except Exception as e:
            logger.error(f"Cost-aware scaling failed: {e}")
            return {"error": str(e)}
    
    async def scaling_event_monitoring(self) -> Dict[str, Any]:
        """
        Monitor scaling events and their impact
        Performance target: < 4ms monitoring
        """
        try:
            recent_events = self._scaling_history[-20:]  # Last 20 events
            
            monitoring_data = {
                "recent_scaling_events": recent_events,
                "scaling_statistics": {
                    "total_scale_ups": len([e for e in recent_events if e.get("action") == "scale_up"]),
                    "total_scale_downs": len([e for e in recent_events if e.get("action") == "scale_down"]),
                    "average_scale_time": self._calculate_average_scale_time(),
                    "scaling_frequency": len(recent_events) / max(1, len(recent_events) / 10),  # Events per hour
                    "scaling_success_rate": self._calculate_scaling_success_rate()
                },
                "performance_impact": {
                    "response_time_during_scaling": self._get_response_time_during_scaling(),
                    "availability_during_scaling": 99.8,  # Simulated
                    "error_rate_during_scaling": 0.1,  # Simulated
                    "user_experience_impact": "minimal"
                },
                "business_impact": {
                    "creator_satisfaction": self._calculate_creator_satisfaction_impact(),
                    "content_processing_delays": self._calculate_processing_delays(),
                    "collaboration_session_stability": 98.5,  # Simulated
                    "revenue_impact": self._calculate_revenue_impact()
                },
                "alerting_summary": {
                    "scaling_alerts_24h": 3,  # Simulated
                    "critical_scaling_issues": 0,
                    "resolved_issues": 2,
                    "pending_issues": 1
                }
            }
            
            return monitoring_data
            
        except Exception as e:
            logger.error(f"Scaling event monitoring failed: {e}")
            return {"error": str(e)}
    
    async def disaster_recovery_scaling(self) -> Dict[str, Any]:
        """
        Configure disaster recovery scaling procedures
        Performance target: < 10ms DR setup
        """
        try:
            dr_configuration = {
                "multi_region_setup": {
                    "primary_region": "us-east-1",
                    "secondary_regions": ["us-west-2", "eu-west-1"],
                    "cross_region_replication": True,
                    "failover_time_target": "< 5 minutes"
                },
                "disaster_scenarios": {
                    "region_failure": {
                        "detection_time": "< 30 seconds",
                        "failover_trigger": "automatic",
                        "scaling_action": "emergency_scale_up",
                        "target_capacity": "150% of normal"
                    },
                    "availability_zone_failure": {
                        "detection_time": "< 15 seconds",
                        "failover_trigger": "automatic",
                        "scaling_action": "redistribute_load",
                        "target_capacity": "120% in remaining AZs"
                    },
                    "service_degradation": {
                        "detection_time": "< 60 seconds",
                        "scaling_trigger": "aggressive_scale_up",
                        "scaling_factor": 2.0,
                        "monitoring_frequency": "10 seconds"
                    }
                },
                "emergency_scaling": {
                    "bypass_cost_limits": True,
                    "bypass_normal_thresholds": True,
                    "maximum_emergency_instances": 50,
                    "emergency_scaling_factor": 3.0,
                    "emergency_duration_limit": "2 hours"
                },
                "data_protection": {
                    "real_time_backup": True,
                    "cross_region_data_sync": True,
                    "point_in_time_recovery": True,
                    "backup_scaling": "automatic"
                },
                "communication_plan": {
                    "stakeholder_notifications": "immediate",
                    "status_page_updates": "automatic",
                    "creator_communications": "within 15 minutes",
                    "escalation_procedures": "defined"
                }
            }
            
            return dr_configuration
            
        except Exception as e:
            logger.error(f"Disaster recovery scaling configuration failed: {e}")
            return {"error": str(e)}
    
    async def _collect_current_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": 50.0,  # Simulated
                "active_connections": 150,  # Simulated
                "queue_size": 25  # Simulated
            }
        except Exception:
            return {}
    
    def _get_historical_metrics(self) -> List[Dict[str, Any]]:
        """Get historical metrics for prediction"""
        # Simulate historical data
        return [
            {"timestamp": time.time() - i * 300, "cpu_percent": 45 + (i % 10) * 2, "memory_percent": 60 + (i % 5)}
            for i in range(20)
        ]
    
    def _calculate_current_cost(self) -> float:
        """Calculate current hourly cost"""
        # Simplified cost calculation
        base_cost_per_instance = 0.50  # $0.50 per hour per instance
        return self._current_instances * base_cost_per_instance
    
    def _calculate_cost_efficiency(self) -> float:
        """Calculate cost efficiency score"""
        cost = self._calculate_current_cost()
        utilization = (self._current_resources.get('cpu_percent', 50) + 
                      self._current_resources.get('memory_percent', 50)) / 2
        
        if cost == 0:
            return 0.0
        
        efficiency = (utilization / 100) / cost * 100
        return min(100.0, efficiency)
    
    def _calculate_average_scale_time(self) -> float:
        """Calculate average time for scaling operations"""
        scale_times = [h.get("duration", 120) for h in self._scaling_history if "duration" in h]
        return sum(scale_times) / len(scale_times) if scale_times else 120.0
    
    def _calculate_scaling_accuracy(self) -> float:
        """Calculate scaling decision accuracy"""
        return 85.5  # Simulated accuracy percentage
    
    def _calculate_resource_utilization(self) -> float:
        """Calculate overall resource utilization"""
        return 72.3  # Simulated utilization percentage
    
    def _calculate_cost_per_request(self) -> float:
        """Calculate cost per request"""
        hourly_cost = self._calculate_current_cost()
        requests_per_hour = 10000  # Simulated
        return hourly_cost / requests_per_hour if requests_per_hour > 0 else 0.0
    
    def _predict_budget_overspend(self) -> bool:
        """Predict if budget will be exceeded"""
        current_cost = self._calculate_current_cost()
        daily_projected = current_cost * 24
        monthly_budget = self.auto_scaling.max_hourly_cost * 24 * 30
        return daily_projected * 30 > monthly_budget
    
    def _calculate_scaling_success_rate(self) -> float:
        """Calculate scaling operation success rate"""
        return 96.2  # Simulated success rate
    
    def _get_response_time_during_scaling(self) -> float:
        """Get average response time during scaling events"""
        return 180.5  # Simulated response time in ms
    
    def _calculate_creator_satisfaction_impact(self) -> float:
        """Calculate impact on creator satisfaction"""
        return 92.1  # Simulated satisfaction score
    
    def _calculate_processing_delays(self) -> float:
        """Calculate content processing delays"""
        return 2.3  # Simulated delay in seconds
    
    def _calculate_revenue_impact(self) -> float:
        """Calculate revenue impact of scaling decisions"""
        return 0.05  # Simulated revenue impact percentage
    
    def _recommend_threshold_adjustments(self) -> Dict[str, Any]:
        """Recommend scaling threshold adjustments"""
        return {
            "cpu_threshold": "Consider lowering to 75% for faster response",
            "memory_threshold": "Current levels optimal",
            "response_time_threshold": "Add response time based scaling"
        }
    
    def _recommend_cooldown_adjustments(self) -> Dict[str, Any]:
        """Recommend cooldown period adjustments"""
        return {
            "scale_up_cooldown": "Consider reducing to 4 minutes",
            "scale_down_cooldown": "Current 10 minutes is optimal"
        }
    
    def _recommend_instance_types(self) -> Dict[str, Any]:
        """Recommend optimal instance types"""
        return {
            "current": "m5.large",
            "recommended": "m5.xlarge for better cost efficiency",
            "alternative": "c5.large for CPU-intensive workloads"
        }
    
    def _recommend_cost_optimizations(self) -> List[str]:
        """Recommend cost optimization strategies"""
        return [
            "Enable spot instances for 60% of fleet",
            "Use reserved instances for baseline capacity",
            "Implement aggressive downscaling during off-peak hours",
            "Consider regional pricing differences"
        ]
    
    def record_scaling_event(self, action: str, reason: str, instances_before: int, instances_after: int):
        """Record a scaling event"""
        event = {
            "timestamp": time.time(),
            "action": action,
            "reason": reason,
            "instances_before": instances_before,
            "instances_after": instances_after,
            "duration": 0,  # Would be filled when event completes
            "success": True
        }
        self._scaling_history.append(event)
        self._current_instances = instances_after
    
    def export_config(self) -> Dict[str, Any]:
        """Export scaling configuration for external use"""
        return {
            "horizontal_scaling": {
                "min_instances": self.horizontal_scaling.min_instances,
                "max_instances": self.horizontal_scaling.max_instances,
                "current_instances": self._current_instances,
                "scaling_strategy": self.auto_scaling.scaling_strategy.value
            },
            "vertical_scaling": {
                "auto_resize_enabled": self.vertical_scaling.enable_auto_resize,
                "cpu_limits": {
                    "min": self.vertical_scaling.min_cpu_cores,
                    "max": self.vertical_scaling.max_cpu_cores
                },
                "memory_limits": {
                    "min": self.vertical_scaling.min_memory_gb,
                    "max": self.vertical_scaling.max_memory_gb
                }
            },
            "auto_scaling": {
                "enabled": self.auto_scaling.enable_auto_scaling,
                "monitoring_interval": self.auto_scaling.monitoring_interval,
                "cost_optimization": self.auto_scaling.enable_cost_optimization
            },
            "current_state": {
                "instances": self._current_instances,
                "resources": self._current_resources,
                "scaling_events_count": len(self._scaling_history),
                "cost_efficiency": self._calculate_cost_efficiency()
            }
        }