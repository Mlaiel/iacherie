#!/usr/bin/env python3
"""
🔗 Integration Service Template - iacherie Enterprise
==================================================
Template enterprise pour services intégration.
API connectors + ETL pipelines + data transformation + error handling.

Author: Fahed Mlaiel (mlaiel@live.de)
Project: iacherie Microservices Templates
Version: 1.0 Production
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - FAHED MLAIEL
Cette architecture microservices et tous ses templates sont la propriété intellectuelle 
EXCLUSIVE de Fahed Mlaiel (mlaiel@live.de). Toute reproduction, modification, 
distribution ou vol d'idée/concept/code sans autorisation écrite PERSONNELLE est 
STRICTEMENT INTERDITE et sera poursuivie en justice avec la PLEINE RIGUEUR de la loi.
"""

import asyncio
import logging
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
import json
import httpx
import uuid
from contextlib import asynccontextmanager

from .service_template import EnterpriseServiceBase, ServiceConfig

# Integration-specific configurations
@dataclass
class IntegrationConfig:
    """Configuration for integration connectors."""
    name: str
    endpoint_url: str
    auth_type: str = "bearer"  # bearer, basic, oauth2, api_key
    auth_credentials: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 1.0
    rate_limit: Optional[int] = None
    circuit_breaker: bool = True
    health_check_url: Optional[str] = None

@dataclass 
class ETLPipelineConfig:
    """Configuration for ETL pipelines."""
    name: str
    source_config: Dict[str, Any]
    destination_config: Dict[str, Any]
    transformation_rules: List[Dict[str, Any]] = field(default_factory=list)
    batch_size: int = 1000
    schedule: Optional[str] = None  # cron expression
    retry_policy: Dict[str, Any] = field(default_factory=dict)

class ConnectorStatus(Enum):
    """Status of integration connectors."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"
    MAINTENANCE = "maintenance"

class IntegrationServiceTemplate(EnterpriseServiceBase):
    """
    🔗 Template enterprise pour services intégration.
    
    Fonctionnalités:
    - API connectors avec retry logic et circuit breakers
    - ETL pipelines avec transformation données
    - Error handling enterprise avec dead letter queues
    - Integration monitoring avec health checks
    - Rate limiting et throttling intelligent
    - Data validation et schema evolution
    """
    
    def __init__(self, config: ServiceConfig):
        """Initialize integration service."""
        super().__init__(config)
        self.connectors: Dict[str, Any] = {}
        self.etl_pipelines: Dict[str, Any] = {}
        self.circuit_breakers: Dict[str, Any] = {}
        self.rate_limiters: Dict[str, Any] = {}
        self.http_client: Optional[httpx.AsyncClient] = None
        self.health_status: Dict[str, ConnectorStatus] = {}
        
        # Integration monitoring
        self.request_metrics: Dict[str, Dict[str, int]] = {}
        self.error_rates: Dict[str, float] = {}
        self.response_times: Dict[str, List[float]] = {}
        
        self.logger = logging.getLogger(f"{self.config.service_name}.integration")
        
    async def setup_http_client(self, client_config: Dict[str, Any]) -> None:
        """Setup HTTP client avec configuration enterprise."""
        try:
            timeout = httpx.Timeout(
                connect=client_config.get('connect_timeout', 10.0),
                read=client_config.get('read_timeout', 30.0),
                write=client_config.get('write_timeout', 10.0),
                pool=client_config.get('pool_timeout', 10.0)
            )
            
            limits = httpx.Limits(
                max_keepalive_connections=client_config.get('max_keepalive', 20),
                max_connections=client_config.get('max_connections', 100),
                keepalive_expiry=client_config.get('keepalive_expiry', 5.0)
            )
            
            self.http_client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                headers=client_config.get('default_headers', {}),
                verify=client_config.get('verify_ssl', True)
            )
            
            self.logger.info("HTTP client configured successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to setup HTTP client: {e}")
            raise
    
    async def setup_api_connectors(self, connector_configs: List[IntegrationConfig]) -> None:
        """Configuration connecteurs API externes avec retry logic."""
        try:
            for config in connector_configs:
                connector = {
                    'config': config,
                    'session': await self._create_authenticated_session(config),
                    'status': ConnectorStatus.HEALTHY,
                    'last_health_check': datetime.utcnow(),
                    'error_count': 0,
                    'request_count': 0
                }
                
                self.connectors[config.name] = connector
                
                # Setup circuit breaker
                if config.circuit_breaker:
                    await self._setup_circuit_breaker(config.name, config)
                
                # Setup rate limiter
                if config.rate_limit:
                    await self._setup_rate_limiter(config.name, config.rate_limit)
                
                self.logger.info(f"API connector '{config.name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup API connectors: {e}")
            raise
    
    async def setup_etl_pipelines(self, pipeline_configs: List[ETLPipelineConfig]) -> None:
        """Configuration pipelines ETL avec transformation données."""
        try:
            for config in pipeline_configs:
                pipeline = {
                    'config': config,
                    'status': 'ready',
                    'last_run': None,
                    'next_run': None,
                    'run_count': 0,
                    'error_count': 0,
                    'transformer': await self._create_data_transformer(config)
                }
                
                self.etl_pipelines[config.name] = pipeline
                
                # Schedule pipeline if configured
                if config.schedule:
                    await self._schedule_pipeline(config.name, config.schedule)
                
                self.logger.info(f"ETL pipeline '{config.name}' configured")
                
        except Exception as e:
            self.logger.error(f"Failed to setup ETL pipelines: {e}")
            raise
    
    async def setup_data_transformation(self, transform_configs: Dict[str, Any]) -> None:
        """Configuration transformation données avec validation schemas."""
        try:
            self.transformation_rules = transform_configs.get('rules', [])
            self.validation_schemas = transform_configs.get('schemas', {})
            self.error_handlers = transform_configs.get('error_handlers', {})
            
            # Setup schema registry connection if configured
            if 'schema_registry' in transform_configs:
                await self._setup_schema_registry(transform_configs['schema_registry'])
            
            self.logger.info("Data transformation configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup data transformation: {e}")
            raise
    
    async def setup_error_handling(self, error_configs: Dict[str, Any]) -> None:
        """Configuration gestion erreurs avec circuit breakers."""
        try:
            self.dead_letter_queue = await self._setup_dlq(error_configs.get('dlq_config', {}))
            self.error_notifications = error_configs.get('notifications', {})
            self.retry_policies = error_configs.get('retry_policies', {})
            
            # Setup error alerting
            if 'alerting' in error_configs:
                await self._setup_error_alerting(error_configs['alerting'])
            
            self.logger.info("Error handling configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup error handling: {e}")
            raise
    
    async def setup_integration_monitoring(self, monitoring_config: Dict[str, Any]) -> None:
        """Configuration monitoring intégrations avec health checks."""
        try:
            self.monitoring_config = monitoring_config
            self.health_check_interval = monitoring_config.get('health_check_interval', 60)
            self.metrics_collection = monitoring_config.get('collect_metrics', True)
            
            # Start health check background task
            if monitoring_config.get('enable_health_checks', True):
                asyncio.create_task(self._health_check_loop())
            
            # Start metrics collection
            if self.metrics_collection:
                asyncio.create_task(self._metrics_collection_loop())
            
            self.logger.info("Integration monitoring configured")
            
        except Exception as e:
            self.logger.error(f"Failed to setup integration monitoring: {e}")
            raise
    
    async def execute_api_call(self, connector_name: str, method: str, 
                              endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute API call avec retry logic et error handling."""
        try:
            connector = self.connectors.get(connector_name)
            if not connector:
                raise ValueError(f"Connector '{connector_name}' not found")
            
            # Check circuit breaker
            if await self._is_circuit_open(connector_name):
                raise Exception(f"Circuit breaker open for '{connector_name}'")
            
            # Apply rate limiting
            await self._apply_rate_limit(connector_name)
            
            start_time = datetime.utcnow()
            
            # Execute API call with retry logic
            response = await self._execute_with_retry(
                connector, method, endpoint, **kwargs
            )
            
            # Record metrics
            await self._record_api_metrics(connector_name, start_time, True)
            
            return response
            
        except Exception as e:
            await self._record_api_metrics(connector_name, start_time, False)
            await self._handle_api_error(connector_name, e)
            raise
    
    async def run_etl_pipeline(self, pipeline_name: str, 
                              data_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute ETL pipeline avec monitoring."""
        try:
            pipeline = self.etl_pipelines.get(pipeline_name)
            if not pipeline:
                raise ValueError(f"Pipeline '{pipeline_name}' not found")
            
            start_time = datetime.utcnow()
            pipeline['status'] = 'running'
            
            self.logger.info(f"Starting ETL pipeline '{pipeline_name}'")
            
            # Extract data
            source_data = await self._extract_data(pipeline, data_override)
            
            # Transform data
            transformed_data = await self._transform_data(pipeline, source_data)
            
            # Load data
            result = await self._load_data(pipeline, transformed_data)
            
            # Update pipeline status
            pipeline['status'] = 'completed'
            pipeline['last_run'] = start_time
            pipeline['run_count'] += 1
            
            self.logger.info(f"ETL pipeline '{pipeline_name}' completed successfully")
            
            return result
            
        except Exception as e:
            pipeline['status'] = 'failed'
            pipeline['error_count'] += 1
            
            self.logger.error(f"ETL pipeline '{pipeline_name}' failed: {e}")
            await self._handle_pipeline_error(pipeline_name, e)
            raise
    
    async def get_integration_health(self) -> Dict[str, Any]:
        """Get health status of all integrations."""
        health_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'overall_status': 'healthy',
            'connectors': {},
            'pipelines': {},
            'metrics': {}
        }
        
        # Check connector health
        unhealthy_connectors = 0
        for name, connector in self.connectors.items():
            status = await self._check_connector_health(name, connector)
            health_report['connectors'][name] = {
                'status': status.value,
                'last_check': connector.get('last_health_check', '').isoformat() if connector.get('last_health_check') else None,
                'error_rate': self.error_rates.get(name, 0.0),
                'request_count': connector.get('request_count', 0)
            }
            
            if status != ConnectorStatus.HEALTHY:
                unhealthy_connectors += 1
        
        # Check pipeline health
        failed_pipelines = 0
        for name, pipeline in self.etl_pipelines.items():
            pipeline_health = {
                'status': pipeline['status'],
                'last_run': pipeline['last_run'].isoformat() if pipeline['last_run'] else None,
                'run_count': pipeline['run_count'],
                'error_count': pipeline['error_count']
            }
            health_report['pipelines'][name] = pipeline_health
            
            if pipeline['status'] == 'failed':
                failed_pipelines += 1
        
        # Overall health assessment
        if unhealthy_connectors > 0 or failed_pipelines > 0:
            health_report['overall_status'] = 'degraded' if (unhealthy_connectors + failed_pipelines) <= 2 else 'unhealthy'
        
        # Add metrics
        health_report['metrics'] = {
            'total_connectors': len(self.connectors),
            'healthy_connectors': len(self.connectors) - unhealthy_connectors,
            'total_pipelines': len(self.etl_pipelines),
            'active_pipelines': sum(1 for p in self.etl_pipelines.values() if p['status'] in ['ready', 'running'])
        }
        
        return health_report
    
    # Private helper methods
    async def _create_authenticated_session(self, config: IntegrationConfig) -> httpx.AsyncClient:
        """Create authenticated HTTP session."""
        headers = {}
        
        if config.auth_type == "bearer":
            headers["Authorization"] = f"Bearer {config.auth_credentials.get('token')}"
        elif config.auth_type == "basic":
            # Basic auth will be handled by httpx.BasicAuth
            pass
        elif config.auth_type == "api_key":
            key_name = config.auth_credentials.get('key_name', 'X-API-Key')
            headers[key_name] = config.auth_credentials.get('api_key')
        
        auth = None
        if config.auth_type == "basic":
            auth = httpx.BasicAuth(
                config.auth_credentials.get('username'),
                config.auth_credentials.get('password')
            )
        
        return httpx.AsyncClient(
            headers=headers,
            auth=auth,
            timeout=config.timeout
        )
    
    async def _setup_circuit_breaker(self, name: str, config: IntegrationConfig) -> None:
        """Setup circuit breaker for connector."""
        self.circuit_breakers[name] = {
            'state': 'closed',  # closed, open, half_open
            'failure_count': 0,
            'failure_threshold': 5,
            'recovery_timeout': 60,
            'last_failure': None
        }
    
    async def _setup_rate_limiter(self, name: str, rate_limit: int) -> None:
        """Setup rate limiter for connector."""
        self.rate_limiters[name] = {
            'limit': rate_limit,
            'window': 60,  # 1 minute window
            'requests': [],
            'last_reset': datetime.utcnow()
        }
    
    async def _is_circuit_open(self, connector_name: str) -> bool:
        """Check if circuit breaker is open."""
        cb = self.circuit_breakers.get(connector_name)
        if not cb:
            return False
        
        if cb['state'] == 'open':
            if datetime.utcnow() - cb['last_failure'] > timedelta(seconds=cb['recovery_timeout']):
                cb['state'] = 'half_open'
                return False
            return True
        
        return False
    
    async def _apply_rate_limit(self, connector_name: str) -> None:
        """Apply rate limiting."""
        limiter = self.rate_limiters.get(connector_name)
        if not limiter:
            return
        
        now = datetime.utcnow()
        
        # Clean old requests outside window
        limiter['requests'] = [req_time for req_time in limiter['requests'] 
                              if now - req_time < timedelta(seconds=limiter['window'])]
        
        # Check if limit exceeded
        if len(limiter['requests']) >= limiter['limit']:
            raise Exception(f"Rate limit exceeded for '{connector_name}'")
        
        limiter['requests'].append(now)
    
    async def _execute_with_retry(self, connector: Dict[str, Any], 
                                 method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Execute API call with retry logic."""
        config = connector['config']
        session = connector['session']
        
        for attempt in range(config.max_retries + 1):
            try:
                response = await session.request(
                    method=method,
                    url=f"{config.endpoint_url.rstrip('/')}/{endpoint.lstrip('/')}",
                    **kwargs
                )
                response.raise_for_status()
                return response.json() if response.content else {}
                
            except Exception as e:
                if attempt == config.max_retries:
                    raise
                
                wait_time = config.retry_backoff * (2 ** attempt)
                await asyncio.sleep(wait_time)
    
    async def _record_api_metrics(self, connector_name: str, start_time: datetime, success: bool) -> None:
        """Record API call metrics."""
        if connector_name not in self.request_metrics:
            self.request_metrics[connector_name] = {'success': 0, 'failure': 0}
        
        response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        if connector_name not in self.response_times:
            self.response_times[connector_name] = []
        
        self.response_times[connector_name].append(response_time)
        
        # Keep only last 100 response times
        if len(self.response_times[connector_name]) > 100:
            self.response_times[connector_name] = self.response_times[connector_name][-100:]
        
        if success:
            self.request_metrics[connector_name]['success'] += 1
        else:
            self.request_metrics[connector_name]['failure'] += 1
        
        # Calculate error rate
        total = self.request_metrics[connector_name]['success'] + self.request_metrics[connector_name]['failure']
        self.error_rates[connector_name] = self.request_metrics[connector_name]['failure'] / total if total > 0 else 0.0
    
    async def _handle_api_error(self, connector_name: str, error: Exception) -> None:
        """Handle API errors and update circuit breaker."""
        connector = self.connectors.get(connector_name)
        if connector:
            connector['error_count'] += 1
        
        # Update circuit breaker
        cb = self.circuit_breakers.get(connector_name)
        if cb:
            cb['failure_count'] += 1
            cb['last_failure'] = datetime.utcnow()
            
            if cb['failure_count'] >= cb['failure_threshold']:
                cb['state'] = 'open'
                self.logger.warning(f"Circuit breaker opened for '{connector_name}'")
    
    async def _create_data_transformer(self, config: ETLPipelineConfig) -> Callable:
        """Create data transformer function."""
        def transformer(data: Any) -> Any:
            result = data
            for rule in config.transformation_rules:
                result = self._apply_transformation_rule(result, rule)
            return result
        
        return transformer
    
    def _apply_transformation_rule(self, data: Any, rule: Dict[str, Any]) -> Any:
        """Apply single transformation rule."""
        rule_type = rule.get('type')
        
        if rule_type == 'map_field':
            # Map field names
            if isinstance(data, dict):
                old_key = rule.get('from')
                new_key = rule.get('to')
                if old_key in data:
                    data[new_key] = data.pop(old_key)
        
        elif rule_type == 'filter':
            # Filter data based on conditions
            condition = rule.get('condition', {})
            if isinstance(data, list):
                data = [item for item in data if self._evaluate_condition(item, condition)]
        
        elif rule_type == 'aggregate':
            # Aggregate data
            if isinstance(data, list):
                group_by = rule.get('group_by')
                agg_func = rule.get('function', 'sum')
                # Implementation of aggregation logic
                pass
        
        return data
    
    def _evaluate_condition(self, item: Any, condition: Dict[str, Any]) -> bool:
        """Evaluate filter condition."""
        # Simple condition evaluation - can be extended
        field = condition.get('field')
        operator = condition.get('operator', 'eq')
        value = condition.get('value')
        
        if not isinstance(item, dict) or field not in item:
            return False
        
        item_value = item[field]
        
        if operator == 'eq':
            return item_value == value
        elif operator == 'ne':
            return item_value != value
        elif operator == 'gt':
            return item_value > value
        elif operator == 'lt':
            return item_value < value
        
        return True
    
    async def _extract_data(self, pipeline: Dict[str, Any], 
                           data_override: Optional[Dict[str, Any]]) -> Any:
        """Extract data from source."""
        if data_override:
            return data_override
        
        config = pipeline['config']
        source_config = config.source_config
        
        if source_config['type'] == 'api':
            connector_name = source_config['connector']
            endpoint = source_config['endpoint']
            return await self.execute_api_call(connector_name, 'GET', endpoint)
        
        elif source_config['type'] == 'database':
            # Database extraction logic
            pass
        
        elif source_config['type'] == 'file':
            # File extraction logic
            pass
        
        return {}
    
    async def _transform_data(self, pipeline: Dict[str, Any], data: Any) -> Any:
        """Transform extracted data."""
        transformer = pipeline['transformer']
        return transformer(data)
    
    async def _load_data(self, pipeline: Dict[str, Any], data: Any) -> Dict[str, Any]:
        """Load transformed data to destination."""
        config = pipeline['config']
        dest_config = config.destination_config
        
        if dest_config['type'] == 'api':
            connector_name = dest_config['connector']
            endpoint = dest_config['endpoint']
            return await self.execute_api_call(connector_name, 'POST', endpoint, json=data)
        
        elif dest_config['type'] == 'database':
            # Database loading logic
            pass
        
        elif dest_config['type'] == 'file':
            # File loading logic
            pass
        
        return {'status': 'loaded', 'records': len(data) if isinstance(data, list) else 1}
    
    async def _check_connector_health(self, name: str, connector: Dict[str, Any]) -> ConnectorStatus:
        """Check health of individual connector."""
        config = connector['config']
        
        try:
            if config.health_check_url:
                session = connector['session']
                response = await session.get(config.health_check_url, timeout=10)
                response.raise_for_status()
                
                connector['last_health_check'] = datetime.utcnow()
                connector['status'] = ConnectorStatus.HEALTHY
                return ConnectorStatus.HEALTHY
            
            # Check error rate
            error_rate = self.error_rates.get(name, 0.0)
            if error_rate > 0.5:  # 50% error rate threshold
                connector['status'] = ConnectorStatus.DEGRADED
                return ConnectorStatus.DEGRADED
            
            connector['status'] = ConnectorStatus.HEALTHY
            return ConnectorStatus.HEALTHY
            
        except Exception as e:
            self.logger.warning(f"Health check failed for '{name}': {e}")
            connector['status'] = ConnectorStatus.DOWN
            return ConnectorStatus.DOWN
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while True:
            try:
                for name, connector in self.connectors.items():
                    await self._check_connector_health(name, connector)
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop."""
        while True:
            try:
                # Collect and export metrics
                metrics = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'connectors': len(self.connectors),
                    'pipelines': len(self.etl_pipelines),
                    'request_metrics': self.request_metrics,
                    'error_rates': self.error_rates,
                    'response_times': {
                        name: {
                            'avg': sum(times) / len(times) if times else 0,
                            'p95': sorted(times)[int(len(times) * 0.95)] if times else 0
                        }
                        for name, times in self.response_times.items()
                    }
                }
                
                # Export metrics (implement based on monitoring system)
                self.logger.debug(f"Metrics collected: {json.dumps(metrics, default=str)}")
                
                await asyncio.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)
    
    @abstractmethod
    async def setup_service_specific_integrations(self) -> None:
        """Setup service-specific integrations. Override in subclasses."""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Service health check."""
        base_health = await super().health_check()
        integration_health = await self.get_integration_health()
        
        return {
            **base_health,
            'integrations': integration_health,
            'components': {
                'http_client': 'healthy' if self.http_client else 'not_configured',
                'connectors': f"{len(self.connectors)} configured",
                'pipelines': f"{len(self.etl_pipelines)} configured"
            }
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self.http_client:
            await self.http_client.aclose()
        
        for connector in self.connectors.values():
            if 'session' in connector:
                await connector['session'].aclose()
        
        await super().cleanup()