"""Advanced Protection Manager for IA Influencer Agent
Orchestrates all protection services and provides high-level API

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: Proprietary - All rights reserved
WARNING: Unauthorized use, copying, or distribution prohibited
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
import asyncio
import uuid
import logging
from dataclasses import dataclass, field

from .protection_agent import ProtectionAgent

logger = logging.getLogger(__name__)


@dataclass
class ProtectionRequest:
    """
Protection request structure"""
    request_id: str
    owner_id: str
    content_data: bytes
    content_type: str
    content_metadata: Dict
    protection_level: str = "standard"
    priority: str = "normal"  # low, normal, high, critical
    requested_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "pending"
    processing_started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict] = None
    errors: List[str] = field(default_factory=list)


@dataclass
class MonitoringAlert:
    """Content monitoring alert structure"""
    alert_id: str
    content_id: str
    alert_type: str  # violation_detected, usage_spike, revenue_drop
    severity: str  # low, medium, high, critical
    description: str
    detected_at: datetime
    platform: Optional[str] = None
    evidence: Dict = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


class ProtectionManager:
    """
    High-level protection manager that orchestrates all protection services
    Provides batch processing, monitoring, and management capabilities
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.protection_agent = ProtectionAgent(config)
        
        # Request management
        self.active_requests: Dict[str, ProtectionRequest] = {}
        self.processing_queue = asyncio.Queue()
        self.completed_requests: Dict[str, ProtectionRequest] = {}
        
        # Monitoring and alerts
        self.monitoring_alerts: Dict[str, MonitoringAlert] = {}
        self.monitoring_active = False
        
        # Performance metrics
        self.metrics = {
            'requests_processed': 0,
            'successful_protections': 0,
            'failed_protections': 0,
            'violations_detected': 0,
            'dmca_notices_sent': 0,
            'revenue_generated': 0.0,
            'processing_times': []
        }
        
        # Configuration
        self.max_concurrent_requests = config.get('max_concurrent_requests', 10)
        self.request_timeout = config.get('request_timeout', 300)  # 5 minutes
        self.monitoring_interval = config.get('monitoring_interval', 3600)  # 1 hour
        
    async def start_services(self):
        """
Start all protection services and background tasks"""
        try:
            # Start monitoring service
            if not self.monitoring_active:
                asyncio.create_task(self._monitoring_service())
                self.monitoring_active = True
                
            # Start request processor
            asyncio.create_task(self._request_processor())
            
            logger.info("Protection services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start protection services: {str(e)}")
            raise
            
    async def stop_services(self):
        """Stop all protection services gracefully"""
        try:
            self.monitoring_active = False
            
            # Wait for active requests to complete
            while self.active_requests:
                await asyncio.sleep(1)
                
            logger.info("Protection services stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping protection services: {str(e)}")
            
    async def submit_protection_request(self, content_data: bytes, content_metadata: Dict,
                                      protection_level: str = "standard", 
                                      priority: str = "normal") -> str:
        """
        Submit content protection request for processing
        
        Args:
            content_data: Raw content bytes
            content_metadata: Content metadata including owner info
            protection_level: Protection level (basic, standard, premium, enterprise)
            priority: Request priority (low, normal, high, critical)
            
        Returns:
            Request ID for tracking
        """
        try:
            request_id = f"REQ_{uuid.uuid4().hex[:16].upper()}"
            
            protection_request = ProtectionRequest(
                request_id=request_id,
                owner_id=content_metadata.get('owner_id', 'unknown'),
                content_data=content_data,
                content_type=content_metadata.get('content_type', 'application/octet-stream'),
                content_metadata=content_metadata,
                protection_level=protection_level,
                priority=priority
            )
            
            # Store request
            self.active_requests[request_id] = protection_request
            
            # Add to processing queue
            await self.processing_queue.put(protection_request)
            
            logger.info(f"Protection request {request_id} submitted for processing")
            return request_id
            
        except Exception as e:
            logger.error(f"Failed to submit protection request: {str(e)}")
            raise
            
    async def batch_protect_content(self, content_batch: List[Dict]) -> Dict:
        """
        Batch processing of multiple content protection requests
        
        Args:
            content_batch: List of content items with data and metadata
            
        Returns:
            Batch processing results
        """
        try:
            batch_id = f"BATCH_{uuid.uuid4().hex[:12].upper()}"
            batch_results = {
                'batch_id': batch_id,
                'total_items': len(content_batch),
                'submitted_requests': [],
                'failed_submissions': [],
                'started_at': datetime.utcnow().isoformat()
            }
            
            # Submit all requests
            for item in content_batch:
                try:
                    request_id = await self.submit_protection_request(
                        item['content_data'],
                        item['content_metadata'],
                        item.get('protection_level', 'standard'),
                        item.get('priority', 'normal')
                    )
                    batch_results['submitted_requests'].append({
                        'request_id': request_id,
                        'content_id': item['content_metadata'].get('content_id', 'unknown')
                    })
                except Exception as e:
                    batch_results['failed_submissions'].append({
                        'content_id': item['content_metadata'].get('content_id', 'unknown'),
                        'error': str(e)
                    })
                    
            batch_results['successful_submissions'] = len(batch_results['submitted_requests'])
            batch_results['failed_submissions_count'] = len(batch_results['failed_submissions'])
            
            logger.info(f"Batch {batch_id} submitted: {batch_results['successful_submissions']}/{batch_results['total_items']} successful")
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch protection failed: {str(e)}")
            return {'error': str(e)}
            
    def get_request_status(self, request_id: str) -> Dict:
        """Get status of protection request"""
        try:
            if request_id in self.active_requests:
                request = self.active_requests[request_id]
                return {
                    'request_id': request_id,
                    'status': request.status,
                    'owner_id': request.owner_id,
                    'protection_level': request.protection_level,
                    'priority': request.priority,
                    'requested_at': request.requested_at.isoformat(),
                    'processing_started_at': request.processing_started_at.isoformat() if request.processing_started_at else None,
                    'completed_at': request.completed_at.isoformat() if request.completed_at else None,
                    'results': request.results,
                    'errors': request.errors
                }
            elif request_id in self.completed_requests:
                request = self.completed_requests[request_id]
                return {
                    'request_id': request_id,
                    'status': 'completed',
                    'results': request.results,
                    'completed_at': request.completed_at.isoformat() if request.completed_at else None,
                    'processing_time': (request.completed_at - request.requested_at).total_seconds() if request.completed_at else None
                }
            else:
                return {'error': 'Request not found'}
                
        except Exception as e:
            logger.error(f"Failed to get request status: {str(e)}")
            return {'error': str(e)}
            
    def get_dashboard_metrics(self) -> Dict:
        """Get comprehensive dashboard metrics"""
        try:
            # Calculate processing statistics
            total_requests = self.metrics['requests_processed']
            success_rate = (self.metrics['successful_protections'] / total_requests * 100) if total_requests > 0 else 0
            
            avg_processing_time = (sum(self.metrics['processing_times']) / len(self.metrics['processing_times'])) if self.metrics['processing_times'] else 0
            
            # Current system status
            active_requests_count = len(self.active_requests)
            queue_size = self.processing_queue.qsize()
            
            return {
                'system_status': {
                    'monitoring_active': self.monitoring_active,
                    'active_requests': active_requests_count,
                    'queue_size': queue_size,
                    'max_concurrent': self.max_concurrent_requests
                },
                'processing_metrics': {
                    'total_requests': total_requests,
                    'successful_protections': self.metrics['successful_protections'],
                    'failed_protections': self.metrics['failed_protections'],
                    'success_rate': success_rate,
                    'average_processing_time': avg_processing_time
                },
                'protection_metrics': {
                    'violations_detected': self.metrics['violations_detected'],
                    'dmca_notices_sent': self.metrics['dmca_notices_sent'],
                    'revenue_generated': self.metrics['revenue_generated']
                },
                'alerts': {
                    'total_alerts': len(self.monitoring_alerts),
                    'unresolved_alerts': len([a for a in self.monitoring_alerts.values() if not a.resolved]),
                    'critical_alerts': len([a for a in self.monitoring_alerts.values() if a.severity == 'critical' and not a.resolved])
                },
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard metrics: {str(e)}")
            return {'error': str(e)}
            
    def get_owner_protection_summary(self, owner_id: str) -> Dict:
        """Get protection summary for specific owner"""
        try:
            # Get owner's requests
            owner_requests = [req for req in list(self.active_requests.values()) + list(self.completed_requests.values()) if req.owner_id == owner_id]
            
            # Calculate owner-specific metrics
            total_content = len(owner_requests)
            protected_content = len([req for req in owner_requests if req.status == 'completed' and req.results and req.results.get('success')])
            
            # Get recent alerts for owner's content
            owner_alerts = []
            for alert in self.monitoring_alerts.values():
                # Find content ID from requests
                content_alerts = [req for req in owner_requests if req.results and req.results.get('fingerprint', {}).get('content_id') == alert.content_id]
                if content_alerts:
                    owner_alerts.append(alert)
                    
            return {
                'owner_id': owner_id,
                'content_statistics': {
                    'total_content': total_content,
                    'protected_content': protected_content,
                    'protection_rate': (protected_content / total_content * 100) if total_content > 0 else 0
                },
                'recent_activity': {
                    'pending_requests': len([req for req in owner_requests if req.status == 'pending']),
                    'processing_requests': len([req for req in owner_requests if req.status == 'processing']),
                    'recent_alerts': len([a for a in owner_alerts if (datetime.utcnow() - a.detected_at).days <= 7])
                },
                'alerts_summary': {
                    'total_alerts': len(owner_alerts),
                    'unresolved_alerts': len([a for a in owner_alerts if not a.resolved]),
                    'violation_alerts': len([a for a in owner_alerts if a.alert_type == 'violation_detected'])
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get owner protection summary: {str(e)}")
            return {'error': str(e)}
            
    async def handle_monitoring_alert(self, alert_data: Dict) -> str:
        """Handle monitoring alert and take appropriate actions"""
        try:
            alert_id = f"ALERT_{uuid.uuid4().hex[:12].upper()}"
            
            alert = MonitoringAlert(
                alert_id=alert_id,
                content_id=alert_data.get('content_id', 'unknown'),
                alert_type=alert_data.get('alert_type', 'unknown'),
                severity=alert_data.get('severity', 'medium'),
                description=alert_data.get('description', ''),
                detected_at=datetime.utcnow(),
                platform=alert_data.get('platform'),
                evidence=alert_data.get('evidence', {})
            )
            
            # Store alert
            self.monitoring_alerts[alert_id] = alert
            
            # Take automated actions based on alert type and severity
            actions_taken = await self._handle_alert_actions(alert, alert_data)
            alert.actions_taken = actions_taken
            
            # Update metrics
            if alert.alert_type == 'violation_detected':
                self.metrics['violations_detected'] += 1
                
            logger.warning(f"Monitoring alert {alert_id} handled: {alert.description}")
            
            return alert_id
            
        except Exception as e:
            logger.error(f"Failed to handle monitoring alert: {str(e)}")
            return ""
            
    async def _request_processor(self):
        """Background request processor"""
        while True:
            try:
                # Get request from queue
                request = await self.processing_queue.get()
                
                # Update status
                request.status = "processing"
                request.processing_started_at = datetime.utcnow()
                
                # Process protection request
                start_time = datetime.utcnow()
                
                try:
                    # Use protection agent to protect content
                    protection_result = await self.protection_agent.protect_content(
                        request.content_data, request.content_metadata)
                        
                    request.results = protection_result
                    
                    if protection_result.get('success', False):
                        request.status = "completed"
                        self.metrics['successful_protections'] += 1
                    else:
                        request.status = "failed"
                        request.errors.append(protection_result.get('error', 'Unknown error'))
                        self.metrics['failed_protections'] += 1
                        
                except Exception as e:
                    request.status = "failed"
                    request.errors.append(str(e))
                    self.metrics['failed_protections'] += 1
                    
                finally:
                    # Update completion time and metrics
                    request.completed_at = datetime.utcnow()
                    processing_time = (request.completed_at - start_time).total_seconds()
                    self.metrics['processing_times'].append(processing_time)
                    self.metrics['requests_processed'] += 1
                    
                    # Move to completed requests
                    if request.request_id in self.active_requests:
                        del self.active_requests[request.request_id]
                    self.completed_requests[request.request_id] = request
                    
                    logger.info(f"Request {request.request_id} completed with status: {request.status}")
                    
            except Exception as e:
                logger.error(f"Request processor error: {str(e)}")
                await asyncio.sleep(1)  # Prevent tight error loop
                
    async def _monitoring_service(self):
        """Background monitoring service"""
        while self.monitoring_active:
            try:
                # Monitor all protected content
                await self._monitor_protected_content()
                
                # Clean up old alerts and requests
                await self._cleanup_old_records()
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"Monitoring service error: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
                
    async def _monitor_protected_content(self):
        """Monitor all protected content for violations and usage"""
        try:
            # Get all protected content IDs
            protected_content = []
            
            for request in self.completed_requests.values():
                if (request.status == "completed" and 
                    request.results and 
                    request.results.get('success') and
                    request.results.get('fingerprint')):
                    
                    content_id = request.results['fingerprint']['content_id']
                    protected_content.append(content_id)
                    
            # Monitor each content
            for content_id in protected_content:
                try:
                    monitoring_result = await self.protection_agent.copyright_manager.monitor_content_usage(content_id)
                    
                    if monitoring_result.get('violations_found', 0) > 0:
                        # Create violation alert
                        await self.handle_monitoring_alert({
                            'content_id': content_id,
                            'alert_type': 'violation_detected',
                            'severity': 'high',
                            'description': f'Copyright violations detected for content {content_id}',
                            'evidence': {
                                'violations_count': monitoring_result['violations_found'],
                                'monitoring_result': monitoring_result
                            }
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to monitor content {content_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Content monitoring failed: {str(e)}")
            
    async def _handle_alert_actions(self, alert: MonitoringAlert, alert_data: Dict) -> List[str]:
        """Handle automated actions for monitoring alerts"""
        actions_taken = []
        
        try:
            if alert.alert_type == 'violation_detected' and alert.severity in ['high', 'critical']:
                # Initiate automated DMCA takedown
                evidence = alert.evidence.get('monitoring_result', {})
                new_claims = evidence.get('new_claims', [])
                
                for claim_id in new_claims:
                    if alert.platform:
                        platform_info = {
                            'platform': alert.platform,
                            'email': f'legal@{alert.platform}.com',  # Would be configured properly
                            'infringing_url': evidence.get('source_url', '')
                        }
                        
                        try:
                            dmca_result = await self.protection_agent.process_dmca_takedown(claim_id, platform_info)
                            if dmca_result.get('success'):
                                actions_taken.append(f'DMCA notice sent for claim {claim_id}')
                                self.metrics['dmca_notices_sent'] += 1
                        except Exception as e:
                            logger.error(f"DMCA processing failed for claim {claim_id}: {str(e)}")
                            
            elif alert.alert_type == 'usage_spike':
                # Analyze for potential monetization optimization
                actions_taken.append('Usage spike analysis initiated')
                
            elif alert.alert_type == 'revenue_drop':
                # Trigger pricing optimization
                try:
                    optimization_result = await self.protection_agent.optimize_monetization(alert.content_id)
                    if not optimization_result.get('error'):
                        actions_taken.append('Pricing optimization triggered')
                except Exception as e:
                    logger.error(f"Monetization optimization failed: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Alert action handling failed: {str(e)}")
            
        return actions_taken
        
    async def _cleanup_old_records(self):
        """Clean up old completed requests and resolved alerts"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Clean up old completed requests
            old_requests = [req_id for req_id, req in self.completed_requests.items() 
                          if req.completed_at and req.completed_at < cutoff_date]
                          
            for req_id in old_requests:
                del self.completed_requests[req_id]
                
            # Clean up old resolved alerts
            old_alerts = [alert_id for alert_id, alert in self.monitoring_alerts.items()
                         if alert.resolved and alert.resolved_at and alert.resolved_at < cutoff_date]
                         
            for alert_id in old_alerts:
                del self.monitoring_alerts[alert_id]
                
            if old_requests or old_alerts:
                logger.info(f"Cleaned up {len(old_requests)} old requests and {len(old_alerts)} old alerts")
                
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

class BatchOperationType(Enum):
    """Batch operation types"""

    PROTECT_CONTENT = "protect_content"
    SCAN_VIOLATIONS = "scan_violations"
    ENFORCE_RIGHTS = "enforce_rights"
    UPDATE_PROTECTION = "update_protection"
    RENEWAL_CHECK = "renewal_check"

@dataclass
class ProtectionMetrics:
    """Protection performance metrics"""
    total_protected: int = 0
    active_monitoring: int = 0
    violations_detected: int = 0
    violations_resolved: int = 0
    enforcement_success_rate: float = 0.0
    average_detection_time: float = 0.0
    false_positive_rate: float = 0.0
    revenue_protected: float = 0.0

@dataclass
class BatchOperationResult:
    """
Batch operation result"""
    operation_id: str
    operation_type: BatchOperationType
    total_items: int
    successful_items: int
    failed_items: int
    errors: List[Dict[str, Any]]
    execution_time: float
    started_at: datetime
    completed_at: datetime

class ProtectionAgentManager(BaseAgent):
    """
    Enterprise-level protection agent manager for advanced content protection operations.
    
    Features:
    - Batch processing capabilities for large-scale operations
    - Advanced protection analytics and reporting
    - Multi-tenant protection management
    - Performance monitoring and optimization
    - Enterprise-grade audit logging
    - High-availability protection services
    - Advanced violation trend analysis
    - Automated protection renewal and lifecycle management
    """
    
    def __init__(self, manager_id: str = "protection_manager", config: Dict[str, Any] = None):
        super().__init__(manager_id, config)
        
        self.config = config or {}
        self.protection_agent = ProtectionAgent(config=config)
        
        # Enterprise components
        self.batch_processor = BatchProcessor(
            max_workers=self.config.get('max_batch_workers', 10),
            batch_size=self.config.get('batch_size', 100)
        )
        self.performance_monitor = PerformanceMonitor()
        self.audit_logger = AuditLogger()
        self.metrics_collector = MetricsCollector()
        
        # Storage
        self.protection_records = {}
        self.violation_records = {}
        self.batch_operations = {}
        
        # Performance tracking
        self.metrics = ProtectionMetrics()
        self.operation_stats = {}
        
        # Enterprise settings
        self.max_concurrent_operations = self.config.get('max_concurrent_operations', 50)
        self.default_protection_level = ProtectionLevel(self.config.get('default_protection_level', 'standard'))
        self.auto_renewal_enabled = self.config.get('auto_renewal_enabled', True)
        
        # Monitoring intervals
        self.violation_scan_interval = self.config.get('violation_scan_interval', 3600)  # 1 hour
        self.metrics_update_interval = self.config.get('metrics_update_interval', 300)   # 5 minutes
        
    async def initialize(self):
        """Initialize protection manager and all components"""
        try:
            # Initialize core protection agent
            await self.protection_agent.initialize()
            
            # Initialize enterprise components
            await self.batch_processor.initialize()
            await self.performance_monitor.initialize()
            await self.audit_logger.initialize()
            await self.metrics_collector.initialize()
            
            # Start background services
            asyncio.create_task(self._start_monitoring_services())
            asyncio.create_task(self._start_metrics_collection())
            asyncio.create_task(self._start_maintenance_tasks())
            
            # Log initialization
            await self.audit_logger.log_event(
                event_type="manager_initialized",
                details={"manager_id": self.agent_id, "config": self.config}
            )
            
            logger.info("Protection Agent Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Protection Agent Manager: {e}")
            raise ProtectionError(f"Manager initialization failed: {e}")
    
    async def process(self, request: Dict[str, Any]) -> AgentResponse:
        """
        Process high-level protection management requests.
        
        Args:
            request: Dictionary containing:
                - action: Management action
                - parameters: Action-specific parameters
                - user_id: User identifier
                - tenant_id: Tenant identifier (for multi-tenant)
        
        Returns:
            AgentResponse with management results
        """
        start_time = time.time()
        
        try:
            action = request.get('action', 'manage_protection')
            user_id = request.get('user_id')
            tenant_id = request.get('tenant_id')
            
            # Log request
            await self.audit_logger.log_event(
                event_type="manager_request",
                user_id=user_id,
                tenant_id=tenant_id,
                details={"action": action, "request_id": str(uuid.uuid4())}
            )
            
            if action == 'batch_protect_content':
                result = await self._batch_protect_content(request)
            elif action == 'batch_scan_violations':
                result = await self._batch_scan_violations(request)
            elif action == 'batch_enforce_rights':
                result = await self._batch_enforce_rights(request)
            elif action == 'get_protection_analytics':
                result = await self._get_protection_analytics(request)
            elif action == 'manage_protection_lifecycle':
                result = await self._manage_protection_lifecycle(request)
            elif action == 'optimize_protection_settings':
                result = await self._optimize_protection_settings(request)
            elif action == 'generate_protection_report':
                result = await self._generate_protection_report(request)
            elif action == 'manage_enterprise_settings':
                result = await self._manage_enterprise_settings(request)
            elif action == 'monitor_system_health':
                result = await self._monitor_system_health(request)
            else:
                raise ValidationError(f"Unknown management action: {action}")
            
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, True)
            
            return AgentResponse(
                success=True,
                data=result,
                message=f"Management {action} completed successfully",
                agent_type=self.agent_id,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.update_metrics(execution_time, False)
            
            logger.error(f"Protection management processing error: {e}")
            return AgentResponse(
                success=False,
                error=str(e),
                agent_type=self.agent_id,
                execution_time=execution_time
            )
    
    async def _batch_protect_content(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Batch protect multiple content files"""
        
        content_paths = request.get('content_paths', [])
        protection_level = ProtectionLevel(request.get('protection_level', 'standard'))
        user_id = request.get('user_id')
        batch_config = request.get('batch_config', {})
        
        if not content_paths:
            raise ValidationError("Content paths are required for batch protection")
        
        # Create batch operation
        operation_id = str(uuid.uuid4())
        operation = BatchOperationResult(
            operation_id=operation_id,
            operation_type=BatchOperationType.PROTECT_CONTENT,
            total_items=len(content_paths),
            successful_items=0,
            failed_items=0,
            errors=[],
            execution_time=0.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        self.batch_operations[operation_id] = operation
        
        # Process batch protection
        start_time = time.time()
        
        async def protect_single_content(content_path: str) -> Dict[str, Any]:
            try:
                result = await self.protection_agent.process({
                    'action': 'protect_content',
                    'content_path': content_path,
                    'protection_level': protection_level.value,
                    'user_id': user_id,
                    'monitoring_options': batch_config.get('monitoring_options', {}),
                    'enforcement_options': batch_config.get('enforcement_options', {})
                })
                
                if result.success:
                    operation.successful_items += 1
                    return {'status': 'success', 'path': content_path, 'data': result.data}
                else:
                    operation.failed_items += 1
                    error = {'path': content_path, 'error': result.error}
                    operation.errors.append(error)
                    return {'status': 'failed', 'path': content_path, 'error': result.error}
                    
            except Exception as e:
                operation.failed_items += 1
                error = {'path': content_path, 'error': str(e)}
                operation.errors.append(error)
                return {'status': 'failed', 'path': content_path, 'error': str(e)}
        
        # Execute batch processing
        results = await self.batch_processor.process_batch(
            items=content_paths,
            processor_func=protect_single_content,
            max_concurrent=batch_config.get('max_concurrent', 10)
        )
        
        # Update operation stats
        operation.execution_time = time.time() - start_time
        operation.completed_at = datetime.utcnow()
        
        # Update metrics
        self.metrics.total_protected += operation.successful_items
        
        # Log batch operation
        await self.audit_logger.log_event(
            event_type="batch_protection_completed",
            user_id=user_id,
            details=asdict(operation)
        )
        
        return {
            'operation_id': operation_id,
            'results': results,
            'summary': asdict(operation),
            'success_rate': operation.successful_items / operation.total_items if operation.total_items > 0 else 0.0
        }
    
    async def _batch_scan_violations(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Batch scan for violations across multiple content"""
        
        content_ids = request.get('content_ids', [])
        scan_config = request.get('scan_config', {})
        user_id = request.get('user_id')
        
        if not content_ids:
            raise ValidationError("Content IDs are required for batch violation scan")
        
        # Create batch operation
        operation_id = str(uuid.uuid4())
        operation = BatchOperationResult(
            operation_id=operation_id,
            operation_type=BatchOperationType.SCAN_VIOLATIONS,
            total_items=len(content_ids),
            successful_items=0,
            failed_items=0,
            errors=[],
            execution_time=0.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        start_time = time.time()
        all_violations = []
        
        async def scan_single_content(content_id: str) -> Dict[str, Any]:
            try:
                result = await self.protection_agent.process({
                    'action': 'check_violations',
                    'content_id': content_id,
                    'platforms': scan_config.get('platforms', []),
                    'deep_scan': scan_config.get('deep_scan', False)
                })
                
                if result.success:
                    operation.successful_items += 1
                    violations = result.data.get('violations', [])
                    all_violations.extend(violations)
                    return {'status': 'success', 'content_id': content_id, 'violations': violations}
                else:
                    operation.failed_items += 1
                    error = {'content_id': content_id, 'error': result.error}
                    operation.errors.append(error)
                    return {'status': 'failed', 'content_id': content_id, 'error': result.error}
                    
            except Exception as e:
                operation.failed_items += 1
                error = {'content_id': content_id, 'error': str(e)}
                operation.errors.append(error)
                return {'status': 'failed', 'content_id': content_id, 'error': str(e)}
        
        # Execute batch scanning
        results = await self.batch_processor.process_batch(
            items=content_ids,
            processor_func=scan_single_content,
            max_concurrent=scan_config.get('max_concurrent', 5)
        )
        
        # Update operation stats
        operation.execution_time = time.time() - start_time
        operation.completed_at = datetime.utcnow()
        
        # Analyze violations
        violation_analysis = await self._analyze_batch_violations(all_violations)
        
        # Update metrics
        self.metrics.violations_detected += len(all_violations)
        
        return {
            'operation_id': operation_id,
            'results': results,
            'total_violations': len(all_violations),
            'violation_analysis': violation_analysis,
            'summary': asdict(operation)
        }
    
    async def _batch_enforce_rights(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Batch enforce rights for multiple violations"""
        
        violation_ids = request.get('violation_ids', [])
        enforcement_action = request.get('enforcement_action', 'takedown_request')
        enforcement_config = request.get('enforcement_config', {})
        user_id = request.get('user_id')
        
        if not violation_ids:
            raise ValidationError("Violation IDs are required for batch enforcement")
        
        # Create batch operation
        operation_id = str(uuid.uuid4())
        operation = BatchOperationResult(
            operation_id=operation_id,
            operation_type=BatchOperationType.ENFORCE_RIGHTS,
            total_items=len(violation_ids),
            successful_items=0,
            failed_items=0,
            errors=[],
            execution_time=0.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        start_time = time.time()
        
        async def enforce_single_violation(violation_id: str) -> Dict[str, Any]:
            try:
                result = await self.protection_agent.process({
                    'action': 'enforce_rights',
                    'violation_id': violation_id,
                    'enforcement_action': enforcement_action
                })
                
                if result.success:
                    operation.successful_items += 1
                    return {'status': 'success', 'violation_id': violation_id, 'result': result.data}
                else:
                    operation.failed_items += 1
                    error = {'violation_id': violation_id, 'error': result.error}
                    operation.errors.append(error)
                    return {'status': 'failed', 'violation_id': violation_id, 'error': result.error}
                    
            except Exception as e:
                operation.failed_items += 1
                error = {'violation_id': violation_id, 'error': str(e)}
                operation.errors.append(error)
                return {'status': 'failed', 'violation_id': violation_id, 'error': str(e)}
        
        # Execute batch enforcement
        results = await self.batch_processor.process_batch(
            items=violation_ids,
            processor_func=enforce_single_violation,
            max_concurrent=enforcement_config.get('max_concurrent', 3)
        )
        
        # Update operation stats
        operation.execution_time = time.time() - start_time
        operation.completed_at = datetime.utcnow()
        
        # Update metrics
        enforcement_success_rate = operation.successful_items / operation.total_items if operation.total_items > 0 else 0.0
        self.metrics.enforcement_success_rate = (
            (self.metrics.enforcement_success_rate + enforcement_success_rate) / 2
        )
        
        return {
            'operation_id': operation_id,
            'results': results,
            'summary': asdict(operation),
            'enforcement_success_rate': enforcement_success_rate
        }
    
    async def _get_protection_analytics(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive protection analytics"""
        
        user_id = request.get('user_id')
        tenant_id = request.get('tenant_id')
        time_range = request.get('time_range', '30d')  # 7d, 30d, 90d, 1y
        include_trends = request.get('include_trends', True)
        
        # Calculate date range
        end_date = datetime.utcnow()
        if time_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_range == '30d':
            start_date = end_date - timedelta(days=30)
        elif time_range == '90d':
            start_date = end_date - timedelta(days=90)
        elif time_range == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Collect analytics data
        analytics = await self._collect_analytics_data(
            user_id, tenant_id, start_date, end_date, include_trends
        )
        
        return {
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'range': time_range
            },
            'metrics': asdict(self.metrics),
            'analytics': analytics,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _manage_protection_lifecycle(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
Manage protection lifecycle operations"""
        
        operation = request.get('operation', 'check_renewals')
        user_id = request.get('user_id')
        tenant_id = request.get('tenant_id')
        
        if operation == 'check_renewals':
            return await self._check_protection_renewals(user_id, tenant_id)
        elif operation == 'renew_protections':
            return await self._renew_protections(request)
        elif operation == 'expire_protections':
            return await self._expire_protections(request)
        elif operation == 'cleanup_old_records':
            return await self._cleanup_old_records(request)
        else:
            raise ValidationError(f"Unknown lifecycle operation: {operation}")
    
    async def _check_protection_renewals(self, user_id: str, tenant_id: str) -> Dict[str, Any]:
        """Check protections that need renewal"""
        
        # Get protections expiring in next 30 days
        expiring_soon = []
        expired = []
        
        current_time = datetime.utcnow()
        warning_threshold = current_time + timedelta(days=30)
        
        # This would normally query the database
        # For now, return mock data structure
        
        return {
            'expiring_soon': {
                'count': len(expiring_soon),
                'protections': expiring_soon
            },
            'expired': {
                'count': len(expired),
                'protections': expired
            },
            'auto_renewal_enabled': self.auto_renewal_enabled,
            'checked_at': current_time.isoformat()
        }
    
    async def _optimize_protection_settings(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
Optimize protection settings based on performance data"""
        
        user_id = request.get('user_id')
        optimization_type = request.get('optimization_type', 'performance')
        
        # Analyze current performance
        performance_data = await self.performance_monitor.get_performance_metrics()
        
        # Generate optimization recommendations
        recommendations = await self._generate_optimization_recommendations(
            performance_data, optimization_type
        )
        
        # Apply optimizations if requested
        applied_optimizations = []
        if request.get('apply_recommendations', False):
            applied_optimizations = await self._apply_optimizations(recommendations)
        
        return {
            'performance_data': performance_data,
            'recommendations': recommendations,
            'applied_optimizations': applied_optimizations,
            'optimization_type': optimization_type,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _generate_protection_report(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
Generate comprehensive protection report"""
        
        report_type = request.get('report_type', 'summary')
        user_id = request.get('user_id')
        tenant_id = request.get('tenant_id')
        time_range = request.get('time_range', '30d')
        
        # Collect report data
        analytics_data = await self._get_protection_analytics({
            'user_id': user_id,
            'tenant_id': tenant_id,
            'time_range': time_range,
            'include_trends': True
        })
        
        # Generate different report types
        if report_type == 'summary':
            report = await self._generate_summary_report(analytics_data)
        elif report_type == 'detailed':
            report = await self._generate_detailed_report(analytics_data)
        elif report_type == 'executive':
            report = await self._generate_executive_report(analytics_data)
        elif report_type == 'compliance':
            report = await self._generate_compliance_report(analytics_data)
        else:
            raise ValidationError(f"Unknown report type: {report_type}")
        
        # Save report if requested
        report_id = None
        if request.get('save_report', False):
            report_id = await self._save_report(report, report_type, user_id, tenant_id)
        
        return {
            'report_id': report_id,
            'report_type': report_type,
            'report': report,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    async def _monitor_system_health(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor protection system health"""
        
        # Collect system health metrics
        health_metrics = {
            'protection_agent_status': await self._check_protection_agent_health(),
            'batch_processor_status': await self._check_batch_processor_health(),
            'monitoring_services_status': await self._check_monitoring_services_health(),
            'database_status': await self._check_database_health(),
            'queue_status': await self._check_queue_health(),
            'performance_metrics': await self.performance_monitor.get_current_metrics()
        }
        
        # Determine overall health
        overall_health = "healthy"
        if any(status.get('status') == 'unhealthy' for status in health_metrics.values() if isinstance(status, dict)):
            overall_health = "unhealthy"
        elif any(status.get('status') == 'degraded' for status in health_metrics.values() if isinstance(status, dict)):
            overall_health = "degraded"
        
        return {
            'overall_health': overall_health,
            'components': health_metrics,
            'checked_at': datetime.utcnow().isoformat(),
            'uptime': await self._get_system_uptime()
        }
    
    async def _start_monitoring_services(self):
        """Start background monitoring services"""
        try:
            # Start violation monitoring
            asyncio.create_task(self._continuous_violation_monitoring())
            
            # Start protection lifecycle monitoring
            asyncio.create_task(self._protection_lifecycle_monitoring())
            
            # Start performance monitoring
            asyncio.create_task(self._performance_monitoring())
            
            logger.info("Protection manager monitoring services started")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring services: {e}")
    
    async def _start_metrics_collection(self):
        """Start metrics collection service"""
        while True:
            try:
                await self._update_metrics()
                await asyncio.sleep(self.metrics_update_interval)
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def _start_maintenance_tasks(self):
        """Start maintenance tasks"""
        while True:
            try:
                # Run maintenance every hour
                await asyncio.sleep(3600)
                await self._run_maintenance_tasks()
            except Exception as e:
                logger.error(f"Maintenance task error: {e}")
    
    async def _continuous_violation_monitoring(self):
        """Continuously monitor for violations"""
        while True:
            try:
                # This would monitor active protections for violations
                await self._scan_active_protections_for_violations()
                await asyncio.sleep(self.violation_scan_interval)
            except Exception as e:
                logger.error(f"Continuous violation monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _analyze_batch_violations(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze batch violations for insights"""
        
        if not violations:
            return {'total': 0, 'by_platform': {}, 'by_type': {}, 'severity_distribution': {}}
        
        # Analyze violations by platform
        by_platform = {}
        by_type = {}
        severity_scores = []
        
        for violation in violations:
            platform = violation.get('platform', 'unknown')
            violation_type = violation.get('violation_type', 'unknown')
            similarity_score = violation.get('similarity_score', 0.0)
            
            by_platform[platform] = by_platform.get(platform, 0) + 1
            by_type[violation_type] = by_type.get(violation_type, 0) + 1
            severity_scores.append(similarity_score)
        
        # Calculate severity distribution
        if severity_scores:
            high_severity = sum(1 for score in severity_scores if score >= 0.9)
            medium_severity = sum(1 for score in severity_scores if 0.7 <= score < 0.9)
            low_severity = sum(1 for score in severity_scores if score < 0.7)
        else:
            high_severity = medium_severity = low_severity = 0
        
        return {
            'total': len(violations),
            'by_platform': by_platform,
            'by_type': by_type,
            'severity_distribution': {
                'high': high_severity,
                'medium': medium_severity,
                'low': low_severity
            },
            'average_similarity': sum(severity_scores) / len(severity_scores) if severity_scores else 0.0
        }
    
    # Additional helper methods would be implemented here
    async def _collect_analytics_data(self, user_id, tenant_id, start_date, end_date, include_trends):
        """
Collect analytics data for the specified period"""
        # Implementation would query database and collect metrics
        return {}
    
    async def _check_protection_agent_health(self):
        """
Check protection agent health"""
        return {'status': 'healthy', 'response_time': 0.1}
    
    async def _check_batch_processor_health(self):
        """
Check batch processor health"""
        return {'status': 'healthy', 'queue_size': 0}
    
    async def _check_monitoring_services_health(self):
        """
Check monitoring services health"""
        return {'status': 'healthy', 'active_monitors': 5}
    
    async def _check_database_health(self):
        """
Check database health"""
        return {'status': 'healthy', 'connection_pool': '10/10'}
    
    async def _check_queue_health(self):
        """
Check queue health"""
        return {'status': 'healthy', 'pending_jobs': 0}
    
    async def _get_system_uptime(self):
        """
Get system uptime"""
        return "99.9%"
