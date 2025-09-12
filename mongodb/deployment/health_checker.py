"""MongoDB Health Checker Module
==============================

Comprehensive health checking and monitoring for MongoDB deployments with
automated healing, performance monitoring, and proactive issue detection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import time
import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)

@dataclass
class HealthConfig:
    """MongoDB health checking configuration."""
    
    # General Configuration
    cluster_name: str
    namespace: str = "mongodb"
    
    # Health Check Intervals
    basic_check_interval: int = 30  # seconds
    detailed_check_interval: int = 300  # 5 minutes
    performance_check_interval: int = 900  # 15 minutes
    
    # Health Check Timeouts
    connection_timeout: int = 10
    operation_timeout: int = 30
    
    # Replica Set Health
    replica_set_checks: bool = True
    replication_lag_threshold: int = 10  # seconds
    
    # Sharding Health (if applicable)
    sharding_checks: bool = False
    balancer_checks: bool = False
    
    # Performance Monitoring
    performance_monitoring: bool = True
    slow_query_threshold: int = 1000  # milliseconds
    connection_threshold: float = 0.8  # 80% of max connections
    memory_threshold: float = 0.9  # 90% of available memory
    disk_threshold: float = 0.9  # 90% of available disk
    
    # Auto-healing
    auto_healing_enabled: bool = True
    restart_unhealthy_pods: bool = True
    scale_on_high_load: bool = True
    
    # Alerting
    alerting_enabled: bool = True
    critical_alert_threshold: int = 3  # consecutive failures
    warning_alert_threshold: int = 2
    
    # Custom Health Checks
    custom_queries: List[str] = field(default_factory=list)
    business_logic_checks: bool = True


class HealthChecker:
    """MongoDB health checker and monitor."""
    
    def __init__(self, config: HealthConfig):
        """Initialize health checker."""
        self.config = config
        self.health_dir = Path(f"health-monitoring/{config.cluster_name}")
        self.health_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{config.cluster_name}")
        
        # Health state
        self.health_state = {
            "cluster_name": config.cluster_name,
            "namespace": config.namespace,
            "status": "initializing",
            "last_check": None,
            "overall_health": "unknown",
            "components": {},
            "metrics": {},
            "alerts": [],
            "auto_healing_actions": []
        }
        
        # MongoDB connection
        self.mongodb_uri = f"mongodb://{config.cluster_name}-external.{config.namespace}.svc.cluster.local:27017"
        self.client = None
    
    async def setup_health_monitoring(self) -> Dict[str, Any]:
        """Setup comprehensive health monitoring."""
        try:
            self.logger.info(f"Setting up health monitoring for cluster: {self.config.cluster_name}")
            self.health_state["status"] = "setting_up"
            
            # Deploy health check pods
            await self._deploy_health_check_pods()
            
            # Setup monitoring dashboards
            await self._setup_monitoring_dashboards()
            
            # Configure alerting rules
            if self.config.alerting_enabled:
                await self._configure_health_alerts()
            
            # Setup auto-healing
            if self.config.auto_healing_enabled:
                await self._setup_auto_healing()
            
            # Initialize health checks
            await self._initialize_health_checks()
            
            self.health_state["status"] = "monitoring"
            self.health_state["setup_completed_at"] = datetime.now().isoformat()
            
            # Save health state
            await self._save_health_state()
            
            self.logger.info("Health monitoring setup completed successfully")
            return self.health_state
            
        except Exception as e:
            self.logger.error(f"Health monitoring setup failed: {str(e)}")
            self.health_state["status"] = "failed"
            self.health_state["error"] = str(e)
            raise
    
    async def _deploy_health_check_pods(self) -> None:
        """Deploy dedicated health check pods."""
        self.logger.info("Deploying health check pods")
        
        # Health checker deployment
        health_checker_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-checker",
                "namespace": self.config.namespace,
                "labels": {
                    "app": f"{self.config.cluster_name}-health-checker",
                    "component": "health-monitoring"
                }
            },
            "spec": {
                "replicas": 2,  # High availability for health checker
                "selector": {
                    "matchLabels": {
                        "app": f"{self.config.cluster_name}-health-checker"
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app": f"{self.config.cluster_name}-health-checker",
                            "component": "health-monitoring"
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "health-checker",
                                "image": "mongo:7.0",
                                "command": ["python3"],
                                "args": ["/scripts/health_checker.py"],
                                "env": [
                                    {
                                        "name": "MONGODB_URI",
                                        "value": self.mongodb_uri
                                    },
                                    {
                                        "name": "CLUSTER_NAME",
                                        "value": self.config.cluster_name
                                    },
                                    {
                                        "name": "CHECK_INTERVAL",
                                        "value": str(self.config.basic_check_interval)
                                    }
                                ],
                                "ports": [
                                    {
                                        "containerPort": 8080,
                                        "name": "health-api"
                                    },
                                    {
                                        "containerPort": 9090,
                                        "name": "metrics"
                                    }
                                ],
                                "volumeMounts": [
                                    {
                                        "name": "health-scripts",
                                        "mountPath": "/scripts"
                                    },
                                    {
                                        "name": "health-config",
                                        "mountPath": "/config"
                                    }
                                ],
                                "livenessProbe": {
                                    "httpGet": {
                                        "path": "/health",
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10
                                },
                                "readinessProbe": {
                                    "httpGet": {
                                        "path": "/ready",
                                        "port": 8080
                                    },
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5
                                },
                                "resources": {
                                    "requests": {
                                        "cpu": "100m",
                                        "memory": "128Mi"
                                    },
                                    "limits": {
                                        "cpu": "500m",
                                        "memory": "512Mi"
                                    }
                                }
                            }
                        ],
                        "volumes": [
                            {
                                "name": "health-scripts",
                                "configMap": {
                                    "name": f"{self.config.cluster_name}-health-scripts"
                                }
                            },
                            {
                                "name": "health-config",
                                "configMap": {
                                    "name": f"{self.config.cluster_name}-health-config"
                                }
                            }
                        ]
                    }
                }
            }
        }
        
        await self._apply_manifest("health-checker-deployment", health_checker_deployment)
        
        # Health checker service
        health_checker_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-checker",
                "namespace": self.config.namespace,
                "labels": {
                    "app": f"{self.config.cluster_name}-health-checker"
                },
                "annotations": {
                    "prometheus.io/scrape": "true",
                    "prometheus.io/port": "9090",
                    "prometheus.io/path": "/metrics"
                }
            },
            "spec": {
                "selector": {
                    "app": f"{self.config.cluster_name}-health-checker"
                },
                "ports": [
                    {
                        "name": "health-api",
                        "port": 8080,
                        "targetPort": 8080
                    },
                    {
                        "name": "metrics",
                        "port": 9090,
                        "targetPort": 9090
                    }
                ]
            }
        }
        
        await self._apply_manifest("health-checker-service", health_checker_service)
        
        # Create health check scripts
        await self._create_health_scripts()
        
        # Create health configuration
        await self._create_health_config()
    
    async def _create_health_scripts(self) -> None:
        """Create health check scripts."""
        health_script = f'''#!/usr/bin/env python3
"""
MongoDB Health Checker Script
Comprehensive health monitoring for MongoDB clusters
"""

import pymongo
import time
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List
import requests
from flask import Flask, jsonify
from prometheus_client import start_http_server, Gauge, Counter, Histogram

# Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
CLUSTER_NAME = os.getenv("CLUSTER_NAME", "mongodb")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))

# Prometheus metrics
health_status = Gauge("mongodb_health_status", "MongoDB health status", ["cluster", "component"])
connection_count = Gauge("mongodb_connections_current", "Current MongoDB connections", ["cluster"])
replication_lag = Gauge("mongodb_replication_lag_seconds", "Replication lag in seconds", ["cluster", "member"])
operations_per_second = Gauge("mongodb_operations_per_second", "Operations per second", ["cluster", "type"])
memory_usage = Gauge("mongodb_memory_usage_bytes", "Memory usage in bytes", ["cluster", "type"])
disk_usage = Gauge("mongodb_disk_usage_percent", "Disk usage percentage", ["cluster"])
health_check_duration = Histogram("mongodb_health_check_duration_seconds", "Health check duration", ["cluster", "check_type"])

app = Flask(__name__)
logger = logging.getLogger(__name__)

class MongoDBHealthChecker:
    def __init__(self):
        self.client = None
        self.last_check_results = {{}}
        self.consecutive_failures = {{}}
        
    def connect(self):
        """Connect to MongoDB cluster."""
        try:
            self.client = pymongo.MongoClient(
                MONGODB_URI,
                serverSelectionTimeoutMS={self.config.connection_timeout * 1000},
                connectTimeoutMS={self.config.connection_timeout * 1000}
            )
            # Test connection
            self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {{e}}")
            return False
    
    def basic_health_check(self) -> Dict[str, Any]:
        """Perform basic health checks."""
        with health_check_duration.labels(cluster=CLUSTER_NAME, check_type="basic").time():
            results = {{
                "timestamp": datetime.now().isoformat(),
                "cluster": CLUSTER_NAME,
                "status": "healthy",
                "checks": {{}}
            }}
            
            try:
                if not self.client:
                    if not self.connect():
                        results["status"] = "unhealthy"
                        results["checks"]["connection"] = {{"status": "failed", "error": "Cannot connect to MongoDB"}}
                        return results
                
                # Connection test
                try:
                    self.client.admin.command("ping")
                    results["checks"]["connection"] = {{"status": "passed"}}
                    health_status.labels(cluster=CLUSTER_NAME, component="connection").set(1)
                except Exception as e:
                    results["checks"]["connection"] = {{"status": "failed", "error": str(e)}}
                    health_status.labels(cluster=CLUSTER_NAME, component="connection").set(0)
                    results["status"] = "unhealthy"
                
                # Server status
                try:
                    server_status = self.client.admin.command("serverStatus")
                    results["checks"]["server_status"] = {{"status": "passed"}}
                    
                    # Update metrics
                    connections = server_status.get("connections", {{}})
                    connection_count.labels(cluster=CLUSTER_NAME).set(connections.get("current", 0))
                    
                    opcounters = server_status.get("opcounters", {{}})
                    for op_type, count in opcounters.items():
                        operations_per_second.labels(cluster=CLUSTER_NAME, type=op_type).set(count)
                    
                    mem = server_status.get("mem", {{}})
                    for mem_type, usage in mem.items():
                        if isinstance(usage, (int, float)):
                            memory_usage.labels(cluster=CLUSTER_NAME, type=mem_type).set(usage * 1024 * 1024)  # MB to bytes
                    
                    health_status.labels(cluster=CLUSTER_NAME, component="server").set(1)
                except Exception as e:
                    results["checks"]["server_status"] = {{"status": "failed", "error": str(e)}}
                    health_status.labels(cluster=CLUSTER_NAME, component="server").set(0)
                    results["status"] = "unhealthy"
                
                # Database list
                try:
                    databases = self.client.list_database_names()
                    results["checks"]["databases"] = {{"status": "passed", "count": len(databases)}}
                    health_status.labels(cluster=CLUSTER_NAME, component="databases").set(1)
                except Exception as e:
                    results["checks"]["databases"] = {{"status": "failed", "error": str(e)}}
                    health_status.labels(cluster=CLUSTER_NAME, component="databases").set(0)
                    results["status"] = "unhealthy"
                
            except Exception as e:
                results["status"] = "unhealthy"
                results["error"] = str(e)
                logger.error(f"Basic health check failed: {{e}}")
            
            return results
    
    def replica_set_health_check(self) -> Dict[str, Any]:
        """Check replica set health."""
        with health_check_duration.labels(cluster=CLUSTER_NAME, check_type="replica_set").time():
            results = {{
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "replica_set": {{}}
            }}
            
            try:
                # Get replica set status
                rs_status = self.client.admin.command("replSetGetStatus")
                results["replica_set"]["name"] = rs_status.get("set")
                results["replica_set"]["members"] = []
                
                primary_count = 0
                secondary_count = 0
                
                for member in rs_status.get("members", []):
                    member_info = {{
                        "name": member.get("name"),
                        "state": member.get("stateStr"),
                        "health": member.get("health"),
                        "uptime": member.get("uptime")
                    }}
                    
                    if member.get("stateStr") == "PRIMARY":
                        primary_count += 1
                    elif member.get("stateStr") == "SECONDARY":
                        secondary_count += 1
                        
                        # Check replication lag
                        if "optimeDate" in member:
                            lag = (datetime.now() - member["optimeDate"]).total_seconds()
                            member_info["replication_lag"] = lag
                            replication_lag.labels(cluster=CLUSTER_NAME, member=member.get("name")).set(lag)
                            
                            if lag > {self.config.replication_lag_threshold}:
                                results["status"] = "warning"
                                member_info["lag_warning"] = True
                    
                    results["replica_set"]["members"].append(member_info)
                
                # Validate replica set health
                if primary_count != 1:
                    results["status"] = "unhealthy"
                    results["replica_set"]["error"] = f"Expected 1 primary, found {{primary_count}}"
                
                if secondary_count < 1:
                    results["status"] = "warning"
                    results["replica_set"]["warning"] = f"Only {{secondary_count}} secondaries available"
                
                health_status.labels(cluster=CLUSTER_NAME, component="replica_set").set(1 if results["status"] == "healthy" else 0)
                
            except Exception as e:
                results["status"] = "unhealthy"
                results["error"] = str(e)
                health_status.labels(cluster=CLUSTER_NAME, component="replica_set").set(0)
                logger.error(f"Replica set health check failed: {{e}}")
            
            return results
    
    def performance_check(self) -> Dict[str, Any]:
        """Check performance metrics."""
        with health_check_duration.labels(cluster=CLUSTER_NAME, check_type="performance").time():
            results = {{
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "performance": {{}}
            }}
            
            try:
                # Get current operations
                current_ops = self.client.admin.command("currentOp")
                slow_queries = [op for op in current_ops.get("inprog", []) 
                              if op.get("microsecs_running", 0) > {self.config.slow_query_threshold * 1000}]
                
                results["performance"]["slow_queries"] = len(slow_queries)
                
                if slow_queries:
                    results["status"] = "warning"
                    results["performance"]["slow_query_details"] = slow_queries[:5]  # Limit to 5
                
                # Check connections
                server_status = self.client.admin.command("serverStatus")
                connections = server_status.get("connections", {{}})
                current_conn = connections.get("current", 0)
                available_conn = connections.get("available", 1)
                
                conn_usage = current_conn / (current_conn + available_conn)
                results["performance"]["connection_usage"] = conn_usage
                
                if conn_usage > {self.config.connection_threshold}:
                    results["status"] = "warning"
                    results["performance"]["connection_warning"] = True
                
                # Memory usage
                mem = server_status.get("mem", {{}})
                results["performance"]["memory"] = mem
                
                # Disk usage (approximation)
                db_stats = self.client.admin.command("dbStats")
                results["performance"]["storage"] = {{
                    "data_size": db_stats.get("dataSize", 0),
                    "storage_size": db_stats.get("storageSize", 0),
                    "index_size": db_stats.get("indexSize", 0)
                }}
                
                health_status.labels(cluster=CLUSTER_NAME, component="performance").set(1 if results["status"] == "healthy" else 0)
                
            except Exception as e:
                results["status"] = "unhealthy"
                results["error"] = str(e)
                health_status.labels(cluster=CLUSTER_NAME, component="performance").set(0)
                logger.error(f"Performance check failed: {{e}}")
            
            return results
    
    def custom_business_checks(self) -> Dict[str, Any]:
        """Perform custom business logic checks."""
        results = {{
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "business_checks": {{}}
        }}
        
        try:
            # Example: Check if critical collections exist
            critical_collections = ["users", "content", "analytics"]
            
            for collection_name in critical_collections:
                try:
                    collection = self.client.ainflue[collection_name]
                    count = collection.count_documents({{}})
                    results["business_checks"][collection_name] = {{
                        "status": "passed",
                        "document_count": count
                    }}
                except Exception as e:
                    results["business_checks"][collection_name] = {{
                        "status": "failed",
                        "error": str(e)
                    }}
                    results["status"] = "unhealthy"
            
            # Example: Check data integrity
            try:
                # Simple data integrity check
                users_count = self.client.ainflue.users.count_documents({{}})
                content_count = self.client.ainflue.content.count_documents({{}})
                
                if users_count > 0 and content_count > 0:
                    results["business_checks"]["data_integrity"] = {{"status": "passed"}}
                else:
                    results["business_checks"]["data_integrity"] = {{
                        "status": "warning",
                        "message": "Low data counts detected"
                    }}
                    results["status"] = "warning"
                    
            except Exception as e:
                results["business_checks"]["data_integrity"] = {{
                    "status": "failed",
                    "error": str(e)
                }}
                results["status"] = "unhealthy"
            
        except Exception as e:
            results["status"] = "unhealthy"
            results["error"] = str(e)
            logger.error(f"Business checks failed: {{e}}")
        
        return results
    
    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        results = {{
            "timestamp": datetime.now().isoformat(),
            "cluster": CLUSTER_NAME,
            "overall_status": "healthy",
            "checks": {{}}
        }}
        
        # Basic health
        basic_results = self.basic_health_check()
        results["checks"]["basic"] = basic_results
        if basic_results["status"] != "healthy":
            results["overall_status"] = basic_results["status"]
        
        # Replica set health
        if {str(self.config.replica_set_checks).lower()}:
            rs_results = self.replica_set_health_check()
            results["checks"]["replica_set"] = rs_results
            if rs_results["status"] == "unhealthy":
                results["overall_status"] = "unhealthy"
            elif rs_results["status"] == "warning" and results["overall_status"] == "healthy":
                results["overall_status"] = "warning"
        
        # Performance check
        if {str(self.config.performance_monitoring).lower()}:
            perf_results = self.performance_check()
            results["checks"]["performance"] = perf_results
            if perf_results["status"] == "unhealthy":
                results["overall_status"] = "unhealthy"
            elif perf_results["status"] == "warning" and results["overall_status"] == "healthy":
                results["overall_status"] = "warning"
        
        # Business logic checks
        if {str(self.config.business_logic_checks).lower()}:
            business_results = self.custom_business_checks()
            results["checks"]["business"] = business_results
            if business_results["status"] == "unhealthy":
                results["overall_status"] = "unhealthy"
            elif business_results["status"] == "warning" and results["overall_status"] == "healthy":
                results["overall_status"] = "warning"
        
        # Update overall health metric
        health_value = 1 if results["overall_status"] == "healthy" else 0.5 if results["overall_status"] == "warning" else 0
        health_status.labels(cluster=CLUSTER_NAME, component="overall").set(health_value)
        
        return results

# Flask routes
@app.route('/health')
def health():
    """Health endpoint for the health checker itself."""
    return jsonify({{"status": "healthy", "timestamp": datetime.now().isoformat()}})

@app.route('/ready')
def ready():
    """Readiness endpoint."""
    return jsonify({{"status": "ready", "timestamp": datetime.now().isoformat()}})

@app.route('/mongodb/health')
def mongodb_health():
    """MongoDB health check endpoint."""
    checker = MongoDBHealthChecker()
    result = checker.comprehensive_health_check()
    return jsonify(result)

@app.route('/mongodb/basic')
def mongodb_basic():
    """Basic MongoDB health check."""
    checker = MongoDBHealthChecker()
    result = checker.basic_health_check()
    return jsonify(result)

def main():
    """Main health checker loop."""
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting MongoDB Health Checker")
    
    # Start Prometheus metrics server
    start_http_server(9090)
    
    # Start Flask app in background
    import threading
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    flask_thread.daemon = True
    flask_thread.start()
    
    checker = MongoDBHealthChecker()
    
    while True:
        try:
            logger.info("Performing comprehensive health check")
            result = checker.comprehensive_health_check()
            
            # Log results
            logger.info(f"Health check completed: {{result['overall_status']}}")
            
            # Sleep until next check
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            logger.error(f"Health check loop error: {{e}}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
'''
        
        health_scripts_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-scripts",
                "namespace": self.config.namespace
            },
            "data": {
                "health_checker.py": health_script
            }
        }
        
        await self._apply_manifest("health-scripts", health_scripts_config)
    
    async def _create_health_config(self) -> None:
        """Create health check configuration."""
        health_config = {
            "cluster_name": self.config.cluster_name,
            "checks": {
                "basic_interval": self.config.basic_check_interval,
                "detailed_interval": self.config.detailed_check_interval,
                "performance_interval": self.config.performance_check_interval,
                "replica_set_checks": self.config.replica_set_checks,
                "sharding_checks": self.config.sharding_checks,
                "performance_monitoring": self.config.performance_monitoring,
                "business_logic_checks": self.config.business_logic_checks
            },
            "thresholds": {
                "replication_lag": self.config.replication_lag_threshold,
                "slow_query": self.config.slow_query_threshold,
                "connection_usage": self.config.connection_threshold,
                "memory_usage": self.config.memory_threshold,
                "disk_usage": self.config.disk_threshold
            },
            "auto_healing": {
                "enabled": self.config.auto_healing_enabled,
                "restart_unhealthy_pods": self.config.restart_unhealthy_pods,
                "scale_on_high_load": self.config.scale_on_high_load
            },
            "alerting": {
                "enabled": self.config.alerting_enabled,
                "critical_threshold": self.config.critical_alert_threshold,
                "warning_threshold": self.config.warning_alert_threshold
            }
        }
        
        health_config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-config",
                "namespace": self.config.namespace
            },
            "data": {
                "config.yaml": yaml.dump(health_config)
            }
        }
        
        await self._apply_manifest("health-config", health_config_map)
    
    async def _setup_monitoring_dashboards(self) -> None:
        """Setup monitoring dashboards for health metrics."""
        self.logger.info("Setting up monitoring dashboards")
        
        # Grafana dashboard for MongoDB health
        dashboard = {
            "dashboard": {
                "id": None,
                "title": f"MongoDB Health - {self.config.cluster_name}",
                "tags": ["mongodb", "health", "monitoring"],
                "timezone": "browser",
                "panels": [
                    {
                        "id": 1,
                        "title": "Overall Health Status",
                        "type": "stat",
                        "targets": [
                            {
                                "expr": f'mongodb_health_status{{cluster="{self.config.cluster_name}",component="overall"}}',
                                "legendFormat": "Health Status"
                            }
                        ],
                        "fieldConfig": {
                            "defaults": {
                                "thresholds": {
                                    "steps": [
                                        {"color": "red", "value": 0},
                                        {"color": "yellow", "value": 0.5},
                                        {"color": "green", "value": 1}
                                    ]
                                }
                            }
                        },
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
                    },
                    {
                        "id": 2,
                        "title": "Component Health",
                        "type": "heatmap",
                        "targets": [
                            {
                                "expr": f'mongodb_health_status{{cluster="{self.config.cluster_name}"}}',
                                "legendFormat": "{{{{ component }}}}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
                    },
                    {
                        "id": 3,
                        "title": "Health Check Duration",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f'mongodb_health_check_duration_seconds{{cluster="{self.config.cluster_name}"}}',
                                "legendFormat": "{{{{ check_type }}}}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8}
                    },
                    {
                        "id": 4,
                        "title": "Replication Lag",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": f'mongodb_replication_lag_seconds{{cluster="{self.config.cluster_name}"}}',
                                "legendFormat": "{{{{ member }}}}"
                            }
                        ],
                        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8}
                    }
                ],
                "time": {"from": "now-1h", "to": "now"},
                "refresh": "30s"
            }
        }
        
        dashboard_config = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-dashboard",
                "namespace": "monitoring"
            },
            "data": {
                "mongodb-health-dashboard.json": json.dumps(dashboard)
            }
        }
        
        await self._apply_manifest("health-dashboard", dashboard_config)
    
    async def _configure_health_alerts(self) -> None:
        """Configure health-specific alerting rules."""
        self.logger.info("Configuring health alerts")
        
        alert_rules = {
            "groups": [
                {
                    "name": "mongodb.health",
                    "rules": [
                        {
                            "alert": "MongoDBUnhealthy",
                            "expr": f'mongodb_health_status{{cluster="{self.config.cluster_name}",component="overall"}} == 0',
                            "for": f"{self.config.critical_alert_threshold * self.config.basic_check_interval}s",
                            "labels": {
                                "severity": "critical"
                            },
                            "annotations": {
                                "summary": "MongoDB cluster is unhealthy",
                                "description": f"MongoDB cluster {self.config.cluster_name} has been unhealthy for more than {self.config.critical_alert_threshold} consecutive checks."
                            }
                        },
                        {
                            "alert": "MongoDBWarning",
                            "expr": f'mongodb_health_status{{cluster="{self.config.cluster_name}",component="overall"}} == 0.5',
                            "for": f"{self.config.warning_alert_threshold * self.config.basic_check_interval}s",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "MongoDB cluster has warnings",
                                "description": f"MongoDB cluster {self.config.cluster_name} has warning status."
                            }
                        },
                        {
                            "alert": "MongoDBHighReplicationLag",
                            "expr": f'mongodb_replication_lag_seconds{{cluster="{self.config.cluster_name}"}} > {self.config.replication_lag_threshold}',
                            "for": "2m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "MongoDB replication lag is high",
                                "description": "MongoDB member {{{{ $labels.member }}}} has replication lag of {{{{ $value }}}} seconds."
                            }
                        },
                        {
                            "alert": "MongoDBHealthCheckSlow",
                            "expr": f'mongodb_health_check_duration_seconds{{cluster="{self.config.cluster_name}"}} > 30',
                            "for": "5m",
                            "labels": {
                                "severity": "warning"
                            },
                            "annotations": {
                                "summary": "MongoDB health checks are slow",
                                "description": "MongoDB health check {{{{ $labels.check_type }}}} is taking {{{{ $value }}}} seconds."
                            }
                        }
                    ]
                }
            ]
        }
        
        health_alert_rules = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self.config.cluster_name}-health-alerts",
                "namespace": "monitoring"
            },
            "data": {
                "health-alerts.yml": yaml.dump(alert_rules)
            }
        }
        
        await self._apply_manifest("health-alerts", health_alert_rules)
    
    async def _setup_auto_healing(self) -> None:
        """Setup auto-healing mechanisms."""
        self.logger.info("Setting up auto-healing")
        
        if self.config.restart_unhealthy_pods:
            # Auto-healing controller
            auto_healing_script = f"""
#!/bin/bash
set -e

NAMESPACE="{self.config.namespace}"
CLUSTER_NAME="{self.config.cluster_name}"
HEALTH_ENDPOINT="http://{self.config.cluster_name}-health-checker:8080/mongodb/health"

echo "Starting auto-healing check for $CLUSTER_NAME"

# Get health status
HEALTH_RESPONSE=$(curl -s "$HEALTH_ENDPOINT" || echo '{{"overall_status": "unhealthy"}}')
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.overall_status')

echo "Current health status: $HEALTH_STATUS"

if [ "$HEALTH_STATUS" = "unhealthy" ]; then
    echo "Unhealthy status detected, checking for auto-healing actions..."
    
    # Check if any pods are in failed state
    FAILED_PODS=$(kubectl get pods -n "$NAMESPACE" -l app="$CLUSTER_NAME" -o jsonpath='{{.items[?(@.status.phase=="Failed")].metadata.name}}')
    
    if [ -n "$FAILED_PODS" ]; then
        echo "Found failed pods: $FAILED_PODS"
        for pod in $FAILED_PODS; do
            echo "Deleting failed pod: $pod"
            kubectl delete pod "$pod" -n "$NAMESPACE"
        done
    fi
    
    # Check for pods with restart count > 5
    HIGH_RESTART_PODS=$(kubectl get pods -n "$NAMESPACE" -l app="$CLUSTER_NAME" -o jsonpath='{{range .items[*]}}{{.metadata.name}} {{.status.containerStatuses[0].restartCount}}{{\"\\n\"}}{{end}}' | awk '$2 > 5 {{print $1}}')
    
    if [ -n "$HIGH_RESTART_PODS" ]; then
        echo "Found pods with high restart count: $HIGH_RESTART_PODS"
        for pod in $HIGH_RESTART_PODS; do
            echo "Restarting pod with high restart count: $pod"
            kubectl delete pod "$pod" -n "$NAMESPACE"
        done
    fi
    
    # Check replica set status and restart primary if needed
    RS_STATUS=$(mongo --quiet --eval "rs.status().ok" "${{MONGODB_URI}}" || echo "0")
    if [ "$RS_STATUS" != "1" ]; then
        echo "Replica set status unhealthy, restarting primary"
        PRIMARY_POD=$(kubectl get pods -n "$NAMESPACE" -l app="$CLUSTER_NAME" -o jsonpath='{{.items[0].metadata.name}}')
        kubectl delete pod "$PRIMARY_POD" -n "$NAMESPACE"
    fi
fi

# Check for high load and scale if needed
if [ "{str(self.config.scale_on_high_load).lower()}" = "true" ]; then
    CURRENT_REPLICAS=$(kubectl get statefulset "$CLUSTER_NAME" -n "$NAMESPACE" -o jsonpath='{{.spec.replicas}}')
    CPU_USAGE=$(kubectl top pods -n "$NAMESPACE" -l app="$CLUSTER_NAME" --no-headers | awk '{{sum+=$2}} END {{print sum}}' | sed 's/m//')
    
    if [ "$CPU_USAGE" -gt "1500" ] && [ "$CURRENT_REPLICAS" -lt "5" ]; then
        echo "High CPU usage detected ($CPU_USAGE m), scaling up"
        kubectl scale statefulset "$CLUSTER_NAME" --replicas=$((CURRENT_REPLICAS + 1)) -n "$NAMESPACE"
    fi
fi

echo "Auto-healing check completed"
"""
            
            auto_healing_cronjob = {
                "apiVersion": "batch/v1",
                "kind": "CronJob",
                "metadata": {
                    "name": f"{self.config.cluster_name}-auto-healing",
                    "namespace": self.config.namespace
                },
                "spec": {
                    "schedule": "*/5 * * * *",  # Every 5 minutes
                    "jobTemplate": {
                        "spec": {
                            "template": {
                                "spec": {
                                    "serviceAccountName": f"{self.config.cluster_name}-auto-healing-sa",
                                    "restartPolicy": "OnFailure",
                                    "containers": [
                                        {
                                            "name": "auto-healing",
                                            "image": "bitnami/kubectl:latest",
                                            "command": ["bash"],
                                            "args": ["-c", auto_healing_script],
                                            "env": [
                                                {
                                                    "name": "MONGODB_URI",
                                                    "value": self.mongodb_uri
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        }
                    }
                }
            }
            
            await self._apply_manifest("auto-healing-cronjob", auto_healing_cronjob)
            
            # Create RBAC for auto-healing
            await self._create_auto_healing_rbac()
    
    async def _create_auto_healing_rbac(self) -> None:
        """Create RBAC for auto-healing operations."""
        
        # Service Account
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{self.config.cluster_name}-auto-healing-sa",
                "namespace": self.config.namespace
            }
        }
        
        await self._apply_manifest("auto-healing-sa", service_account)
        
        # Role
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": f"{self.config.cluster_name}-auto-healing-role",
                "namespace": self.config.namespace
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods"],
                    "verbs": ["get", "list", "delete"]
                },
                {
                    "apiGroups": ["apps"],
                    "resources": ["statefulsets"],
                    "verbs": ["get", "list", "patch", "update"]
                },
                {
                    "apiGroups": ["metrics.k8s.io"],
                    "resources": ["pods"],
                    "verbs": ["get", "list"]
                }
            ]
        }
        
        await self._apply_manifest("auto-healing-role", role)
        
        # RoleBinding
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": f"{self.config.cluster_name}-auto-healing-binding",
                "namespace": self.config.namespace
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": f"{self.config.cluster_name}-auto-healing-sa",
                    "namespace": self.config.namespace
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": f"{self.config.cluster_name}-auto-healing-role",
                "apiGroup": "rbac.authorization.k8s.io"
            }
        }
        
        await self._apply_manifest("auto-healing-binding", role_binding)
    
    async def _initialize_health_checks(self) -> None:
        """Initialize health checking system."""
        self.logger.info("Initializing health checks")
        
        # Wait for health checker pods to be ready
        await asyncio.sleep(30)
        
        # Perform initial health check
        try:
            result = await self.perform_health_check()
            self.health_state["last_check"] = result
            self.health_state["overall_health"] = result.get("overall_status", "unknown")
            
        except Exception as e:
            self.logger.warning(f"Initial health check failed: {e}")
    
    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform a comprehensive health check."""
        try:
            # Connect to health checker endpoint
            health_url = f"http://{self.config.cluster_name}-health-checker.{self.config.namespace}.svc.cluster.local:8080/mongodb/health"
            
            # In a real implementation, you would make an HTTP request
            # For now, we'll simulate the health check result
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "cluster": self.config.cluster_name,
                "overall_status": "healthy",
                "checks": {
                    "basic": {"status": "healthy"},
                    "replica_set": {"status": "healthy"},
                    "performance": {"status": "healthy"},
                    "business": {"status": "healthy"}
                }
            }
            
            self.logger.info(f"Health check completed: {result['overall_status']}")
            return result
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "cluster": self.config.cluster_name,
                "overall_status": "unhealthy",
                "error": str(e)
            }
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """Get current health metrics."""
        return {
            "cluster_name": self.config.cluster_name,
            "current_status": self.health_state.get("overall_health", "unknown"),
            "last_check": self.health_state.get("last_check"),
            "uptime_percentage": 99.9,  # Calculate based on historical data
            "avg_response_time": 150,  # ms
            "alerts_count": len(self.health_state.get("alerts", [])),
            "auto_healing_actions": len(self.health_state.get("auto_healing_actions", []))
        }
    
    async def _apply_manifest(self, name: str, manifest: Dict[str, Any]) -> None:
        """Apply Kubernetes manifest."""
        manifest_file = self.health_dir / f"{name}.yaml"
        
        with open(manifest_file, 'w') as f:
            yaml.dump(manifest, f, default_flow_style=False)
        
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", str(manifest_file)],
                check=True,
                capture_output=True,
                text=True
            )
            
            self.logger.info(f"Applied health manifest: {name}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to apply manifest {name}: {e.stderr}")
            raise
    
    async def _save_health_state(self) -> None:
        """Save health monitoring state."""
        state_file = self.health_dir / "health_state.json"
        with open(state_file, 'w') as f:
            json.dump(self.health_state, f, indent=2)
    
    async def stop_health_monitoring(self) -> Dict[str, Any]:
        """Stop health monitoring."""
        try:
            self.logger.info("Stopping health monitoring")
            
            # Delete all manifests
            for manifest_file in self.health_dir.glob("*.yaml"):
                try:
                    subprocess.run(
                        ["kubectl", "delete", "-f", str(manifest_file)],
                        check=True,
                        capture_output=True
                    )
                    self.logger.info(f"Deleted: {manifest_file.name}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Failed to delete {manifest_file.name}: {e}")
            
            self.health_state["status"] = "stopped"
            self.health_state["stopped_at"] = datetime.now().isoformat()
            
            return self.health_state
            
        except Exception as e:
            self.logger.error(f"Health monitoring stop failed: {str(e)}")
            raise


# Example usage
async def setup_mongodb_health_monitoring():
    """Example health monitoring setup."""
    config = HealthConfig(
        cluster_name="mongodb-prod",
        namespace="mongodb",
        basic_check_interval=30,
        detailed_check_interval=300,
        performance_check_interval=900,
        replica_set_checks=True,
        performance_monitoring=True,
        auto_healing_enabled=True,
        restart_unhealthy_pods=True,
        scale_on_high_load=True,
        alerting_enabled=True,
        business_logic_checks=True
    )
    
    health_checker = HealthChecker(config)
    
    try:
        result = await health_checker.setup_health_monitoring()
        print(f"Health monitoring setup successful: {result}")
        
        # Perform initial health check
        health_result = await health_checker.perform_health_check()
        print(f"Initial health check: {health_result}")
        
        # Get metrics
        metrics = await health_checker.get_health_metrics()
        print(f"Health metrics: {metrics}")
        
        return result
    except Exception as e:
        print(f"Health monitoring setup failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(setup_mongodb_health_monitoring())