"""
Timeout Management System - Enterprise Circuit Breakers
Advanced timeout patterns with adaptive timeouts and cascade prevention

This module implements comprehensive timeout management for microservices,
including adaptive timeout calculation, cascading timeout prevention,
and SLA compliance monitoring.

Expert Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
            Microservices + Audio + DevOps + IA Prompt Engineer

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️ PROPRIÉTÉ INTELLECTUELLE - PROTECTION FORTE
Cette implémentation est la propriété exclusive de Fahed Mlaiel.
Toute reproduction ou utilisation non autorisée est strictement interdite.
"""

import asyncio
import logging
import time
import uuid
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from collections import defaultdict, deque
import weakref


logger = logging.getLogger(__name__)


class TimeoutType(Enum):
    """Types of timeout management"""
    FIXED = "fixed"
    ADAPTIVE = "adaptive"
    PERCENTILE = "percentile"
    PREDICTIVE = "predictive"
    CONTEXTUAL = "contextual"


class TimeoutEvent(Enum):
    """Timeout event types"""
    TIMEOUT_TRIGGERED = "timeout_triggered"
    TIMEOUT_PREVENTED = "timeout_prevented"
    TIMEOUT_EXTENDED = "timeout_extended"
    TIMEOUT_SHORTENED = "timeout_shortened"
    CASCADE_DETECTED = "cascade_detected"
    CASCADE_PREVENTED = "cascade_prevented"


class ServiceProfile(Enum):
    """Service performance profiles"""
    FAST = "fast"          # < 100ms typical
    NORMAL = "normal"      # 100ms - 1s typical  
    SLOW = "slow"          # 1s - 5s typical
    BATCH = "batch"        # > 5s typical
    VARIABLE = "variable"   # Highly variable response times


@dataclass
class TimeoutConfig:
    """Timeout configuration parameters"""
    service_name: str
    timeout_type: TimeoutType = TimeoutType.ADAPTIVE
    base_timeout: float = 5.0
    min_timeout: float = 0.1
    max_timeout: float = 60.0
    percentile: float = 95.0
    adaptation_factor: float = 1.2
    history_window: int = 100
    cascade_detection: bool = True
    sla_target: Optional[float] = None
    service_profile: ServiceProfile = ServiceProfile.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TimeoutMetrics:
    """Timeout performance metrics"""
    total_requests: int = 0
    timeout_count: int = 0
    timeout_rate: float = 0.0
    avg_response_time: float = 0.0
    median_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    current_timeout: float = 0.0
    sla_compliance: float = 100.0
    cascade_preventions: int = 0
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class TimeoutEvent:
    """Timeout event data"""
    event_id: str
    event_type: TimeoutEvent
    service_name: str
    timeout_value: float
    response_time: Optional[float]
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    cascade_info: Optional[Dict[str, Any]] = None


@dataclass
class ResponseTimeData:
    """Response time measurement data"""
    timestamp: datetime
    response_time: float
    timeout_used: float
    success: bool
    service_name: str
    context: Dict[str, Any] = field(default_factory=dict)


class TimeoutCalculator:
    """Advanced timeout calculation engine"""
    
    def __init__(self, config: TimeoutConfig):
        self.config = config
        self.response_history: deque = deque(maxlen=config.history_window)
        self.timeout_history: List[float] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
    def add_response_time(self, response_time: float, success: bool):
        """Add response time measurement"""
        data = ResponseTimeData(
            timestamp=datetime.now(),
            response_time=response_time,
            timeout_used=self.config.base_timeout,
            success=success,
            service_name=self.config.service_name
        )
        
        self.response_history.append(data)
        
        # Update timeout if adaptive
        if self.config.timeout_type == TimeoutType.ADAPTIVE:
            self._update_adaptive_timeout()
    
    def calculate_timeout(self, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate optimal timeout value"""
        if self.config.timeout_type == TimeoutType.FIXED:
            return self.config.base_timeout
        elif self.config.timeout_type == TimeoutType.ADAPTIVE:
            return self._calculate_adaptive_timeout()
        elif self.config.timeout_type == TimeoutType.PERCENTILE:
            return self._calculate_percentile_timeout()
        elif self.config.timeout_type == TimeoutType.PREDICTIVE:
            return self._calculate_predictive_timeout(context)
        elif self.config.timeout_type == TimeoutType.CONTEXTUAL:
            return self._calculate_contextual_timeout(context)
        else:
            return self.config.base_timeout
    
    def _calculate_adaptive_timeout(self) -> float:
        """Calculate adaptive timeout based on recent performance"""
        if len(self.response_history) < 10:
            return self.config.base_timeout
        
        recent_times = [data.response_time for data in self.response_history 
                       if data.success]
        
        if not recent_times:
            return self.config.base_timeout
        
        # Use exponential moving average
        alpha = 0.1  # Smoothing factor
        ema = recent_times[0]
        for time_val in recent_times[1:]:
            ema = alpha * time_val + (1 - alpha) * ema
        
        # Apply adaptation factor
        adaptive_timeout = ema * self.config.adaptation_factor
        
        # Clamp to min/max bounds
        return max(
            self.config.min_timeout,
            min(adaptive_timeout, self.config.max_timeout)
        )
    
    def _calculate_percentile_timeout(self) -> float:
        """Calculate timeout based on percentile of response times"""
        if len(self.response_history) < 20:
            return self.config.base_timeout
        
        response_times = [data.response_time for data in self.response_history 
                         if data.success]
        
        if not response_times:
            return self.config.base_timeout
        
        percentile_value = np.percentile(response_times, self.config.percentile)
        
        return max(
            self.config.min_timeout,
            min(percentile_value, self.config.max_timeout)
        )
    
    def _calculate_predictive_timeout(self, context: Optional[Dict[str, Any]]) -> float:
        """Calculate predictive timeout using trend analysis"""
        if len(self.response_history) < 30:
            return self._calculate_adaptive_timeout()
        
        # Simple trend analysis - can be enhanced with ML models
        recent_times = [data.response_time for data in self.response_history[-20:] 
                       if data.success]
        older_times = [data.response_time for data in self.response_history[-40:-20] 
                      if data.success]
        
        if not recent_times or not older_times:
            return self._calculate_adaptive_timeout()
        
        recent_avg = statistics.mean(recent_times)
        older_avg = statistics.mean(older_times)
        
        # Trend factor
        trend_factor = recent_avg / older_avg if older_avg > 0 else 1.0
        
        # Base calculation
        base_timeout = self._calculate_adaptive_timeout()
        
        # Apply trend adjustment
        predictive_timeout = base_timeout * trend_factor
        
        return max(
            self.config.min_timeout,
            min(predictive_timeout, self.config.max_timeout)
        )
    
    def _calculate_contextual_timeout(self, context: Optional[Dict[str, Any]]) -> float:
        """Calculate timeout based on request context"""
        base_timeout = self._calculate_adaptive_timeout()
        
        if not context:
            return base_timeout
        
        # Context-based adjustments
        multiplier = 1.0
        
        # Request size adjustment
        if 'payload_size' in context:
            size_mb = context['payload_size'] / (1024 * 1024)
            if size_mb > 10:
                multiplier *= 1.5
            elif size_mb > 1:
                multiplier *= 1.2
        
        # Complexity adjustment
        if 'complexity' in context:
            complexity = context['complexity'].lower()
            if complexity == 'high':
                multiplier *= 2.0
            elif complexity == 'medium':
                multiplier *= 1.5
        
        # Priority adjustment
        if 'priority' in context:
            priority = context['priority'].lower()
            if priority == 'low':
                multiplier *= 0.8
            elif priority == 'high':
                multiplier *= 1.3
        
        contextual_timeout = base_timeout * multiplier
        
        return max(
            self.config.min_timeout,
            min(contextual_timeout, self.config.max_timeout)
        )
    
    def _update_adaptive_timeout(self):
        """Update adaptive timeout configuration"""
        new_timeout = self._calculate_adaptive_timeout()
        self.config.base_timeout = new_timeout
        self.timeout_history.append(new_timeout)
        
        # Keep history bounded
        if len(self.timeout_history) > 100:
            self.timeout_history = self.timeout_history[-100:]


class CascadeDetector:
    """Cascade timeout detection and prevention"""
    
    def __init__(self):
        self.service_chains: Dict[str, List[str]] = {}
        self.timeout_events: deque = deque(maxlen=1000)
        self.cascade_patterns: Dict[str, int] = defaultdict(int)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_service_chain(self, chain_id: str, services: List[str]):
        """Register service dependency chain"""
        self.service_chains[chain_id] = services
        self.logger.info(f"🔗 Registered service chain {chain_id}: {' -> '.join(services)}")
    
    def detect_cascade_risk(self, timeout_event: TimeoutEvent) -> Dict[str, Any]:
        """Detect potential cascade timeout risk"""
        self.timeout_events.append(timeout_event)
        
        # Find service chains containing this service
        affected_chains = []
        for chain_id, services in self.service_chains.items():
            if timeout_event.service_name in services:
                affected_chains.append((chain_id, services))
        
        if not affected_chains:
            return {'cascade_risk': 'low', 'affected_chains': []}
        
        # Analyze recent timeout patterns
        recent_timeouts = [event for event in self.timeout_events 
                          if (datetime.now() - event.timestamp).seconds < 300]  # Last 5 minutes
        
        cascade_risk = 'low'
        risk_factors = []
        
        # Check for timeout clustering
        timeout_count = len(recent_timeouts)
        if timeout_count > 10:
            cascade_risk = 'high'
            risk_factors.append('high_timeout_frequency')
        elif timeout_count > 5:
            cascade_risk = 'medium'
            risk_factors.append('elevated_timeout_frequency')
        
        # Check for chain propagation
        for chain_id, services in affected_chains:
            chain_timeouts = [event for event in recent_timeouts 
                            if event.service_name in services]
            
            if len(chain_timeouts) > len(services) * 0.5:
                cascade_risk = 'high'
                risk_factors.append(f'chain_propagation_{chain_id}')
        
        return {
            'cascade_risk': cascade_risk,
            'risk_factors': risk_factors,
            'affected_chains': affected_chains,
            'recent_timeouts': timeout_count,
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def prevent_cascade(self, risk_analysis: Dict[str, Any]) -> List[str]:
        """Generate cascade prevention actions"""
        actions = []
        
        if risk_analysis['cascade_risk'] == 'high':
            actions.extend([
                'circuit_breaker_activation',
                'emergency_timeout_extension',
                'load_balancer_adjustment',
                'fallback_service_activation'
            ])
        elif risk_analysis['cascade_risk'] == 'medium':
            actions.extend([
                'timeout_extension',
                'request_queuing',
                'health_check_increase'
            ])
        
        # Chain-specific actions
        for chain_id, services in risk_analysis['affected_chains']:
            actions.append(f'isolate_chain_{chain_id}')
        
        return actions


class SLAMonitor:
    """SLA compliance monitoring and alerting"""
    
    def __init__(self):
        self.sla_configs: Dict[str, Dict[str, Any]] = {}
        self.compliance_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def register_sla(self, service_name: str, sla_config: Dict[str, Any]):
        """Register SLA configuration for service"""
        self.sla_configs[service_name] = sla_config
        self.logger.info(f"📋 Registered SLA for {service_name}: {sla_config}")
    
    def record_response(self, service_name: str, response_time: float, success: bool):
        """Record response for SLA monitoring"""
        if service_name not in self.sla_configs:
            return
        
        sla_config = self.sla_configs[service_name]
        target_time = sla_config.get('target_response_time', 1.0)
        
        # Check SLA compliance
        compliant = success and response_time <= target_time
        
        compliance_record = {
            'timestamp': datetime.now(),
            'response_time': response_time,
            'success': success,
            'compliant': compliant,
            'target_time': target_time
        }
        
        self.compliance_history[service_name].append(compliance_record)
        
        # Calculate current compliance rate
        recent_records = list(self.compliance_history[service_name])[-100:]  # Last 100 requests
        compliance_rate = sum(1 for record in recent_records if record['compliant']) / len(recent_records)
        
        # Check for SLA violations
        min_compliance = sla_config.get('min_compliance_rate', 0.95)
        if compliance_rate < min_compliance:
            self._trigger_sla_alert(service_name, compliance_rate, min_compliance)
    
    def _trigger_sla_alert(self, service_name: str, current_rate: float, target_rate: float):
        """Trigger SLA violation alert"""
        alert = {
            'alert_id': str(uuid.uuid4()),
            'service_name': service_name,
            'alert_type': 'sla_violation',
            'current_compliance_rate': current_rate,
            'target_compliance_rate': target_rate,
            'severity': 'high' if current_rate < target_rate * 0.8 else 'medium',
            'timestamp': datetime.now(),
            'actions_recommended': [
                'increase_timeout_values',
                'scale_service_instances',
                'enable_circuit_breaker',
                'investigate_performance_degradation'
            ]
        }
        
        self.alerts.append(alert)
        self.logger.warning(f"🚨 SLA violation alert for {service_name}: {current_rate:.2%} compliance")
    
    def get_compliance_report(self, service_name: str) -> Dict[str, Any]:
        """Get SLA compliance report"""
        if service_name not in self.compliance_history:
            return {'error': f'No data for service {service_name}'}
        
        records = list(self.compliance_history[service_name])
        if not records:
            return {'error': f'No records for service {service_name}'}
        
        # Calculate metrics
        total_requests = len(records)
        successful_requests = sum(1 for record in records if record['success'])
        compliant_requests = sum(1 for record in records if record['compliant'])
        
        response_times = [record['response_time'] for record in records if record['success']]
        
        return {
            'service_name': service_name,
            'total_requests': total_requests,
            'success_rate': successful_requests / total_requests,
            'compliance_rate': compliant_requests / total_requests,
            'avg_response_time': statistics.mean(response_times) if response_times else 0,
            'median_response_time': statistics.median(response_times) if response_times else 0,
            'p95_response_time': np.percentile(response_times, 95) if response_times else 0,
            'p99_response_time': np.percentile(response_times, 99) if response_times else 0,
            'report_timestamp': datetime.now().isoformat()
        }


class TimeoutManagementSystem:
    """
    Enterprise timeout management system with adaptive patterns.
    Implements dynamic timeouts, cascade prevention, and SLA monitoring.
    """
    
    def __init__(self):
        """Initialize timeout management system"""
        self.timeout_calculators: Dict[str, TimeoutCalculator] = {}
        self.service_configs: Dict[str, TimeoutConfig] = {}
        self.cascade_detector = CascadeDetector()
        self.sla_monitor = SLAMonitor()
        self.active_timeouts: Dict[str, asyncio.Task] = {}
        self.metrics: Dict[str, TimeoutMetrics] = defaultdict(TimeoutMetrics)
        self.event_handlers: Dict[TimeoutEvent, List[Callable]] = defaultdict(list)
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        self.logger.info("⏱️ Timeout Management System initialized - Enterprise patterns ready")
    
    async def calculate_adaptive_timeouts(self, service_profile: Dict[str, Any]) -> Dict[str, float]:
        """Calculate adaptive timeouts based on service performance profiles"""
        try:
            service_name = service_profile.get('service_name')
            if not service_name:
                raise ValueError("Service name required in profile")
            
            # Get or create timeout calculator
            if service_name not in self.timeout_calculators:
                config = TimeoutConfig(
                    service_name=service_name,
                    timeout_type=TimeoutType[service_profile.get('timeout_type', 'ADAPTIVE')],
                    base_timeout=service_profile.get('base_timeout', 5.0),
                    min_timeout=service_profile.get('min_timeout', 0.1),
                    max_timeout=service_profile.get('max_timeout', 60.0),
                    service_profile=ServiceProfile[service_profile.get('profile', 'NORMAL')]
                )
                
                self.timeout_calculators[service_name] = TimeoutCalculator(config)
                self.service_configs[service_name] = config
            
            calculator = self.timeout_calculators[service_name]
            
            # Calculate timeouts for different scenarios
            timeout_scenarios = {
                'default': calculator.calculate_timeout(),
                'high_load': calculator.calculate_timeout({'complexity': 'high'}),
                'low_priority': calculator.calculate_timeout({'priority': 'low'}),
                'large_payload': calculator.calculate_timeout({'payload_size': 10 * 1024 * 1024}),
                'batch_operation': calculator.calculate_timeout({'complexity': 'high', 'priority': 'low'})
            }
            
            self.logger.info(f"📊 Calculated adaptive timeouts for {service_name}: {timeout_scenarios}")
            return timeout_scenarios
            
        except Exception as e:
            self.logger.error(f"❌ Failed to calculate adaptive timeouts: {e}")
            raise
    
    async def prevent_cascading_timeouts(self, timeout_event: TimeoutEvent) -> bool:
        """Prevent cascading timeouts in distributed system"""
        try:
            # Detect cascade risk
            risk_analysis = self.cascade_detector.detect_cascade_risk(timeout_event)
            
            if risk_analysis['cascade_risk'] == 'low':
                return True
            
            # Get prevention actions
            prevention_actions = self.cascade_detector.prevent_cascade(risk_analysis)
            
            # Execute prevention actions
            success = True
            for action in prevention_actions:
                try:
                    success &= await self._execute_prevention_action(action, timeout_event)
                except Exception as e:
                    self.logger.error(f"❌ Failed to execute prevention action {action}: {e}")
                    success = False
            
            # Log cascade prevention
            if success:
                self.logger.info(f"🛡️ Successfully prevented timeout cascade for {timeout_event.service_name}")
                
                # Update metrics
                if timeout_event.service_name in self.metrics:
                    self.metrics[timeout_event.service_name].cascade_preventions += 1
            else:
                self.logger.warning(f"⚠️ Partially prevented timeout cascade for {timeout_event.service_name}")
            
            # Trigger event handlers
            await self._trigger_event_handlers(TimeoutEvent.CASCADE_PREVENTED if success else TimeoutEvent.CASCADE_DETECTED, {
                'timeout_event': timeout_event,
                'risk_analysis': risk_analysis,
                'prevention_actions': prevention_actions,
                'success': success
            })
            
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Failed to prevent cascading timeouts: {e}")
            return False
    
    async def _execute_prevention_action(self, action: str, timeout_event: TimeoutEvent) -> bool:
        """Execute specific prevention action"""
        try:
            if action == 'circuit_breaker_activation':
                return await self._activate_circuit_breaker(timeout_event.service_name)
            elif action == 'emergency_timeout_extension':
                return await self._extend_timeout_emergency(timeout_event.service_name)
            elif action == 'load_balancer_adjustment':
                return await self._adjust_load_balancer(timeout_event.service_name)
            elif action == 'fallback_service_activation':
                return await self._activate_fallback_service(timeout_event.service_name)
            elif action == 'timeout_extension':
                return await self._extend_timeout_gradual(timeout_event.service_name)
            elif action == 'request_queuing':
                return await self._enable_request_queuing(timeout_event.service_name)
            elif action.startswith('isolate_chain_'):
                chain_id = action.replace('isolate_chain_', '')
                return await self._isolate_service_chain(chain_id)
            else:
                self.logger.warning(f"⚠️ Unknown prevention action: {action}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Error executing prevention action {action}: {e}")
            return False
    
    async def _activate_circuit_breaker(self, service_name: str) -> bool:
        """Activate circuit breaker for service"""
        self.logger.info(f"🔌 Activating circuit breaker for {service_name}")
        # Implementation would integrate with circuit breakers module
        return True
    
    async def _extend_timeout_emergency(self, service_name: str) -> bool:
        """Emergency timeout extension"""
        if service_name in self.service_configs:
            config = self.service_configs[service_name]
            config.base_timeout = min(config.base_timeout * 2, config.max_timeout)
            self.logger.info(f"⏰ Emergency timeout extension for {service_name}: {config.base_timeout}s")
            return True
        return False
    
    async def _adjust_load_balancer(self, service_name: str) -> bool:
        """Adjust load balancer settings"""
        self.logger.info(f"⚖️ Adjusting load balancer for {service_name}")
        # Implementation would integrate with load balancer
        return True
    
    async def _activate_fallback_service(self, service_name: str) -> bool:
        """Activate fallback service"""
        self.logger.info(f"🔄 Activating fallback service for {service_name}")
        # Implementation would integrate with fallback services
        return True
    
    async def _extend_timeout_gradual(self, service_name: str) -> bool:
        """Gradual timeout extension"""
        if service_name in self.service_configs:
            config = self.service_configs[service_name]
            config.base_timeout = min(config.base_timeout * 1.2, config.max_timeout)
            self.logger.info(f"⏱️ Gradual timeout extension for {service_name}: {config.base_timeout}s")
            return True
        return False
    
    async def _enable_request_queuing(self, service_name: str) -> bool:
        """Enable request queuing"""
        self.logger.info(f"📝 Enabling request queuing for {service_name}")
        # Implementation would integrate with queuing system
        return True
    
    async def _isolate_service_chain(self, chain_id: str) -> bool:
        """Isolate service chain"""
        self.logger.info(f"🔗 Isolating service chain {chain_id}")
        # Implementation would isolate entire service chain
        return True
    
    async def monitor_sla_compliance(self, sla_config: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor SLA compliance with timeout tracking"""
        try:
            service_name = sla_config.get('service_name')
            if not service_name:
                raise ValueError("Service name required in SLA config")
            
            # Register SLA if not already registered
            if service_name not in self.sla_monitor.sla_configs:
                self.sla_monitor.register_sla(service_name, sla_config)
            
            # Get compliance report
            compliance_report = self.sla_monitor.get_compliance_report(service_name)
            
            # Add timeout-specific metrics
            if service_name in self.metrics:
                timeout_metrics = self.metrics[service_name]
                compliance_report.update({
                    'timeout_rate': timeout_metrics.timeout_rate,
                    'current_timeout': timeout_metrics.current_timeout,
                    'cascade_preventions': timeout_metrics.cascade_preventions,
                    'timeout_adjustments': len(self.timeout_calculators[service_name].timeout_history) if service_name in self.timeout_calculators else 0
                })
            
            self.logger.info(f"📊 SLA compliance monitoring for {service_name}: {compliance_report.get('compliance_rate', 0):.2%}")
            return compliance_report
            
        except Exception as e:
            self.logger.error(f"❌ Failed to monitor SLA compliance: {e}")
            raise
    
    async def record_response_time(self, service_name: str, response_time: float, 
                                 success: bool, context: Optional[Dict[str, Any]] = None):
        """Record response time for timeout adaptation"""
        try:
            # Update timeout calculator
            if service_name in self.timeout_calculators:
                self.timeout_calculators[service_name].add_response_time(response_time, success)
            
            # Update SLA monitor
            self.sla_monitor.record_response(service_name, response_time, success)
            
            # Update metrics
            metrics = self.metrics[service_name]
            metrics.total_requests += 1
            
            if success:
                # Update response time statistics
                if metrics.total_requests == 1:
                    metrics.avg_response_time = response_time
                else:
                    # Exponential moving average
                    alpha = 0.1
                    metrics.avg_response_time = alpha * response_time + (1 - alpha) * metrics.avg_response_time
            else:
                metrics.timeout_count += 1
            
            metrics.timeout_rate = metrics.timeout_count / metrics.total_requests
            metrics.last_updated = datetime.now()
            
            # Check for timeout event
            if not success and response_time >= (self.service_configs.get(service_name, TimeoutConfig("")).base_timeout):
                timeout_event = TimeoutEvent(
                    event_id=str(uuid.uuid4()),
                    event_type=TimeoutEvent.TIMEOUT_TRIGGERED,
                    service_name=service_name,
                    timeout_value=self.service_configs.get(service_name, TimeoutConfig("")).base_timeout,
                    response_time=response_time,
                    timestamp=datetime.now(),
                    context=context or {}
                )
                
                # Attempt cascade prevention
                await self.prevent_cascading_timeouts(timeout_event)
            
            self.logger.debug(f"📊 Recorded response time for {service_name}: {response_time:.3f}s (success: {success})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to record response time: {e}")
    
    async def register_event_handler(self, event_type: TimeoutEvent, handler: Callable):
        """Register event handler for timeout events"""
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"📝 Registered event handler for {event_type.value}")
    
    async def _trigger_event_handlers(self, event_type: TimeoutEvent, event_data: Dict[str, Any]):
        """Trigger registered event handlers"""
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                self.logger.error(f"❌ Error in event handler for {event_type.value}: {e}")
    
    async def register_service_chain(self, chain_id: str, services: List[str]):
        """Register service dependency chain for cascade detection"""
        self.cascade_detector.register_service_chain(chain_id, services)
    
    async def get_timeout_analytics(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive timeout analytics"""
        try:
            if service_name:
                # Single service analytics
                if service_name not in self.metrics:
                    return {'error': f'No data for service {service_name}'}
                
                metrics = self.metrics[service_name]
                calculator = self.timeout_calculators.get(service_name)
                
                analytics = {
                    'service_name': service_name,
                    'metrics': {
                        'total_requests': metrics.total_requests,
                        'timeout_count': metrics.timeout_count,
                        'timeout_rate': metrics.timeout_rate,
                        'avg_response_time': metrics.avg_response_time,
                        'current_timeout': metrics.current_timeout,
                        'cascade_preventions': metrics.cascade_preventions
                    },
                    'timeout_history': calculator.timeout_history if calculator else [],
                    'response_history_size': len(calculator.response_history) if calculator else 0,
                    'last_updated': metrics.last_updated.isoformat()
                }
                
                # Add SLA compliance if available
                sla_report = self.sla_monitor.get_compliance_report(service_name)
                if 'error' not in sla_report:
                    analytics['sla_compliance'] = sla_report
                
                return analytics
            else:
                # System-wide analytics
                total_requests = sum(m.total_requests for m in self.metrics.values())
                total_timeouts = sum(m.timeout_count for m in self.metrics.values())
                total_preventions = sum(m.cascade_preventions for m in self.metrics.values())
                
                return {
                    'system_wide': {
                        'total_services': len(self.metrics),
                        'total_requests': total_requests,
                        'total_timeouts': total_timeouts,
                        'overall_timeout_rate': total_timeouts / max(total_requests, 1),
                        'total_cascade_preventions': total_preventions,
                        'active_calculators': len(self.timeout_calculators),
                        'service_chains': len(self.cascade_detector.service_chains)
                    },
                    'services': {name: {
                        'requests': metrics.total_requests,
                        'timeout_rate': metrics.timeout_rate,
                        'cascade_preventions': metrics.cascade_preventions
                    } for name, metrics in self.metrics.items()},
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Failed to get timeout analytics: {e}")
            raise
    
    async def optimize_timeouts(self, optimization_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Optimize timeout values across all services"""
        try:
            optimization_config = optimization_config or {}
            results = {}
            
            for service_name, calculator in self.timeout_calculators.items():
                try:
                    # Get current performance metrics
                    metrics = self.metrics[service_name]
                    
                    # Determine if optimization is needed
                    needs_optimization = (
                        metrics.timeout_rate > optimization_config.get('max_timeout_rate', 0.05) or
                        metrics.avg_response_time > calculator.config.base_timeout * 0.8
                    )
                    
                    if needs_optimization:
                        # Calculate optimized timeout
                        old_timeout = calculator.config.base_timeout
                        optimized_timeout = calculator.calculate_timeout()
                        
                        # Apply optimization if significantly different
                        if abs(optimized_timeout - old_timeout) / old_timeout > 0.1:  # 10% difference threshold
                            calculator.config.base_timeout = optimized_timeout
                            
                            results[service_name] = {
                                'optimized': True,
                                'old_timeout': old_timeout,
                                'new_timeout': optimized_timeout,
                                'improvement': (old_timeout - optimized_timeout) / old_timeout,
                                'reason': 'high_timeout_rate' if metrics.timeout_rate > 0.05 else 'response_time_optimization'
                            }
                        else:
                            results[service_name] = {
                                'optimized': False,
                                'current_timeout': old_timeout,
                                'reason': 'no_significant_improvement'
                            }
                    else:
                        results[service_name] = {
                            'optimized': False,
                            'current_timeout': calculator.config.base_timeout,
                            'reason': 'performance_acceptable'
                        }
                        
                except Exception as e:
                    results[service_name] = {
                        'optimized': False,
                        'error': str(e)
                    }
            
            self.logger.info(f"🔧 Timeout optimization completed for {len(results)} services")
            return {
                'optimization_results': results,
                'summary': {
                    'services_optimized': sum(1 for r in results.values() if r.get('optimized', False)),
                    'total_services': len(results),
                    'timestamp': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to optimize timeouts: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup timeout management system"""
        try:
            # Cancel active timeout tasks
            for task_id, task in self.active_timeouts.items():
                try:
                    task.cancel()
                    await task
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    self.logger.warning(f"⚠️ Error cancelling timeout task {task_id}: {e}")
            
            self.active_timeouts.clear()
            self.timeout_calculators.clear()
            self.service_configs.clear()
            self.metrics.clear()
            self.event_handlers.clear()
            
            self.logger.info("🧹 Timeout Management System cleaned up")
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup error: {e}")


# Global timeout management system instance
timeout_manager = TimeoutManagementSystem()


# Export main classes and functions
__all__ = [
    'TimeoutManagementSystem',
    'TimeoutConfig',
    'TimeoutType',
    'TimeoutEvent',
    'ServiceProfile',
    'TimeoutMetrics',
    'TimeoutCalculator',
    'CascadeDetector',
    'SLAMonitor',
    'ResponseTimeData',
    'timeout_manager'
]


if __name__ == "__main__":
    async def demo():
        """Demo timeout management system functionality"""
        manager = TimeoutManagementSystem()
        
        # Configure service profile
        service_profile = {
            'service_name': 'user-service',
            'timeout_type': 'ADAPTIVE',
            'base_timeout': 2.0,
            'min_timeout': 0.1,
            'max_timeout': 10.0,
            'profile': 'NORMAL'
        }
        
        # Calculate adaptive timeouts
        timeouts = await manager.calculate_adaptive_timeouts(service_profile)
        print(f"Calculated timeouts: {json.dumps(timeouts, indent=2)}")
        
        # Register service chain
        await manager.register_service_chain('user_workflow', ['user-service', 'auth-service', 'db-service'])
        
        # Simulate some response times
        for i in range(10):
            response_time = 0.5 + (i * 0.1)  # Gradually increasing response times
            success = response_time < 2.0
            await manager.record_response_time('user-service', response_time, success)
        
        # Get analytics
        analytics = await manager.get_timeout_analytics('user-service')
        print(f"Service analytics: {json.dumps(analytics, indent=2, default=str)}")
        
        # Optimize timeouts
        optimization = await manager.optimize_timeouts()
        print(f"Optimization results: {json.dumps(optimization, indent=2, default=str)}")
        
        # Cleanup
        await manager.cleanup()
    
    # Run demo
    asyncio.run(demo())