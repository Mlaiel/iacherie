"""
Scaling Configuration Module for IA-Influencer Agent Platform
============================================================

Professional auto-scaling and capacity management configuration
for multi-format content protection and AI-powered creator monetization platform.

Author: Fahed Mlaiel <mlaiel@live.de>
Project: IA-Influencer Agent + Content Protection Platform
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices + Audio + DevOps

Copyright Notice:
This code is the intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution of this code
without explicit written permission from the author is strictly prohibited.

Contact: mlaiel@live.de for licensing inquiries.
"""

import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class ScalingTrigger(Enum):
    """Scaling trigger types"""
    CPU_UTILIZATION = "cpu_utilization"
    MEMORY_UTILIZATION = "memory_utilization"
    REQUEST_RATE = "request_rate"
    QUEUE_LENGTH = "queue_length"
    RESPONSE_TIME = "response_time"
    CUSTOM_METRIC = "custom_metric"


class ScalingDirection(Enum):
    """Scaling direction"""
    UP = "up"
    DOWN = "down"
    BOTH = "both"


class ScalingPolicy(Enum):
    """Scaling policy types"""
    TARGET_TRACKING = "target_tracking"
    STEP_SCALING = "step_scaling"
    SIMPLE_SCALING = "simple_scaling"
    PREDICTIVE = "predictive"


@dataclass
class ScalingMetric:
    """Scaling metric configuration"""
    name: str
    trigger: ScalingTrigger
    target_value: float
    threshold_up: float
    threshold_down: float
    evaluation_periods: int = 2
    datapoints_to_alarm: int = 2
    comparison_operator: str = "GreaterThanThreshold"
    statistic: str = "Average"
    unit: str = "Percent"


@dataclass
class ScalingRule:
    """Scaling rule configuration"""
    name: str
    metric: ScalingMetric
    policy: ScalingPolicy
    cooldown_seconds: int = 300
    scale_out_step: int = 1
    scale_in_step: int = 1
    min_adjustment_magnitude: int = 1
    max_instances: int = 10
    min_instances: int = 1
    target_capacity: int = 2
    enabled: bool = True


@dataclass
class HorizontalPodAutoscaler:
    """Kubernetes HPA configuration"""
    name: str
    namespace: str
    target_ref: Dict[str, str]
    min_replicas: int = 1
    max_replicas: int = 10
    metrics: List[Dict[str, Any]] = field(default_factory=list)
    behavior: Optional[Dict[str, Any]] = None


@dataclass
class VerticalPodAutoscaler:
    """Kubernetes VPA configuration"""
    name: str
    namespace: str
    target_ref: Dict[str, str]
    update_mode: str = "Auto"  # Auto, Initial, Off
    resource_policy: Optional[Dict[str, Any]] = None


class ScalingConfig:
    """
    Professional auto-scaling configuration manager for IA-Influencer Agent Platform.
    
    Manages intelligent scaling for:
    - API services (horizontal and vertical scaling)
    - AI processing workers (GPU/CPU based scaling)
    - Content protection crawlers (task-based scaling)
    - Database connections and read replicas
    - Redis cache clusters and sharding
    - WebSocket connection handlers
    - File processing queues and workers
    - Revenue analytics processors
    """
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_name = "ia-influencer-agent"
        self.namespace = self.environment
        self.scaling_enabled = self._get_scaling_enabled()
        
    def _get_scaling_enabled(self) -> bool:
        """Check if auto-scaling is enabled for environment"""
        return self.environment in ["staging", "production"]
    
    def get_scaling_metrics(self) -> Dict[str, ScalingMetric]:
        """Get scaling metrics for different services"""
        return {
            # CPU utilization
            "cpu_usage": ScalingMetric(
                name="cpu_usage",
                trigger=ScalingTrigger.CPU_UTILIZATION,
                target_value=70.0,
                threshold_up=80.0,
                threshold_down=30.0,
                evaluation_periods=2,
                datapoints_to_alarm=2,
                statistic="Average",
                unit="Percent"
            ),
            
            # Memory utilization
            "memory_usage": ScalingMetric(
                name="memory_usage",
                trigger=ScalingTrigger.MEMORY_UTILIZATION,
                target_value=75.0,
                threshold_up=85.0,
                threshold_down=40.0,
                evaluation_periods=2,
                datapoints_to_alarm=2,
                statistic="Average",
                unit="Percent"
            ),
            
            # Request rate
            "request_rate": ScalingMetric(
                name="request_rate",
                trigger=ScalingTrigger.REQUEST_RATE,
                target_value=1000.0,
                threshold_up=1500.0,
                threshold_down=300.0,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                statistic="Sum",
                unit="Count/Second"
            ),
            
            # Response time
            "response_time": ScalingMetric(
                name="response_time",
                trigger=ScalingTrigger.RESPONSE_TIME,
                target_value=200.0,
                threshold_up=500.0,
                threshold_down=100.0,
                evaluation_periods=3,
                datapoints_to_alarm=2,
                statistic="Average",
                unit="Milliseconds"
            ),
            
            # Queue length (for Celery tasks)
            "queue_length": ScalingMetric(
                name="queue_length",
                trigger=ScalingTrigger.QUEUE_LENGTH,
                target_value=50.0,
                threshold_up=100.0,
                threshold_down=10.0,
                evaluation_periods=1,
                datapoints_to_alarm=1,
                statistic="Average",
                unit="Count"
            ),
            
            # AI processing GPU utilization
            "gpu_usage": ScalingMetric(
                name="gpu_usage",
                trigger=ScalingTrigger.CUSTOM_METRIC,
                target_value=80.0,
                threshold_up=90.0,
                threshold_down=40.0,
                evaluation_periods=2,
                datapoints_to_alarm=2,
                statistic="Average",
                unit="Percent"
            )
        }
    
    def get_scaling_rules(self) -> Dict[str, ScalingRule]:
        """Get scaling rules for different services"""
        metrics = self.get_scaling_metrics()
        
        base_config = {
            "development": {"max_instances": 3, "min_instances": 1},
            "staging": {"max_instances": 5, "min_instances": 2},
            "production": {"max_instances": 20, "min_instances": 3}
        }
        
        env_config = base_config.get(self.environment, base_config["development"])
        
        return {
            # Main API service scaling
            "api_service": ScalingRule(
                name="api_service",
                metric=metrics["cpu_usage"],
                policy=ScalingPolicy.TARGET_TRACKING,
                cooldown_seconds=300,
                scale_out_step=2,
                scale_in_step=1,
                max_instances=env_config["max_instances"],
                min_instances=env_config["min_instances"],
                target_capacity=env_config["min_instances"] + 1
            ),
            
            # AI fingerprinting service scaling
            "ai_fingerprinting": ScalingRule(
                name="ai_fingerprinting",
                metric=metrics["queue_length"],
                policy=ScalingPolicy.STEP_SCALING,
                cooldown_seconds=180,
                scale_out_step=1,
                scale_in_step=1,
                max_instances=env_config["max_instances"] // 2,
                min_instances=1,
                target_capacity=2
            ),
            
            # Audio processing scaling (GPU intensive)
            "ai_audio": ScalingRule(
                name="ai_audio",
                metric=metrics["gpu_usage"],
                policy=ScalingPolicy.TARGET_TRACKING,
                cooldown_seconds=600,  # Longer cooldown for GPU services
                scale_out_step=1,
                scale_in_step=1,
                max_instances=env_config["max_instances"] // 4,
                min_instances=1,
                target_capacity=1
            ),
            
            # Video processing scaling
            "ai_video": ScalingRule(
                name="ai_video",
                metric=metrics["memory_usage"],
                policy=ScalingPolicy.TARGET_TRACKING,
                cooldown_seconds=900,  # Very long cooldown for video processing
                scale_out_step=1,
                scale_in_step=1,
                max_instances=env_config["max_instances"] // 5,
                min_instances=1,
                target_capacity=1
            ),
            
            # Content protection crawlers
            "protection_crawlers": ScalingRule(
                name="protection_crawlers",
                metric=metrics["request_rate"],
                policy=ScalingPolicy.SIMPLE_SCALING,
                cooldown_seconds=240,
                scale_out_step=2,
                scale_in_step=1,
                max_instances=env_config["max_instances"],
                min_instances=2,
                target_capacity=3
            ),
            
            # WebSocket service scaling
            "websocket_service": ScalingRule(
                name="websocket_service",
                metric=metrics["cpu_usage"],
                policy=ScalingPolicy.TARGET_TRACKING,
                cooldown_seconds=300,
                scale_out_step=1,
                scale_in_step=1,
                max_instances=env_config["max_instances"] // 2,
                min_instances=2,
                target_capacity=3
            ),
            
            # Revenue analytics scaling
            "revenue_analytics": ScalingRule(
                name="revenue_analytics",
                metric=metrics["memory_usage"],
                policy=ScalingPolicy.TARGET_TRACKING,
                cooldown_seconds=300,
                scale_out_step=1,
                scale_in_step=1,
                max_instances=env_config["max_instances"] // 3,
                min_instances=1,
                target_capacity=2
            ),
            
            # Celery workers scaling
            "celery_workers": ScalingRule(
                name="celery_workers",
                metric=metrics["queue_length"],
                policy=ScalingPolicy.STEP_SCALING,
                cooldown_seconds=120,
                scale_out_step=3,
                scale_in_step=2,
                max_instances=env_config["max_instances"] * 2,
                min_instances=env_config["min_instances"],
                target_capacity=env_config["min_instances"] * 2
            )
        }
    
    def get_kubernetes_hpa_configs(self) -> List[HorizontalPodAutoscaler]:
        """Get Kubernetes Horizontal Pod Autoscaler configurations"""
        scaling_rules = self.get_scaling_rules()
        hpa_configs = []
        
        for service_name, rule in scaling_rules.items():
            # Standard CPU/Memory based HPA
            metrics = [
                {
                    "type": "Resource",
                    "resource": {
                        "name": "cpu",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": int(rule.metric.target_value)
                        }
                    }
                }
            ]
            
            # Add memory metric for memory-intensive services
            if service_name in ["ai_video", "revenue_analytics", "ai_fingerprinting"]:
                metrics.append({
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": 75
                        }
                    }
                })
            
            # Add custom metrics for specific services
            if service_name == "celery_workers":
                metrics.append({
                    "type": "External",
                    "external": {
                        "metric": {
                            "name": "redis_queue_length",
                            "selector": {
                                "matchLabels": {
                                    "app": service_name,
                                    "environment": self.environment
                                }
                            }
                        },
                        "target": {
                            "type": "AverageValue",
                            "averageValue": str(int(rule.metric.target_value))
                        }
                    }
                })
            
            # Scaling behavior configuration
            behavior = {
                "scaleUp": {
                    "stabilizationWindowSeconds": rule.cooldown_seconds,
                    "policies": [
                        {
                            "type": "Pods",
                            "value": rule.scale_out_step,
                            "periodSeconds": 60
                        },
                        {
                            "type": "Percent",
                            "value": 50,
                            "periodSeconds": 60
                        }
                    ],
                    "selectPolicy": "Min"
                },
                "scaleDown": {
                    "stabilizationWindowSeconds": rule.cooldown_seconds * 2,
                    "policies": [
                        {
                            "type": "Pods",
                            "value": rule.scale_in_step,
                            "periodSeconds": 60
                        },
                        {
                            "type": "Percent",
                            "value": 10,
                            "periodSeconds": 60
                        }
                    ],
                    "selectPolicy": "Min"
                }
            }
            
            hpa = HorizontalPodAutoscaler(
                name=f"{service_name}-hpa",
                namespace=self.namespace,
                target_ref={
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{service_name}-deployment"
                },
                min_replicas=rule.min_instances,
                max_replicas=rule.max_instances,
                metrics=metrics,
                behavior=behavior
            )
            
            hpa_configs.append(hpa)
        
        return hpa_configs
    
    def get_kubernetes_vpa_configs(self) -> List[VerticalPodAutoscaler]:
        """Get Kubernetes Vertical Pod Autoscaler configurations"""
        vpa_configs = []
        
        # Services that benefit from VPA
        vpa_services = {
            "ai_audio": {
                "cpu": {"min": "500m", "max": "4000m"},
                "memory": {"min": "1Gi", "max": "8Gi"}
            },
            "ai_video": {
                "cpu": {"min": "1000m", "max": "8000m"},
                "memory": {"min": "2Gi", "max": "16Gi"}
            },
            "ai_fingerprinting": {
                "cpu": {"min": "500m", "max": "2000m"},
                "memory": {"min": "1Gi", "max": "4Gi"}
            },
            "revenue_analytics": {
                "cpu": {"min": "250m", "max": "1000m"},
                "memory": {"min": "512Mi", "max": "4Gi"}
            }
        }
        
        for service_name, resources in vpa_services.items():
            resource_policy = {
                "containerPolicies": [
                    {
                        "containerName": service_name,
                        "minAllowed": {
                            "cpu": resources["cpu"]["min"],
                            "memory": resources["memory"]["min"]
                        },
                        "maxAllowed": {
                            "cpu": resources["cpu"]["max"],
                            "memory": resources["memory"]["max"]
                        },
                        "controlledResources": ["cpu", "memory"]
                    }
                ]
            }
            
            vpa = VerticalPodAutoscaler(
                name=f"{service_name}-vpa",
                namespace=self.namespace,
                target_ref={
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": f"{service_name}-deployment"
                },
                update_mode="Auto",
                resource_policy=resource_policy
            )
            
            vpa_configs.append(vpa)
        
        return vpa_configs
    
    def get_aws_autoscaling_configs(self) -> Dict[str, Any]:
        """Get AWS Auto Scaling configurations"""
        scaling_rules = self.get_scaling_rules()
        
        return {
            "auto_scaling_groups": [
                {
                    "auto_scaling_group_name": f"{self.project_name}-{self.environment}-asg",
                    "launch_template": {
                        "launch_template_name": f"{self.project_name}-{self.environment}-lt",
                        "version": "$Latest"
                    },
                    "min_size": scaling_rules["api_service"].min_instances,
                    "max_size": scaling_rules["api_service"].max_instances,
                    "desired_capacity": scaling_rules["api_service"].target_capacity,
                    "vpc_zone_identifier": [
                        "subnet-12345678",
                        "subnet-87654321"
                    ],
                    "health_check_type": "ELB",
                    "health_check_grace_period": 300,
                    "default_cooldown": 300,
                    "termination_policies": ["OldestInstance"],
                    "tags": [
                        {
                            "key": "Name",
                            "value": f"{self.project_name}-{self.environment}",
                            "propagate_at_launch": True
                        },
                        {
                            "key": "Environment",
                            "value": self.environment,
                            "propagate_at_launch": True
                        }
                    ]
                }
            ],
            "scaling_policies": [
                {
                    "policy_name": f"{self.project_name}-{self.environment}-scale-up",
                    "policy_type": "TargetTrackingScaling",
                    "auto_scaling_group_name": f"{self.project_name}-{self.environment}-asg",
                    "target_tracking_configuration": {
                        "target_value": scaling_rules["api_service"].metric.target_value,
                        "predefined_metric_specification": {
                            "predefined_metric_type": "ASGAverageCPUUtilization"
                        },
                        "scale_out_cooldown": scaling_rules["api_service"].cooldown_seconds,
                        "scale_in_cooldown": scaling_rules["api_service"].cooldown_seconds * 2
                    }
                },
                {
                    "policy_name": f"{self.project_name}-{self.environment}-scale-request-count",
                    "policy_type": "TargetTrackingScaling",
                    "auto_scaling_group_name": f"{self.project_name}-{self.environment}-asg",
                    "target_tracking_configuration": {
                        "target_value": 1000.0,
                        "predefined_metric_specification": {
                            "predefined_metric_type": "ALBRequestCountPerTarget",
                            "resource_label": f"app/{self.project_name}-{self.environment}-alb/12345678/targetgroup/{self.project_name}-{self.environment}-tg/87654321"
                        }
                    }
                }
            ],
            "cloudwatch_alarms": [
                {
                    "alarm_name": f"{self.project_name}-{self.environment}-high-cpu",
                    "comparison_operator": "GreaterThanThreshold",
                    "evaluation_periods": 2,
                    "metric_name": "CPUUtilization",
                    "namespace": "AWS/EC2",
                    "period": 300,
                    "statistic": "Average",
                    "threshold": 80.0,
                    "actions_enabled": True,
                    "alarm_actions": [
                        f"arn:aws:sns:eu-central-1:123456789012:{self.project_name}-{self.environment}-alerts"
                    ],
                    "alarm_description": "Alarm when server CPU exceeds 80%",
                    "dimensions": [
                        {
                            "name": "AutoScalingGroupName",
                            "value": f"{self.project_name}-{self.environment}-asg"
                        }
                    ]
                }
            ]
        }
    
    def get_prometheus_scaling_rules(self) -> Dict[str, Any]:
        """Get Prometheus-based scaling rules for custom metrics"""
        return {
            "recording_rules": [
                {
                    "name": f"{self.project_name}_scaling_metrics",
                    "rules": [
                        {
                            "record": "ia_influencer:queue_length",
                            "expr": 'redis_list_length{job="redis"}'
                        },
                        {
                            "record": "ia_influencer:response_time_95th",
                            "expr": 'histogram_quantile(0.95, http_request_duration_seconds_bucket{job="api"})'
                        },
                        {
                            "record": "ia_influencer:gpu_utilization",
                            "expr": 'nvidia_gpu_utilization_percent{job="ai-services"}'
                        },
                        {
                            "record": "ia_influencer:api_request_rate",
                            "expr": 'rate(http_requests_total{job="api"}[5m])'
                        }
                    ]
                }
            ],
            "alerting_rules": [
                {
                    "name": f"{self.project_name}_scaling_alerts",
                    "rules": [
                        {
                            "alert": "HighQueueLength",
                            "expr": "ia_influencer:queue_length > 100",
                            "for": "2m",
                            "labels": {
                                "severity": "warning",
                                "service": "celery"
                            },
                            "annotations": {
                                "summary": "High queue length detected",
                                "description": "Queue length is {{ $value }}, consider scaling workers"
                            }
                        },
                        {
                            "alert": "HighResponseTime",
                            "expr": "ia_influencer:response_time_95th > 0.5",
                            "for": "5m",
                            "labels": {
                                "severity": "warning",
                                "service": "api"
                            },
                            "annotations": {
                                "summary": "High API response time",
                                "description": "95th percentile response time is {{ $value }}s"
                            }
                        },
                        {
                            "alert": "LowGPUUtilization",
                            "expr": "ia_influencer:gpu_utilization < 20",
                            "for": "10m",
                            "labels": {
                                "severity": "info",
                                "service": "ai"
                            },
                            "annotations": {
                                "summary": "Low GPU utilization",
                                "description": "GPU utilization is {{ $value }}%, consider scaling down"
                            }
                        }
                    ]
                }
            ]
        }
    
    def generate_scaling_script(self) -> str:
        """Generate manual scaling script"""
        return f"""#!/bin/bash
# Manual Scaling Script for IA-Influencer Agent Platform
# Author: Fahed Mlaiel <mlaiel@live.de>

set -euo pipefail

ENVIRONMENT="{self.environment}"
PROJECT_NAME="{self.project_name}"
NAMESPACE="$ENVIRONMENT"

# Default values
ACTION=""
SERVICE=""
REPLICAS=""
DRY_RUN=false

# Help function
show_help() {{
    cat << EOF
Usage: $0 [OPTIONS]

Manual scaling script for IA-Influencer Agent Platform

Options:
    -a, --action     Action: scale-up, scale-down, set-replicas, status
    -s, --service    Service name (api, ai-audio, ai-video, etc.)
    -r, --replicas   Number of replicas (for set-replicas action)
    -n, --dry-run    Show what would be done without executing
    -h, --help       Show this help message

Examples:
    $0 --action scale-up --service api
    $0 --action set-replicas --service ai-audio --replicas 3
    $0 --action status
    $0 --action scale-down --service celery-workers --dry-run

Services:
    - api               (Main API service)
    - ai-audio          (Audio processing service)
    - ai-video          (Video processing service)
    - ai-fingerprinting (Fingerprinting service)
    - protection        (Content protection service)
    - websocket         (WebSocket service)
    - revenue           (Revenue analytics service)
    - celery-workers    (Background task workers)

EOF
}}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -s|--service)
            SERVICE="$2"
            shift 2
            ;;
        -r|--replicas)
            REPLICAS="$2"
            shift 2
            ;;
        -n|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Validate inputs
if [[ -z "$ACTION" ]]; then
    echo "Error: Action is required"
    show_help
    exit 1
fi

# Service mapping
declare -A SERVICE_MAP
SERVICE_MAP["api"]="api-service-deployment"
SERVICE_MAP["ai-audio"]="ai-audio-deployment"
SERVICE_MAP["ai-video"]="ai-video-deployment"
SERVICE_MAP["ai-fingerprinting"]="ai-fingerprinting-deployment"
SERVICE_MAP["protection"]="protection-crawlers-deployment"
SERVICE_MAP["websocket"]="websocket-realtime-deployment"
SERVICE_MAP["revenue"]="revenue-analytics-deployment"
SERVICE_MAP["celery-workers"]="celery-workers-deployment"

# Logging function
log() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}}

# Get current replicas
get_current_replicas() {{
    local deployment="$1"
    kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{{.spec.replicas}}' 2>/dev/null || echo "0"
}}

# Get available replicas
get_available_replicas() {{
    local deployment="$1"
    kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{{.status.availableReplicas}}' 2>/dev/null || echo "0"
}}

# Scale deployment
scale_deployment() {{
    local deployment="$1"
    local replicas="$2"
    
    log "Scaling $deployment to $replicas replicas..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "DRY RUN: kubectl scale deployment $deployment --replicas=$replicas -n $NAMESPACE"
        return 0
    fi
    
    kubectl scale deployment "$deployment" --replicas="$replicas" -n "$NAMESPACE"
    
    if [[ $? -eq 0 ]]; then
        log "Successfully initiated scaling of $deployment"
        
        # Wait for rollout
        log "Waiting for rollout to complete..."
        kubectl rollout status deployment/"$deployment" -n "$NAMESPACE" --timeout=300s
        
        if [[ $? -eq 0 ]]; then
            log "Scaling completed successfully"
            return 0
        else
            log "Warning: Rollout timed out or failed"
            return 1
        fi
    else
        log "Error: Failed to scale $deployment"
        return 1
    fi
}}

# Show status
show_status() {{
    log "Current deployment status:"
    echo
    printf "%-25s %-10s %-10s %-10s %s\n" "SERVICE" "DESIRED" "CURRENT" "AVAILABLE" "STATUS"
    printf "%-25s %-10s %-10s %-10s %s\n" "-------" "-------" "-------" "---------" "------"
    
    for service in "${{!SERVICE_MAP[@]}}"; do
        deployment="${{SERVICE_MAP[$service]}}"
        
        if kubectl get deployment "$deployment" -n "$NAMESPACE" >/dev/null 2>&1; then
            desired=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{{.spec.replicas}}')
            current=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{{.status.replicas}}')
            available=$(kubectl get deployment "$deployment" -n "$NAMESPACE" -o jsonpath='{{.status.availableReplicas}}')
            
            current="${{current:-0}}"
            available="${{available:-0}}"
            
            if [[ "$desired" == "$available" ]]; then
                status="Ready"
            elif [[ "$available" -lt "$desired" ]]; then
                status="Scaling"
            else
                status="Unknown"
            fi
            
            printf "%-25s %-10s %-10s %-10s %s\n" "$service" "$desired" "$current" "$available" "$status"
        else
            printf "%-25s %-10s %-10s %-10s %s\n" "$service" "N/A" "N/A" "N/A" "Not Found"
        fi
    done
    
    echo
    log "HPA Status:"
    kubectl get hpa -n "$NAMESPACE" 2>/dev/null || echo "No HPAs found"
}}

# Main logic
case "$ACTION" in
    "scale-up")
        if [[ -z "$SERVICE" ]]; then
            echo "Error: Service is required for scale-up action"
            exit 1
        fi
        
        deployment="${{SERVICE_MAP[$SERVICE]}}"
        if [[ -z "$deployment" ]]; then
            echo "Error: Unknown service: $SERVICE"
            exit 1
        fi
        
        current_replicas=$(get_current_replicas "$deployment")
        new_replicas=$((current_replicas + 1))
        
        log "Scaling up $SERVICE from $current_replicas to $new_replicas replicas"
        scale_deployment "$deployment" "$new_replicas"
        ;;
        
    "scale-down")
        if [[ -z "$SERVICE" ]]; then
            echo "Error: Service is required for scale-down action"
            exit 1
        fi
        
        deployment="${{SERVICE_MAP[$SERVICE]}}"
        if [[ -z "$deployment" ]]; then
            echo "Error: Unknown service: $SERVICE"
            exit 1
        fi
        
        current_replicas=$(get_current_replicas "$deployment")
        
        if [[ "$current_replicas" -le 1 ]]; then
            log "Warning: Cannot scale down $SERVICE below 1 replica (current: $current_replicas)"
            exit 1
        fi
        
        new_replicas=$((current_replicas - 1))
        
        log "Scaling down $SERVICE from $current_replicas to $new_replicas replicas"
        scale_deployment "$deployment" "$new_replicas"
        ;;
        
    "set-replicas")
        if [[ -z "$SERVICE" || -z "$REPLICAS" ]]; then
            echo "Error: Service and replicas are required for set-replicas action"
            exit 1
        fi
        
        deployment="${{SERVICE_MAP[$SERVICE]}}"
        if [[ -z "$deployment" ]]; then
            echo "Error: Unknown service: $SERVICE"
            exit 1
        fi
        
        if ! [[ "$REPLICAS" =~ ^[0-9]+$ ]]; then
            echo "Error: Replicas must be a positive integer"
            exit 1
        fi
        
        log "Setting $SERVICE to $REPLICAS replicas"
        scale_deployment "$deployment" "$REPLICAS"
        ;;
        
    "status")
        show_status
        ;;
        
    *)
        echo "Error: Unknown action: $ACTION"
        show_help
        exit 1
        ;;
esac
"""
    
    def export_configurations(self, output_dir: str = "./scaling-configs") -> Dict[str, str]:
        """Export all scaling configurations to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        configs = {}
        
        # Kubernetes HPA configurations
        hpa_configs = self.get_kubernetes_hpa_configs()
        for hpa in hpa_configs:
            hpa_dict = {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": hpa.name,
                    "namespace": hpa.namespace
                },
                "spec": {
                    "scaleTargetRef": hpa.target_ref,
                    "minReplicas": hpa.min_replicas,
                    "maxReplicas": hpa.max_replicas,
                    "metrics": hpa.metrics
                }
            }
            
            if hpa.behavior:
                hpa_dict["spec"]["behavior"] = hpa.behavior
            
            hpa_path = os.path.join(output_dir, f"{hpa.name}-{self.environment}.yaml")
            with open(hpa_path, 'w') as f:
                yaml.dump(hpa_dict, f, default_flow_style=False)
            configs[hpa.name] = hpa_path
        
        # Kubernetes VPA configurations
        vpa_configs = self.get_kubernetes_vpa_configs()
        for vpa in vpa_configs:
            vpa_dict = {
                "apiVersion": "autoscaling.k8s.io/v1",
                "kind": "VerticalPodAutoscaler",
                "metadata": {
                    "name": vpa.name,
                    "namespace": vpa.namespace
                },
                "spec": {
                    "targetRef": vpa.target_ref,
                    "updatePolicy": {
                        "updateMode": vpa.update_mode
                    }
                }
            }
            
            if vpa.resource_policy:
                vpa_dict["spec"]["resourcePolicy"] = vpa.resource_policy
            
            vpa_path = os.path.join(output_dir, f"{vpa.name}-{self.environment}.yaml")
            with open(vpa_path, 'w') as f:
                yaml.dump(vpa_dict, f, default_flow_style=False)
            configs[vpa.name] = vpa_path
        
        # AWS Auto Scaling configuration
        aws_config = self.get_aws_autoscaling_configs()
        aws_path = os.path.join(output_dir, f"aws-autoscaling-{self.environment}.json")
        with open(aws_path, 'w') as f:
            json.dump(aws_config, f, indent=2)
        configs['aws_autoscaling'] = aws_path
        
        # Prometheus scaling rules
        prometheus_config = self.get_prometheus_scaling_rules()
        prometheus_path = os.path.join(output_dir, f"prometheus-scaling-{self.environment}.yaml")
        with open(prometheus_path, 'w') as f:
            yaml.dump(prometheus_config, f, default_flow_style=False)
        configs['prometheus_scaling'] = prometheus_path
        
        # Manual scaling script
        scaling_script = self.generate_scaling_script()
        script_path = os.path.join(output_dir, f"manual-scaling-{self.environment}.sh")
        with open(script_path, 'w') as f:
            f.write(scaling_script)
        os.chmod(script_path, 0o755)
        configs['scaling_script'] = script_path
        
        return configs
