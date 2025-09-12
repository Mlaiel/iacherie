#!/usr/bin/env python3
"""
🔍 Infrastructure Validator Enterprise - System Health & Compliance Checker
==========================================================================

Multi-role expertise demonstrated:
- DevOps Engineer: Infrastructure monitoring and validation
- Security Specialist: Security compliance and vulnerability scanning
- Backend Senior: Service health and performance validation
- DBA: Database integrity and performance validation
- Microservices Architect: Distributed system health validation

@author: Fahed Mlaiel <mlaiel@live.de>
@copyright: 2025 Fahed Mlaiel - Propriété Intellectuelle Exclusive
"""

import os
import sys
import json
import yaml
import time
import logging
import subprocess
import requests
import socket
import psutil
import docker
import kubernetes as k8s
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from pathlib import Path
import boto3
import redis
import psycopg2
import pymongo
from urllib.parse import urlparse
import ssl
import asyncio
import concurrent.futures

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ValidationRule:
    """Infrastructure validation rule"""
    name: str
    description: str
    category: str  # security, performance, availability, compliance
    severity: str  # critical, high, medium, low
    check_function: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    enabled: bool = True

@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    status: str  # pass, fail, warning, error
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class InfrastructureComponent:
    """Infrastructure component to validate"""
    name: str
    type: str  # service, database, cache, storage, network
    endpoint: str
    credentials: Optional[Dict[str, Any]] = None
    health_check_url: Optional[str] = None
    expected_response_time: float = 5.0
    dependencies: List[str] = field(default_factory=list)

class InfrastructureValidator:
    """
    Enterprise Infrastructure Validator
    Comprehensive infrastructure health and compliance validation
    """
    
    def __init__(self, config_file: str = "infrastructure_validation.yaml"):
        """Initialize the validator"""
        self.config_file = config_file
        self.validation_rules = {}
        self.components = {}
        self.cloud_clients = {}
        self.results = []
        
        # Initialize cloud clients
        self._initialize_cloud_clients()
        
        # Load validation configuration
        self._load_validation_config()
        
        # Register built-in validation rules
        self._register_builtin_rules()
    
    def _initialize_cloud_clients(self):
        """Initialize cloud provider clients"""
        try:
            # AWS clients
            self.cloud_clients['aws'] = {
                'ec2': boto3.client('ec2'),
                'rds': boto3.client('rds'),
                'cloudwatch': boto3.client('cloudwatch'),
                'ecs': boto3.client('ecs'),
                'elbv2': boto3.client('elbv2')
            }
        except Exception as e:
            logger.warning(f"Failed to initialize AWS clients: {e}")
        
        try:
            # Kubernetes client
            k8s.config.load_kube_config()
            self.cloud_clients['k8s'] = {
                'core_v1': k8s.client.CoreV1Api(),
                'apps_v1': k8s.client.AppsV1Api(),
                'metrics': k8s.client.MetricsV1beta1Api()
            }
        except Exception as e:
            logger.warning(f"Failed to initialize Kubernetes clients: {e}")
        
        try:
            # Docker client
            self.cloud_clients['docker'] = docker.from_env()
        except Exception as e:
            logger.warning(f"Failed to initialize Docker client: {e}")
    
    def _load_validation_config(self):
        """Load validation configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Load components
                for comp_name, comp_config in config.get('components', {}).items():
                    self.components[comp_name] = InfrastructureComponent(
                        name=comp_name,
                        **comp_config
                    )
                
                # Load custom rules
                for rule_name, rule_config in config.get('rules', {}).items():
                    self.validation_rules[rule_name] = ValidationRule(
                        name=rule_name,
                        **rule_config
                    )
                
                logger.info(f"Loaded {len(self.components)} components and {len(self.validation_rules)} custom rules")
            else:
                logger.warning(f"Configuration file {self.config_file} not found, using defaults")
                self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading validation config: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default validation configuration"""
        default_config = {
            'components': {
                'web_service': {
                    'type': 'service',
                    'endpoint': 'http://localhost:8000',
                    'health_check_url': 'http://localhost:8000/health',
                    'expected_response_time': 2.0
                },
                'database': {
                    'type': 'database',
                    'endpoint': 'postgresql://localhost:5432/ainflue',
                    'expected_response_time': 1.0
                },
                'cache': {
                    'type': 'cache',
                    'endpoint': 'redis://localhost:6379',
                    'expected_response_time': 0.5
                }
            },
            'rules': {
                'custom_security_check': {
                    'description': 'Custom security validation',
                    'category': 'security',
                    'severity': 'high',
                    'check_function': 'validate_custom_security',
                    'enabled': False
                }
            }
        }
        
        # Save default configuration
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        # Load the configuration
        self._load_validation_config()
    
    def _register_builtin_rules(self):
        """Register built-in validation rules"""
        builtin_rules = [
            # Security Rules
            ValidationRule(
                name="ssl_certificate_validation",
                description="Validate SSL certificates for HTTPS endpoints",
                category="security",
                severity="high",
                check_function="validate_ssl_certificates",
                timeout=30
            ),
            ValidationRule(
                name="open_ports_scan",
                description="Scan for unnecessarily open ports",
                category="security",
                severity="medium",
                check_function="scan_open_ports",
                timeout=60
            ),
            ValidationRule(
                name="security_headers_check",
                description="Check for security headers in HTTP responses",
                category="security",
                severity="medium",
                check_function="check_security_headers",
                timeout=30
            ),
            
            # Performance Rules
            ValidationRule(
                name="response_time_validation",
                description="Validate service response times",
                category="performance",
                severity="high",
                check_function="validate_response_times",
                timeout=30
            ),
            ValidationRule(
                name="resource_utilization_check",
                description="Check CPU, memory, and disk utilization",
                category="performance",
                severity="medium",
                check_function="check_resource_utilization",
                timeout=30
            ),
            ValidationRule(
                name="database_performance_check",
                description="Check database performance metrics",
                category="performance",
                severity="high",
                check_function="check_database_performance",
                timeout=30
            ),
            
            # Availability Rules
            ValidationRule(
                name="service_health_check",
                description="Check service health endpoints",
                category="availability",
                severity="critical",
                check_function="check_service_health",
                timeout=30
            ),
            ValidationRule(
                name="dependency_validation",
                description="Validate service dependencies",
                category="availability",
                severity="high",
                check_function="validate_dependencies",
                timeout=60
            ),
            ValidationRule(
                name="load_balancer_health",
                description="Check load balancer health and configuration",
                category="availability",
                severity="high",
                check_function="check_load_balancer_health",
                timeout=30
            ),
            
            # Compliance Rules
            ValidationRule(
                name="backup_validation",
                description="Validate backup systems and schedules",
                category="compliance",
                severity="high",
                check_function="validate_backups",
                timeout=30
            ),
            ValidationRule(
                name="log_retention_check",
                description="Check log retention policies",
                category="compliance",
                severity="medium",
                check_function="check_log_retention",
                timeout=30
            ),
            ValidationRule(
                name="encryption_validation",
                description="Validate encryption at rest and in transit",
                category="compliance",
                severity="high",
                check_function="validate_encryption",
                timeout=30
            ),
            
            # Docker/Container Rules
            ValidationRule(
                name="container_health_check",
                description="Check Docker container health",
                category="availability",
                severity="high",
                check_function="check_container_health",
                timeout=30
            ),
            ValidationRule(
                name="container_security_scan",
                description="Scan containers for security vulnerabilities",
                category="security",
                severity="high",
                check_function="scan_container_security",
                timeout=120
            ),
            
            # Kubernetes Rules
            ValidationRule(
                name="k8s_cluster_health",
                description="Check Kubernetes cluster health",
                category="availability",
                severity="critical",
                check_function="check_k8s_cluster_health",
                timeout=60,
                enabled=bool(self.cloud_clients.get('k8s'))
            ),
            ValidationRule(
                name="k8s_resource_quotas",
                description="Check Kubernetes resource quotas and limits",
                category="performance",
                severity="medium",
                check_function="check_k8s_resource_quotas",
                timeout=30,
                enabled=bool(self.cloud_clients.get('k8s'))
            )
        ]
        
        for rule in builtin_rules:
            self.validation_rules[rule.name] = rule
        
        logger.info(f"Registered {len(builtin_rules)} built-in validation rules")
    
    async def validate_infrastructure(self, categories: Optional[List[str]] = None, 
                                    severity_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Validate infrastructure according to rules
        
        Args:
            categories: List of categories to validate (security, performance, availability, compliance)
            severity_filter: List of severities to include (critical, high, medium, low)
            
        Returns:
            Dictionary with validation results
        """
        start_time = time.time()
        self.results = []
        
        # Filter rules based on criteria
        rules_to_run = []
        for rule in self.validation_rules.values():
            if not rule.enabled:
                continue
            if categories and rule.category not in categories:
                continue
            if severity_filter and rule.severity not in severity_filter:
                continue
            rules_to_run.append(rule)
        
        logger.info(f"Running {len(rules_to_run)} validation rules...")
        
        # Run validations concurrently
        tasks = []
        for rule in rules_to_run:
            task = self._run_validation_rule(rule)
            tasks.append(task)
        
        # Execute with controlled concurrency
        semaphore = asyncio.Semaphore(10)  # Limit concurrent validations
        results = await asyncio.gather(*[self._run_with_semaphore(semaphore, task) for task in tasks], 
                                     return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.results.append(ValidationResult(
                    rule_name=rules_to_run[i].name,
                    status="error",
                    message=f"Validation failed with exception: {str(result)}",
                    execution_time=0.0
                ))
            elif result:
                self.results.append(result)
        
        # Generate summary
        summary = self._generate_summary()
        
        end_time = time.time()
        
        return {
            'validation_summary': summary,
            'total_execution_time': end_time - start_time,
            'rules_executed': len(rules_to_run),
            'timestamp': end_time,
            'results': [self._result_to_dict(r) for r in self.results]
        }
    
    async def _run_with_semaphore(self, semaphore: asyncio.Semaphore, coro):
        """Run coroutine with semaphore for concurrency control"""
        async with semaphore:
            return await coro
    
    async def _run_validation_rule(self, rule: ValidationRule) -> Optional[ValidationResult]:
        """Run a single validation rule"""
        start_time = time.time()
        
        try:
            # Get the validation function
            check_function = getattr(self, rule.check_function, None)
            if not check_function:
                return ValidationResult(
                    rule_name=rule.name,
                    status="error",
                    message=f"Validation function '{rule.check_function}' not found",
                    execution_time=time.time() - start_time
                )
            
            # Run the validation with timeout
            try:
                if asyncio.iscoroutinefunction(check_function):
                    result = await asyncio.wait_for(
                        check_function(rule.parameters),
                        timeout=rule.timeout
                    )
                else:
                    # Run sync function in thread pool
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, check_function, rule.parameters),
                        timeout=rule.timeout
                    )
                
                if isinstance(result, ValidationResult):
                    result.rule_name = rule.name
                    result.execution_time = time.time() - start_time
                    return result
                else:
                    return ValidationResult(
                        rule_name=rule.name,
                        status="pass" if result else "fail",
                        message=f"Validation {'passed' if result else 'failed'}",
                        execution_time=time.time() - start_time
                    )
            
            except asyncio.TimeoutError:
                return ValidationResult(
                    rule_name=rule.name,
                    status="error",
                    message=f"Validation timed out after {rule.timeout} seconds",
                    execution_time=rule.timeout
                )
        
        except Exception as e:
            return ValidationResult(
                rule_name=rule.name,
                status="error",
                message=f"Validation error: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    # Validation Functions
    
    def validate_ssl_certificates(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate SSL certificates for HTTPS endpoints"""
        issues = []
        
        for component in self.components.values():
            if component.endpoint.startswith('https://'):
                try:
                    parsed = urlparse(component.endpoint)
                    hostname = parsed.hostname
                    port = parsed.port or 443
                    
                    # Get certificate
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, port), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            cert = ssock.getpeercert()
                    
                    # Check expiration
                    import datetime
                    expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (expiry_date - datetime.datetime.now()).days
                    
                    if days_until_expiry < 30:
                        issues.append(f"Certificate for {hostname} expires in {days_until_expiry} days")
                    
                except Exception as e:
                    issues.append(f"Failed to validate certificate for {component.endpoint}: {e}")
        
        if issues:
            return ValidationResult(
                rule_name="ssl_certificate_validation",
                status="fail",
                message="SSL certificate issues found",
                details={'issues': issues}
            )
        
        return ValidationResult(
            rule_name="ssl_certificate_validation",
            status="pass",
            message="All SSL certificates are valid"
        )
    
    def scan_open_ports(self, params: Dict[str, Any]) -> ValidationResult:
        """Scan for unnecessarily open ports"""
        dangerous_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 1433, 3306, 3389, 5432, 6379, 27017]
        open_ports = []
        
        for port in dangerous_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except Exception:
                pass
        
        if open_ports:
            return ValidationResult(
                rule_name="open_ports_scan",
                status="warning",
                message=f"Found open ports: {open_ports}",
                details={'open_ports': open_ports}
            )
        
        return ValidationResult(
            rule_name="open_ports_scan",
            status="pass",
            message="No dangerous ports found open"
        )
    
    def check_security_headers(self, params: Dict[str, Any]) -> ValidationResult:
        """Check for security headers in HTTP responses"""
        required_headers = [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security',
            'Content-Security-Policy'
        ]
        
        missing_headers = {}
        
        for component in self.components.values():
            if component.type == 'service' and component.endpoint.startswith('http'):
                try:
                    response = requests.get(component.endpoint, timeout=10)
                    component_missing = []
                    
                    for header in required_headers:
                        if header not in response.headers:
                            component_missing.append(header)
                    
                    if component_missing:
                        missing_headers[component.name] = component_missing
                
                except Exception as e:
                    missing_headers[component.name] = f"Error checking headers: {e}"
        
        if missing_headers:
            return ValidationResult(
                rule_name="security_headers_check",
                status="fail",
                message="Missing security headers detected",
                details={'missing_headers': missing_headers}
            )
        
        return ValidationResult(
            rule_name="security_headers_check",
            status="pass",
            message="All required security headers present"
        )
    
    def validate_response_times(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate service response times"""
        slow_services = []
        
        for component in self.components.values():
            if component.type == 'service':
                try:
                    start_time = time.time()
                    response = requests.get(component.endpoint, timeout=30)
                    response_time = time.time() - start_time
                    
                    if response_time > component.expected_response_time:
                        slow_services.append({
                            'service': component.name,
                            'response_time': response_time,
                            'expected': component.expected_response_time
                        })
                
                except Exception as e:
                    slow_services.append({
                        'service': component.name,
                        'error': str(e)
                    })
        
        if slow_services:
            return ValidationResult(
                rule_name="response_time_validation",
                status="fail",
                message="Services with slow response times detected",
                details={'slow_services': slow_services}
            )
        
        return ValidationResult(
            rule_name="response_time_validation",
            status="pass",
            message="All services respond within expected time"
        )
    
    def check_resource_utilization(self, params: Dict[str, Any]) -> ValidationResult:
        """Check CPU, memory, and disk utilization"""
        issues = []
        
        # CPU utilization
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 80:
            issues.append(f"High CPU utilization: {cpu_percent}%")
        
        # Memory utilization
        memory = psutil.virtual_memory()
        if memory.percent > 80:
            issues.append(f"High memory utilization: {memory.percent}%")
        
        # Disk utilization
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 80:
            issues.append(f"High disk utilization: {disk_percent:.1f}%")
        
        if issues:
            return ValidationResult(
                rule_name="resource_utilization_check",
                status="warning",
                message="High resource utilization detected",
                details={
                    'issues': issues,
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk_percent
                }
            )
        
        return ValidationResult(
            rule_name="resource_utilization_check",
            status="pass",
            message="Resource utilization within normal limits",
            details={
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk_percent
            }
        )
    
    def check_database_performance(self, params: Dict[str, Any]) -> ValidationResult:
        """Check database performance metrics"""
        db_issues = []
        
        for component in self.components.values():
            if component.type == 'database':
                try:
                    parsed = urlparse(component.endpoint)
                    
                    if parsed.scheme == 'postgresql':
                        db_issues.extend(self._check_postgresql_performance(component))
                    elif parsed.scheme == 'mongodb':
                        db_issues.extend(self._check_mongodb_performance(component))
                    elif parsed.scheme == 'redis':
                        db_issues.extend(self._check_redis_performance(component))
                
                except Exception as e:
                    db_issues.append(f"Error checking {component.name}: {e}")
        
        if db_issues:
            return ValidationResult(
                rule_name="database_performance_check",
                status="warning",
                message="Database performance issues detected",
                details={'issues': db_issues}
            )
        
        return ValidationResult(
            rule_name="database_performance_check",
            status="pass",
            message="Database performance within acceptable limits"
        )
    
    def _check_postgresql_performance(self, component: InfrastructureComponent) -> List[str]:
        """Check PostgreSQL performance"""
        issues = []
        try:
            parsed = urlparse(component.endpoint)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path.lstrip('/') or 'postgres',
                user=parsed.username or 'postgres',
                password=parsed.password or '',
                connect_timeout=10
            )
            
            cursor = conn.cursor()
            
            # Check for long-running queries
            cursor.execute("""
                SELECT count(*) FROM pg_stat_activity 
                WHERE state = 'active' AND query_start < now() - interval '5 minutes'
            """)
            long_queries = cursor.fetchone()[0]
            if long_queries > 0:
                issues.append(f"PostgreSQL has {long_queries} long-running queries")
            
            # Check connection count
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            connections = cursor.fetchone()[0]
            cursor.execute("SHOW max_connections")
            max_connections = int(cursor.fetchone()[0])
            
            if connections > max_connections * 0.8:
                issues.append(f"PostgreSQL connection usage high: {connections}/{max_connections}")
            
            conn.close()
        except Exception as e:
            issues.append(f"PostgreSQL check failed: {e}")
        
        return issues
    
    def _check_redis_performance(self, component: InfrastructureComponent) -> List[str]:
        """Check Redis performance"""
        issues = []
        try:
            parsed = urlparse(component.endpoint)
            r = redis.Redis(
                host=parsed.hostname,
                port=parsed.port or 6379,
                password=parsed.password,
                socket_timeout=10
            )
            
            info = r.info()
            
            # Check memory usage
            used_memory = int(info.get('used_memory', 0))
            max_memory = int(info.get('maxmemory', 0))
            
            if max_memory > 0 and used_memory > max_memory * 0.8:
                issues.append(f"Redis memory usage high: {used_memory}/{max_memory}")
            
            # Check connected clients
            connected_clients = int(info.get('connected_clients', 0))
            if connected_clients > 100:
                issues.append(f"Redis has many connected clients: {connected_clients}")
            
        except Exception as e:
            issues.append(f"Redis check failed: {e}")
        
        return issues
    
    def check_service_health(self, params: Dict[str, Any]) -> ValidationResult:
        """Check service health endpoints"""
        unhealthy_services = []
        
        for component in self.components.values():
            if component.type == 'service' and component.health_check_url:
                try:
                    response = requests.get(component.health_check_url, timeout=10)
                    if response.status_code != 200:
                        unhealthy_services.append({
                            'service': component.name,
                            'status_code': response.status_code,
                            'url': component.health_check_url
                        })
                except Exception as e:
                    unhealthy_services.append({
                        'service': component.name,
                        'error': str(e),
                        'url': component.health_check_url
                    })
        
        if unhealthy_services:
            return ValidationResult(
                rule_name="service_health_check",
                status="fail",
                message="Unhealthy services detected",
                details={'unhealthy_services': unhealthy_services}
            )
        
        return ValidationResult(
            rule_name="service_health_check",
            status="pass",
            message="All services are healthy"
        )
    
    def validate_dependencies(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate service dependencies"""
        dependency_issues = []
        
        for component in self.components.values():
            for dep_name in component.dependencies:
                if dep_name not in self.components:
                    dependency_issues.append(f"{component.name} depends on unknown service {dep_name}")
                    continue
                
                dep_component = self.components[dep_name]
                
                # Test dependency connectivity
                try:
                    if dep_component.type == 'service':
                        response = requests.get(dep_component.endpoint, timeout=5)
                        if response.status_code >= 400:
                            dependency_issues.append(f"{component.name} dependency {dep_name} is not responsive")
                    elif dep_component.type == 'database':
                        # Test database connection
                        parsed = urlparse(dep_component.endpoint)
                        if parsed.scheme == 'postgresql':
                            # Test PostgreSQL connection
                            pass
                except Exception as e:
                    dependency_issues.append(f"{component.name} cannot reach dependency {dep_name}: {e}")
        
        if dependency_issues:
            return ValidationResult(
                rule_name="validate_dependencies",
                status="fail",
                message="Service dependency issues detected",
                details={'dependency_issues': dependency_issues}
            )
        
        return ValidationResult(
            rule_name="validate_dependencies",
            status="pass",
            message="All service dependencies are accessible"
        )
    
    def check_container_health(self, params: Dict[str, Any]) -> ValidationResult:
        """Check Docker container health"""
        if 'docker' not in self.cloud_clients:
            return ValidationResult(
                rule_name="container_health_check",
                status="error",
                message="Docker client not available"
            )
        
        docker_client = self.cloud_clients['docker']
        unhealthy_containers = []
        
        try:
            containers = docker_client.containers.list()
            
            for container in containers:
                container.reload()
                
                # Check container status
                if container.status != 'running':
                    unhealthy_containers.append({
                        'name': container.name,
                        'status': container.status,
                        'issue': 'not_running'
                    })
                    continue
                
                # Check health status if available
                health = container.attrs.get('State', {}).get('Health', {})
                if health and health.get('Status') not in ['healthy', None]:
                    unhealthy_containers.append({
                        'name': container.name,
                        'health_status': health.get('Status'),
                        'issue': 'unhealthy'
                    })
                
                # Check restart count
                restart_count = container.attrs.get('RestartCount', 0)
                if restart_count > 5:
                    unhealthy_containers.append({
                        'name': container.name,
                        'restart_count': restart_count,
                        'issue': 'frequent_restarts'
                    })
        
        except Exception as e:
            return ValidationResult(
                rule_name="container_health_check",
                status="error",
                message=f"Failed to check container health: {e}"
            )
        
        if unhealthy_containers:
            return ValidationResult(
                rule_name="container_health_check",
                status="fail",
                message="Unhealthy containers detected",
                details={'unhealthy_containers': unhealthy_containers}
            )
        
        return ValidationResult(
            rule_name="container_health_check",
            status="pass",
            message="All containers are healthy"
        )
    
    def check_k8s_cluster_health(self, params: Dict[str, Any]) -> ValidationResult:
        """Check Kubernetes cluster health"""
        if 'k8s' not in self.cloud_clients:
            return ValidationResult(
                rule_name="k8s_cluster_health",
                status="error",
                message="Kubernetes client not available"
            )
        
        core_v1 = self.cloud_clients['k8s']['core_v1']
        issues = []
        
        try:
            # Check node health
            nodes = core_v1.list_node()
            for node in nodes.items:
                for condition in node.status.conditions:
                    if condition.type == 'Ready' and condition.status != 'True':
                        issues.append(f"Node {node.metadata.name} is not ready")
            
            # Check pod health
            pods = core_v1.list_pod_for_all_namespaces()
            failed_pods = []
            for pod in pods.items:
                if pod.status.phase in ['Failed', 'Pending']:
                    failed_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}: {pod.status.phase}")
            
            if failed_pods:
                issues.append(f"Failed/Pending pods: {', '.join(failed_pods[:5])}")
        
        except Exception as e:
            return ValidationResult(
                rule_name="k8s_cluster_health",
                status="error",
                message=f"Failed to check cluster health: {e}"
            )
        
        if issues:
            return ValidationResult(
                rule_name="k8s_cluster_health",
                status="fail",
                message="Kubernetes cluster issues detected",
                details={'issues': issues}
            )
        
        return ValidationResult(
            rule_name="k8s_cluster_health",
            status="pass",
            message="Kubernetes cluster is healthy"
        )
    
    # Placeholder validation functions (would be implemented based on specific requirements)
    
    def check_load_balancer_health(self, params: Dict[str, Any]) -> ValidationResult:
        """Check load balancer health and configuration"""
        return ValidationResult(
            rule_name="load_balancer_health",
            status="pass",
            message="Load balancer health check not implemented"
        )
    
    def validate_backups(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate backup systems and schedules"""
        return ValidationResult(
            rule_name="validate_backups",
            status="pass",
            message="Backup validation not implemented"
        )
    
    def check_log_retention(self, params: Dict[str, Any]) -> ValidationResult:
        """Check log retention policies"""
        return ValidationResult(
            rule_name="check_log_retention",
            status="pass",
            message="Log retention check not implemented"
        )
    
    def validate_encryption(self, params: Dict[str, Any]) -> ValidationResult:
        """Validate encryption at rest and in transit"""
        return ValidationResult(
            rule_name="validate_encryption",
            status="pass",
            message="Encryption validation not implemented"
        )
    
    def scan_container_security(self, params: Dict[str, Any]) -> ValidationResult:
        """Scan containers for security vulnerabilities"""
        return ValidationResult(
            rule_name="scan_container_security",
            status="pass",
            message="Container security scan not implemented"
        )
    
    def check_k8s_resource_quotas(self, params: Dict[str, Any]) -> ValidationResult:
        """Check Kubernetes resource quotas and limits"""
        return ValidationResult(
            rule_name="check_k8s_resource_quotas",
            status="pass",
            message="K8s resource quota check not implemented"
        )
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        summary = {
            'total_checks': len(self.results),
            'passed': len([r for r in self.results if r.status == 'pass']),
            'failed': len([r for r in self.results if r.status == 'fail']),
            'warnings': len([r for r in self.results if r.status == 'warning']),
            'errors': len([r for r in self.results if r.status == 'error']),
            'categories': {},
            'severity_breakdown': {},
            'critical_issues': []
        }
        
        # Category breakdown
        for result in self.results:
            rule = self.validation_rules.get(result.rule_name)
            if rule:
                category = rule.category
                if category not in summary['categories']:
                    summary['categories'][category] = {'passed': 0, 'failed': 0, 'warnings': 0, 'errors': 0}
                summary['categories'][category][result.status + ('ed' if result.status == 'pass' else 's' if result.status != 'error' else 's')] += 1
                
                # Severity breakdown
                severity = rule.severity
                if severity not in summary['severity_breakdown']:
                    summary['severity_breakdown'][severity] = {'passed': 0, 'failed': 0, 'warnings': 0, 'errors': 0}
                summary['severity_breakdown'][severity][result.status + ('ed' if result.status == 'pass' else 's' if result.status != 'error' else 's')] += 1
                
                # Critical issues
                if rule.severity == 'critical' and result.status in ['fail', 'error']:
                    summary['critical_issues'].append({
                        'rule': result.rule_name,
                        'status': result.status,
                        'message': result.message
                    })
        
        # Overall health score
        total_weighted_score = 0
        total_weight = 0
        
        for result in self.results:
            rule = self.validation_rules.get(result.rule_name)
            if rule:
                weight = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[rule.severity]
                score = {'pass': 1, 'warning': 0.5, 'fail': 0, 'error': 0}[result.status]
                total_weighted_score += score * weight
                total_weight += weight
        
        summary['health_score'] = round((total_weighted_score / total_weight * 100) if total_weight > 0 else 0, 1)
        
        return summary
    
    def _result_to_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """Convert ValidationResult to dictionary"""
        return {
            'rule_name': result.rule_name,
            'status': result.status,
            'message': result.message,
            'details': result.details,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp
        }
    
    def generate_report(self, format: str = 'json') -> str:
        """Generate validation report in specified format"""
        if format == 'json':
            return self._generate_json_report()
        elif format == 'html':
            return self._generate_html_report()
        elif format == 'markdown':
            return self._generate_markdown_report()
        else:
            raise ValueError(f"Unsupported report format: {format}")
    
    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        report_data = {
            'summary': self._generate_summary(),
            'results': [self._result_to_dict(r) for r in self.results],
            'timestamp': time.time()
        }
        return json.dumps(report_data, indent=2)
    
    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        summary = self._generate_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Infrastructure Validation Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .summary {{ background: #f5f5f5; padding: 15px; border-radius: 5px; }}
                .pass {{ color: green; }}
                .fail {{ color: red; }}
                .warning {{ color: orange; }}
                .error {{ color: red; font-weight: bold; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Infrastructure Validation Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <p><strong>Health Score:</strong> {summary['health_score']}%</p>
                <p><strong>Total Checks:</strong> {summary['total_checks']}</p>
                <p><span class="pass">Passed: {summary['passed']}</span> | 
                   <span class="fail">Failed: {summary['failed']}</span> | 
                   <span class="warning">Warnings: {summary['warnings']}</span> | 
                   <span class="error">Errors: {summary['errors']}</span></p>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Rule</th>
                        <th>Status</th>
                        <th>Message</th>
                        <th>Execution Time</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for result in self.results:
            html += f"""
                    <tr>
                        <td>{result.rule_name}</td>
                        <td class="{result.status}">{result.status.upper()}</td>
                        <td>{result.message}</td>
                        <td>{result.execution_time:.2f}s</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self) -> str:
        """Generate Markdown report"""
        summary = self._generate_summary()
        
        markdown = f"""# Infrastructure Validation Report

## Summary

- **Health Score:** {summary['health_score']}%
- **Total Checks:** {summary['total_checks']}
- **Passed:** {summary['passed']}
- **Failed:** {summary['failed']}
- **Warnings:** {summary['warnings']}
- **Errors:** {summary['errors']}

## Results

| Rule | Status | Message | Execution Time |
|------|--------|---------|----------------|
"""
        
        for result in self.results:
            status_emoji = {'pass': '✅', 'fail': '❌', 'warning': '⚠️', 'error': '🔥'}[result.status]
            markdown += f"| {result.rule_name} | {status_emoji} {result.status.upper()} | {result.message} | {result.execution_time:.2f}s |\n"
        
        return markdown

async def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ainflue Infrastructure Validator')
    parser.add_argument('--config', help='Configuration file path', default='infrastructure_validation.yaml')
    parser.add_argument('--categories', nargs='+', help='Categories to validate', 
                       choices=['security', 'performance', 'availability', 'compliance'])
    parser.add_argument('--severity', nargs='+', help='Severity levels to include',
                       choices=['critical', 'high', 'medium', 'low'])
    parser.add_argument('--format', help='Report format', choices=['json', 'html', 'markdown'], default='json')
    parser.add_argument('--output', help='Output file path')
    parser.add_argument('--timeout', type=int, help='Global timeout for validations', default=300)
    
    args = parser.parse_args()
    
    validator = InfrastructureValidator(args.config)
    
    try:
        # Run validation
        results = await validator.validate_infrastructure(
            categories=args.categories,
            severity_filter=args.severity
        )
        
        # Generate report
        report = validator.generate_report(args.format)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report written to {args.output}")
        else:
            print(report)
        
        # Exit with appropriate code based on results
        summary = results['validation_summary']
        if summary['failed'] > 0 or summary['errors'] > 0:
            sys.exit(1)
        elif summary['warnings'] > 0:
            sys.exit(2)
        else:
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())