"""Envoy Proxy Load Balancer Manager

Modern service mesh and edge proxy configuration for the IA Influencer
Agent platform, providing advanced traffic management, observability,
and circuit breaking capabilities.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ WARNING: This code is proprietary and confidential.
Unauthorized copying, distribution, or use without explicit written
permission from Fahed Mlaiel is strictly prohibited and may result
in legal action.
"""import os
import json
import yaml
import logging
import subprocess
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


@dataclass
class EnvoyEndpoint:
    """Envoy cluster endpoint configuration"""    address: str
    port: int
    weight: int = 1
    health_check_config: Optional[Dict[str, Any]] = None


@dataclass
class EnvoyCluster:
    """Envoy cluster configuration"""    name: str
    type: str = "STRICT_DNS"  # STATIC, STRICT_DNS, LOGICAL_DNS, EDS
    lb_policy: str = "ROUND_ROBIN"  # ROUND_ROBIN, LEAST_REQUEST, RING_HASH, RANDOM
    endpoints: List[EnvoyEndpoint] = None
    health_check: Optional[Dict[str, Any]] = None
    circuit_breaker: Optional[Dict[str, Any]] = None
    outlier_detection: Optional[Dict[str, Any]] = None
    timeout: str = "30s"
    retry_policy: Optional[Dict[str, Any]] = None


@dataclass
class EnvoyRoute:
    """Envoy route configuration"""    match: Dict[str, Any]
    route: Dict[str, Any]
    decorator: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    typed_per_filter_config: Optional[Dict[str, Any]] = None


@dataclass
class EnvoyListener:
    """Envoy listener configuration"""    name: str
    address: str
    port: int
    filter_chains: List[Dict[str, Any]] = None
    access_log: Optional[List[Dict[str, Any]]] = None


class EnvoyConfigGenerator:
    """Generate Envoy Proxy configurations"""    
    def __init__(self):
        self.admin_config = {
            "access_log_path": "/dev/stdout",
            "address": {
                "socket_address": {
                    "address": "127.0.0.1",
                    "port_value": 9901
                }
            }
        }
        
        self.tracing_config = {
            "http": {
                "name": "envoy.tracers.jaeger",
                "typed_config": {
                    "@type": "type.googleapis.com/envoy.config.trace.v3.JaegerConfig",
                    "collector_cluster": "jaeger",
                    "collector_endpoint": "/api/traces"
                }
            }
        }
    
    def generate_cluster_config(self, cluster: EnvoyCluster) -> Dict[str, Any]:
        """Generate cluster configuration"""        config = {
            "name": cluster.name,
            "type": cluster.type,
            "lb_policy": cluster.lb_policy,
            "connect_timeout": cluster.timeout
        }
        
        # Endpoints configuration
        if cluster.endpoints:
            if cluster.type in ["STATIC", "STRICT_DNS"]:
                config["load_assignment"] = {
                    "cluster_name": cluster.name,
                    "endpoints": [{
                        "lb_endpoints": [
                            {
                                "endpoint": {
                                    "address": {
                                        "socket_address": {
                                            "address": endpoint.address,
                                            "port_value": endpoint.port
                                        }
                                    }
                                },
                                "load_balancing_weight": endpoint.weight
                            }
                            for endpoint in cluster.endpoints
                        ]
                    }]
                }
        
        # Health check configuration
        if cluster.health_check:
            config["health_checks"] = [cluster.health_check]
        
        # Circuit breaker configuration
        if cluster.circuit_breaker:
            config["circuit_breakers"] = {
                "thresholds": [cluster.circuit_breaker]
            }
        
        # Outlier detection
        if cluster.outlier_detection:
            config["outlier_detection"] = cluster.outlier_detection
        
        # Retry policy
        if cluster.retry_policy:
            config["typed_extension_protocol_options"] = {
                "envoy.extensions.upstreams.http.v3.HttpProtocolOptions": {
                    "@type": "type.googleapis.com/envoy.extensions.upstreams.http.v3.HttpProtocolOptions",
                    "common_http_protocol_options": {
                        "idle_timeout": "60s"
                    }
                }
            }
        
        return config
    
    def generate_listener_config(self, listener: EnvoyListener) -> Dict[str, Any]:
        """Generate listener configuration"""        config = {
            "name": listener.name,
            "address": {
                "socket_address": {
                    "address": listener.address,
                    "port_value": listener.port
                }
            }
        }
        
        if listener.filter_chains:
            config["filter_chains"] = listener.filter_chains
        
        if listener.access_log:
            config["access_log"] = listener.access_log
        
        return config
    
    def generate_http_connection_manager(self, 
                                       routes: List[EnvoyRoute],
                                       access_log: bool = True,
                                       tracing: bool = True,
                                       stats_prefix: str = "ingress_http") -> Dict[str, Any]:
        """Generate HTTP connection manager filter"""        config = {
            "name": "envoy.filters.network.http_connection_manager",
            "typed_config": {
                "@type": "type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager",
                "stat_prefix": stats_prefix,
                "codec_type": "AUTO",
                "route_config": {
                    "name": "local_route",
                    "virtual_hosts": [{
                        "name": "ia_influencer_service",
                        "domains": ["*"],
                        "routes": [asdict(route) for route in routes]
                    }]
                },
                "http_filters": [
                    {
                        "name": "envoy.filters.http.router",
                        "typed_config": {
                            "@type": "type.googleapis.com/envoy.extensions.filters.http.router.v3.Router"
                        }
                    }
                ]
            }
        }
        
        # Add access logging
        if access_log:
            config["typed_config"]["access_log"] = [{
                "name": "envoy.access_loggers.file",
                "typed_config": {
                    "@type": "type.googleapis.com/envoy.extensions.access_loggers.file.v3.FileAccessLog",
                    "path": "/dev/stdout",
                    "format": json.dumps({
                        "start_time": "%START_TIME%",
                        "method": "%REQ(:METHOD)%",
                        "path": "%REQ(X-ENVOY-ORIGINAL-PATH?:PATH)%",
                        "protocol": "%PROTOCOL%",
                        "response_code": "%RESPONSE_CODE%",
                        "response_flags": "%RESPONSE_FLAGS%",
                        "bytes_received": "%BYTES_RECEIVED%",
                        "bytes_sent": "%BYTES_SENT%",
                        "duration": "%DURATION%",
                        "upstream_service_time": "%RESP(X-ENVOY-UPSTREAM-SERVICE-TIME)%",
                        "x_forwarded_for": "%REQ(X-FORWARDED-FOR)%",
                        "user_agent": "%REQ(USER-AGENT)%",
                        "request_id": "%REQ(X-REQUEST-ID)%",
                        "authority": "%REQ(:AUTHORITY)%",
                        "upstream_host": "%UPSTREAM_HOST%"
                    })
                }
            }]
        
        # Add tracing
        if tracing:
            config["typed_config"]["generate_request_id"] = True
            config["typed_config"]["tracing"] = {
                "client_sampling": {
                    "value": 100.0
                },
                "random_sampling": {
                    "value": 100.0
                },
                "overall_sampling": {
                    "value": 100.0
                }
            }
        
        return config
    
    def generate_complete_config(self, 
                               clusters: List[EnvoyCluster],
                               listeners: List[EnvoyListener]) -> Dict[str, Any]:
        """Generate complete Envoy configuration"""        config = {
            "admin": self.admin_config,
            "static_resources": {
                "listeners": [self.generate_listener_config(listener) for listener in listeners],
                "clusters": [self.generate_cluster_config(cluster) for cluster in clusters]
            },
            "tracing": self.tracing_config,
            "stats_sinks": [{
                "name": "envoy.stat_sinks.metrics_service",
                "typed_config": {
                    "@type": "type.googleapis.com/envoy.config.metrics.v3.MetricsServiceConfig",
                    "transport_api_version": "V3",
                    "grpc_service": {
                        "envoy_grpc": {
                            "cluster_name": "metrics-service"
                        }
                    }
                }
            }]
        }
        
        return config


class EnvoyManager:
    """Enterprise Envoy Proxy Load Balancer Manager"""    
    def __init__(self, config_file: str = "/etc/envoy/envoy.yaml"):
        self.config_file = Path(config_file)
        self.config_dir = self.config_file.parent
        self.config_generator = EnvoyConfigGenerator()
        self.clusters: List[EnvoyCluster] = []
        self.listeners: List[EnvoyListener] = []
        
        # Ensure directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def add_cluster(self, cluster: EnvoyCluster) -> bool:
        """Add cluster configuration"""        try:
            # Check if cluster already exists
            existing = next((c for c in self.clusters if c.name == cluster.name), None)
            if existing:
                self.clusters.remove(existing)
            
            self.clusters.append(cluster)
            logger.info(f"Cluster {cluster.name} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add cluster {cluster.name}: {e}")
            return False
    
    def add_listener(self, listener: EnvoyListener) -> bool:
        """Add listener configuration"""        try:
            # Check if listener already exists
            existing = next((l for l in self.listeners if l.name == listener.name), None)
            if existing:
                self.listeners.remove(existing)
            
            self.listeners.append(listener)
            logger.info(f"Listener {listener.name} added successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add listener {listener.name}: {e}")
            return False
    
    def configure_platform_services(self) -> bool:
        """Configure Envoy for platform services"""        try:
            # Define health check configurations
            http_health_check = {
                "timeout": "5s",
                "interval": "10s",
                "unhealthy_threshold": 3,
                "healthy_threshold": 2,
                "http_health_check": {
                    "path": "/health",
                    "expected_statuses": [{"start": 200, "end": 299}]
                }
            }
            
            # Define circuit breaker configuration
            circuit_breaker = {
                "priority": "DEFAULT",
                "max_connections": 1000,
                "max_pending_requests": 100,
                "max_requests": 1000,
                "max_retries": 3
            }
            
            # Define outlier detection
            outlier_detection = {
                "consecutive_5xx": 3,
                "consecutive_gateway_failure": 3,
                "interval": "30s",
                "base_ejection_time": "30s",
                "max_ejection_percent": 50,
                "min_health_percent": 50
            }
            
            # Configure clusters for different services
            clusters = [
                EnvoyCluster(
                    name="fingerprinting_service",
                    lb_policy="LEAST_REQUEST",
                    endpoints=[
                        EnvoyEndpoint("fingerprint-service-1", 8001, weight=2),
                        EnvoyEndpoint("fingerprint-service-2", 8001, weight=2),
                        EnvoyEndpoint("fingerprint-service-3", 8001, weight=1)
                    ],
                    health_check=http_health_check,
                    circuit_breaker=circuit_breaker,
                    outlier_detection=outlier_detection,
                    timeout="300s"  # Extended for fingerprinting
                ),
                EnvoyCluster(
                    name="protection_service",
                    lb_policy="ROUND_ROBIN",
                    endpoints=[
                        EnvoyEndpoint("protection-service-1", 8002, weight=3),
                        EnvoyEndpoint("protection-service-2", 8002, weight=2)
                    ],
                    health_check=http_health_check,
                    circuit_breaker=circuit_breaker,
                    outlier_detection=outlier_detection
                ),
                EnvoyCluster(
                    name="monetization_service",
                    lb_policy="RING_HASH",  # Consistent hashing for session affinity
                    endpoints=[
                        EnvoyEndpoint("monetization-service-1", 8003, weight=2),
                        EnvoyEndpoint("monetization-service-2", 8003, weight=2)
                    ],
                    health_check=http_health_check,
                    circuit_breaker=circuit_breaker,
                    outlier_detection=outlier_detection
                ),
                EnvoyCluster(
                    name="ai_agent_service",
                    lb_policy="LEAST_REQUEST",
                    endpoints=[
                        EnvoyEndpoint("ai-agent-service-1", 8004, weight=3),
                        EnvoyEndpoint("ai-agent-service-2", 8004, weight=2)
                    ],
                    health_check=http_health_check,
                    circuit_breaker=circuit_breaker,
                    outlier_detection=outlier_detection,
                    timeout="120s"  # Extended for AI processing
                ),
                EnvoyCluster(
                    name="crawler_service",
                    lb_policy="ROUND_ROBIN",
                    endpoints=[
                        EnvoyEndpoint("crawler-service-1", 8005, weight=1),
                        EnvoyEndpoint("crawler-service-2", 8005, weight=1)
                    ],
                    health_check=http_health_check,
                    circuit_breaker=circuit_breaker,
                    outlier_detection=outlier_detection
                ),
                # Observability clusters
                EnvoyCluster(
                    name="jaeger",
                    type="STRICT_DNS",
                    endpoints=[
                        EnvoyEndpoint("jaeger-collector", 14268)
                    ]
                ),
                EnvoyCluster(
                    name="metrics-service",
                    type="STRICT_DNS",
                    endpoints=[
                        EnvoyEndpoint("prometheus", 9090)
                    ]
                )
            ]
            
            # Add all clusters
            for cluster in clusters:
                self.add_cluster(cluster)
            
            # Configure routes
            routes = [
                EnvoyRoute(
                    match={"prefix": "/api/v1/fingerprinting/"},
                    route={
                        "cluster": "fingerprinting_service",
                        "timeout": "300s",
                        "retry_policy": {
                            "retry_on": "5xx,gateway-error,connect-failure,refused-stream",
                            "num_retries": 3,
                            "per_try_timeout": "10s"
                        }
                    },
                    decorator={"operation": "fingerprinting"}
                ),
                EnvoyRoute(
                    match={"prefix": "/api/v1/protection/"},
                    route={
                        "cluster": "protection_service",
                        "timeout": "60s",
                        "retry_policy": {
                            "retry_on": "5xx,gateway-error,connect-failure,refused-stream",
                            "num_retries": 3,
                            "per_try_timeout": "5s"
                        }
                    },
                    decorator={"operation": "protection"}
                ),
                EnvoyRoute(
                    match={"prefix": "/api/v1/monetization/"},
                    route={
                        "cluster": "monetization_service",
                        "timeout": "60s",
                        "hash_policy": [{
                            "header": {
                                "header_name": "x-user-id"
                            }
                        }],
                        "retry_policy": {
                            "retry_on": "5xx,gateway-error,connect-failure,refused-stream",
                            "num_retries": 2,
                            "per_try_timeout": "5s"
                        }
                    },
                    decorator={"operation": "monetization"}
                ),
                EnvoyRoute(
                    match={"prefix": "/api/v1/ai-agent/"},
                    route={
                        "cluster": "ai_agent_service",
                        "timeout": "120s",
                        "retry_policy": {
                            "retry_on": "5xx,gateway-error,connect-failure,refused-stream",
                            "num_retries": 2,
                            "per_try_timeout": "10s"
                        }
                    },
                    decorator={"operation": "ai_agent"}
                ),
                EnvoyRoute(
                    match={"prefix": "/api/v1/crawlers/"},
                    route={
                        "cluster": "crawler_service",
                        "timeout": "60s",
                        "retry_policy": {
                            "retry_on": "5xx,gateway-error,connect-failure,refused-stream",
                            "num_retries": 3,
                            "per_try_timeout": "5s"
                        }
                    },
                    decorator={"operation": "crawler"}
                ),
                EnvoyRoute(
                    match={"prefix": "/"},
                    route={
                        "cluster": "ai_agent_service",
                        "timeout": "30s"
                    },
                    decorator={"operation": "default"}
                )
            ]
            
            # Configure HTTP connection manager
            http_filter = self.config_generator.generate_http_connection_manager(
                routes=routes,
                access_log=True,
                tracing=True,
                stats_prefix="ia_influencer_ingress"
            )
            
            # Configure main listener
            main_listener = EnvoyListener(
                name="ia_influencer_listener",
                address="0.0.0.0",
                port=80,
                filter_chains=[{
                    "filters": [http_filter]
                }]
            )
            
            # Configure HTTPS listener
            https_listener = EnvoyListener(
                name="ia_influencer_https_listener",
                address="0.0.0.0",
                port=443,
                filter_chains=[{
                    "transport_socket": {
                        "name": "envoy.transport_sockets.tls",
                        "typed_config": {
                            "@type": "type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext",
                            "common_tls_context": {
                                "tls_certificates": [{
                                    "certificate_chain": {
                                        "filename": "/etc/ssl/certs/ia-influencer.com.crt"
                                    },
                                    "private_key": {
                                        "filename": "/etc/ssl/private/ia-influencer.com.key"
                                    }
                                }]
                            }
                        }
                    },
                    "filters": [http_filter]
                }]
            )
            
            # Add listeners
            self.add_listener(main_listener)
            self.add_listener(https_listener)
            
            logger.info("Platform services configured successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure platform services: {e}")
            return False
    
    def generate_configuration(self) -> Dict[str, Any]:
        """Generate complete Envoy configuration"""        try:
            return self.config_generator.generate_complete_config(
                clusters=self.clusters,
                listeners=self.listeners
            )
            
        except Exception as e:
            logger.error(f"Failed to generate configuration: {e}")
            return {}
    
    def write_configuration(self) -> bool:
        """Write configuration to file"""        try:
            config_data = self.generate_configuration()
            if not config_data:
                logger.error("Failed to generate configuration data")
                return False
            
            # Backup existing configuration
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix(f".bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                self.config_file.rename(backup_file)
                logger.info(f"Existing configuration backed up to {backup_file}")
            
            # Write new configuration
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration written to {self.config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write configuration: {e}")
            return False
    
    def test_configuration(self) -> bool:
        """Test Envoy configuration validity"""        try:
            result = subprocess.run(
                ['envoy', '--mode', 'validate', '--config-path', str(self.config_file)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Envoy configuration test passed")
                return True
            else:
                logger.error(f"Envoy configuration test failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to test configuration: {e}")
            return False
    
    def get_admin_stats(self) -> Dict[str, Any]:
        """Get Envoy admin statistics"""        try:
            # Try to connect to admin interface
            response = requests.get("http://127.0.0.1:9901/stats/prometheus", timeout=5)
            if response.status_code == 200:
                return {
                    'stats_available': True,
                    'prometheus_metrics': response.text,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'stats_available': False,
                    'error': f"Admin interface returned {response.status_code}",
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Failed to get Envoy admin stats: {e}")
            return {
                'stats_available': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get Envoy status and health"""        try:
            # Check if Envoy is running
            ps_result = subprocess.run(['pgrep', 'envoy'], capture_output=True, text=True)
            is_running = ps_result.returncode == 0
            
            status = {
                'is_running': is_running,
                'config_test_passed': self.test_configuration(),
                'clusters_count': len(self.clusters),
                'listeners_count': len(self.listeners),
                'config_file': str(self.config_file),
                'timestamp': datetime.now().isoformat()
            }
            
            if is_running:
                # Get admin stats
                admin_stats = self.get_admin_stats()
                status['admin_interface'] = admin_stats
                
                # Get process info
                ps_info = subprocess.run(
                    ['ps', '-p', ps_result.stdout.strip(), '-o', 'pid,ppid,cmd'],
                    capture_output=True,
                    text=True
                )
                status['process_info'] = ps_info.stdout if ps_info.returncode == 0 else None
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get Envoy status: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
