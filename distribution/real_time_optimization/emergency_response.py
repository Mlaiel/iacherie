"""Emergency Response System

Automated emergency response system for critical content performance situations,
crisis detection, and immediate corrective action deployment.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EmergencyType(Enum):
    """Types of emergency situations"""
    VIRAL_CRISIS = "viral_crisis"
    ENGAGEMENT_COLLAPSE = "engagement_collapse"
    NEGATIVE_SENTIMENT = "negative_sentiment"
    PLATFORM_VIOLATION = "platform_violation"
    SECURITY_BREACH = "security_breach"
    REPUTATION_DAMAGE = "reputation_damage"
    CONTENT_THEFT = "content_theft"
    API_FAILURE = "api_failure"


class EmergencySeverity(Enum):
    """Emergency severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    CATASTROPHIC = "catastrophic"


@dataclass
class ResponseProtocol:
    """Emergency response protocol configuration"""
    protocol_id: str
    emergency_type: EmergencyType
    severity_threshold: EmergencySeverity
    response_time_seconds: int
    automatic_actions: List[str]
    manual_approval_required: bool
    escalation_chain: List[str]
    cost_limit: float
    notification_channels: List[str]
    rollback_conditions: List[str]


@dataclass
class EmergencyAlert:
    """Emergency alert data structure"""
    alert_id: str
    emergency_type: EmergencyType
    severity: EmergencySeverity
    content_id: str
    platform: str
    detected_at: datetime
    description: str
    metrics: Dict[str, Any]
    trigger_conditions: List[str]
    recommended_actions: List[str]
    escalation_required: bool


@dataclass
class EmergencyResponse:
    """Emergency response execution record"""
    response_id: str
    alert_id: str
    protocol_used: str
    actions_taken: List[Dict[str, Any]]
    response_time: int
    cost_incurred: float
    effectiveness_score: float
    resolution_status: str
    created_at: datetime
    resolved_at: Optional[datetime]


class EmergencyResponseSystem:
    """Automated emergency response and crisis management system"""
    
    def __init__(self) -> None:
        """Initialize emergency response system"""
        self.active_emergencies = {}
        self.response_protocols = self._init_response_protocols()
        self.emergency_history = {}
        self.escalation_chains = self._init_escalation_chains()
        self.monitoring_active = False
        
    def _init_response_protocols(self) -> Dict[str, ResponseProtocol]:
        """Initialize emergency response protocols"""
        protocols = {}
        
        # Viral Crisis Protocol
        protocols['viral_crisis'] = ResponseProtocol(
            protocol_id='viral_crisis',
            emergency_type=EmergencyType.VIRAL_CRISIS,
            severity_threshold=EmergencySeverity.HIGH,
            response_time_seconds=60,
            automatic_actions=[
                'pause_automated_posting',
                'increase_monitoring_frequency',
                'activate_crisis_communication',
                'notify_legal_team'
            ],
            manual_approval_required=True,
            escalation_chain=['content_manager', 'legal_team', 'ceo'],
            cost_limit=10000.0,
            notification_channels=['email', 'sms', 'slack', 'phone'],
            rollback_conditions=['negative_sentiment_below_20']
        )
        
        # Engagement Collapse Protocol
        protocols['engagement_collapse'] = ResponseProtocol(
            protocol_id='engagement_collapse',
            emergency_type=EmergencyType.ENGAGEMENT_COLLAPSE,
            severity_threshold=EmergencySeverity.MEDIUM,
            response_time_seconds=300,
            automatic_actions=[
                'emergency_content_boost',
                'cross_platform_amplification',
                'influencer_outreach',
                'content_optimization'
            ],
            manual_approval_required=False,
            escalation_chain=['marketing_manager', 'content_director'],
            cost_limit=1000.0,
            notification_channels=['email', 'slack'],
            rollback_conditions=['engagement_rate_above_baseline']
        )
        
        # Negative Sentiment Protocol
        protocols['negative_sentiment'] = ResponseProtocol(
            protocol_id='negative_sentiment',
            emergency_type=EmergencyType.NEGATIVE_SENTIMENT,
            severity_threshold=EmergencySeverity.HIGH,
            response_time_seconds=120,
            automatic_actions=[
                'pause_content_distribution',
                'activate_sentiment_recovery',
                'engage_community_management',
                'prepare_public_response'
            ],
            manual_approval_required=True,
            escalation_chain=['pr_manager', 'cmo', 'ceo'],
            cost_limit=5000.0,
            notification_channels=['email', 'sms', 'slack'],
            rollback_conditions=['sentiment_score_above_60']
        )
        
        # Platform Violation Protocol
        protocols['platform_violation'] = ResponseProtocol(
            protocol_id='platform_violation',
            emergency_type=EmergencyType.PLATFORM_VIOLATION,
            severity_threshold=EmergencySeverity.CRITICAL,
            response_time_seconds=30,
            automatic_actions=[
                'immediate_content_removal',
                'backup_content_activation',
                'legal_compliance_check',
                'platform_appeal_preparation'
            ],
            manual_approval_required=False,
            escalation_chain=['compliance_officer', 'legal_team'],
            cost_limit=0.0,
            notification_channels=['email', 'sms', 'phone'],
            rollback_conditions=['platform_approval_received']
        )
        
        return protocols
    
    def _init_escalation_chains(self) -> Dict[str, Dict[str, Any]]:
        """Initialize escalation chains for different scenarios"""
        return {
            'content_manager': {
                'contact': 'content@ainflue.com',
                'phone': '+1-555-0101',
                'escalation_time': 15  # minutes
            },
            'marketing_manager': {
                'contact': 'marketing@ainflue.com',
                'phone': '+1-555-0102',
                'escalation_time': 30
            },
            'pr_manager': {
                'contact': 'pr@ainflue.com',
                'phone': '+1-555-0103',
                'escalation_time': 10
            },
            'legal_team': {
                'contact': 'legal@ainflue.com',
                'phone': '+1-555-0104',
                'escalation_time': 5
            },
            'cmo': {
                'contact': 'cmo@ainflue.com',
                'phone': '+1-555-0105',
                'escalation_time': 20
            },
            'ceo': {
                'contact': 'mlaiel@live.de',
                'phone': '+1-555-0106',
                'escalation_time': 60
            }
        }
    
    async def start_emergency_monitoring(self) -> bool:
        """Start emergency monitoring system"""
        try:
            logger.info("Starting emergency response monitoring")
            self.monitoring_active = True
            
            # Start monitoring task
            asyncio.create_task(self._emergency_monitoring_loop())
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting emergency monitoring: {str(e)}")
            return False
    
    async def detect_emergency(
        self,
        content_id: str,
        platform: str,
        performance_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[EmergencyAlert]:
        """Detect emergency situations from performance data"""
        try:
            # Analyze performance data for emergency conditions
            emergency_conditions = await self._analyze_emergency_conditions(
                performance_data, context
            )
            
            if not emergency_conditions:
                return None
            
            # Determine emergency type and severity
            emergency_type = await self._determine_emergency_type(emergency_conditions)
            severity = await self._calculate_emergency_severity(
                emergency_type, emergency_conditions, performance_data
            )
            
            # Create emergency alert
            alert = EmergencyAlert(
                alert_id=f"emergency_{content_id}_{int(datetime.utcnow().timestamp())}",
                emergency_type=emergency_type,
                severity=severity,
                content_id=content_id,
                platform=platform,
                detected_at=datetime.utcnow(),
                description=await self._generate_emergency_description(
                    emergency_type, emergency_conditions, performance_data
                ),
                metrics=performance_data,
                trigger_conditions=emergency_conditions,
                recommended_actions=await self._get_recommended_actions(emergency_type, severity),
                escalation_required=severity in [EmergencySeverity.HIGH, EmergencySeverity.CRITICAL, EmergencySeverity.CATASTROPHIC]
            )
            
            # Store active emergency
            self.active_emergencies[alert.alert_id] = alert
            
            logger.warning(f"Emergency detected: {alert.emergency_type.value} - {alert.severity.value}")
            
            return alert
            
        except Exception as e:
            logger.error(f"Error detecting emergency: {str(e)}")
            return None
    
    async def respond_to_emergency(self, alert: EmergencyAlert) -> EmergencyResponse:
        """Execute emergency response for detected emergency"""
        try:
            logger.critical(f"Executing emergency response for: {alert.alert_id}")
            
            response_start_time = datetime.utcnow()
            
            # Get appropriate response protocol
            protocol = self.response_protocols.get(alert.emergency_type.value)
            if not protocol:
                protocol = await self._create_default_protocol(alert.emergency_type)
            
            # Check if manual approval is required
            if protocol.manual_approval_required and alert.severity in [EmergencySeverity.HIGH, EmergencySeverity.CRITICAL]:
                approval_result = await self._request_manual_approval(alert, protocol)
                if not approval_result.get('approved', False):
                    logger.warning(f"Manual approval denied for emergency: {alert.alert_id}")
                    return await self._create_denied_response(alert, protocol)
            
            # Execute automatic actions
            executed_actions = await self._execute_automatic_actions(
                alert, protocol.automatic_actions
            )
            
            # Send notifications
            await self._send_emergency_notifications(alert, protocol)
            
            # Start escalation if required
            if alert.escalation_required:
                await self._start_escalation_process(alert, protocol)
            
            # Calculate response time
            response_time = int((datetime.utcnow() - response_start_time).total_seconds())
            
            # Calculate cost
            total_cost = sum(action.get('cost', 0.0) for action in executed_actions)
            
            # Create response record
            response = EmergencyResponse(
                response_id=f"response_{alert.alert_id}",
                alert_id=alert.alert_id,
                protocol_used=protocol.protocol_id,
                actions_taken=executed_actions,
                response_time=response_time,
                cost_incurred=total_cost,
                effectiveness_score=0.0,  # Will be calculated later
                resolution_status='in_progress',
                created_at=response_start_time,
                resolved_at=None
            )
            
            # Store response
            await self._store_emergency_response(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error executing emergency response: {str(e)}")
            raise
    
    async def monitor_emergency_resolution(self, alert_id: str) -> Dict[str, Any]:
        """Monitor emergency resolution progress"""
        try:
            if alert_id not in self.active_emergencies:
                return {'status': 'not_found'}
            
            alert = self.active_emergencies[alert_id]
            
            # Get current performance data
            current_performance = await self._get_current_performance(
                alert.content_id, alert.platform
            )
            
            # Check resolution conditions
            resolution_status = await self._check_resolution_conditions(
                alert, current_performance
            )
            
            if resolution_status['resolved']:
                # Mark emergency as resolved
                await self._resolve_emergency(alert_id, resolution_status)
                
                return {
                    'status': 'resolved',
                    'resolution_time': resolution_status.get('resolution_time'),
                    'final_metrics': current_performance,
                    'effectiveness_score': resolution_status.get('effectiveness_score', 0.0)
                }
            else:
                # Check if escalation is needed
                if resolution_status.get('needs_escalation'):
                    await self._escalate_emergency(alert_id)
                
                return {
                    'status': 'in_progress',
                    'current_metrics': current_performance,
                    'time_elapsed': (datetime.utcnow() - alert.detected_at).total_seconds(),
                    'next_action': resolution_status.get('next_action')
                }
            
        except Exception as e:
            logger.error(f"Error monitoring emergency resolution: {str(e)}")
            return {'status': 'error', 'error': str(e)}
    
    async def get_emergency_dashboard(self) -> Dict[str, Any]:
        """Get emergency response dashboard data"""
        try:
            active_count = len(self.active_emergencies)
            
            # Categorize active emergencies by severity
            severity_breakdown = {}
            type_breakdown = {}
            
            for alert in self.active_emergencies.values():
                severity = alert.severity.value
                emergency_type = alert.emergency_type.value
                
                severity_breakdown[severity] = severity_breakdown.get(severity, 0) + 1
                type_breakdown[emergency_type] = type_breakdown.get(emergency_type, 0) + 1
            
            # Get recent emergency statistics
            recent_emergencies = await self._get_recent_emergency_stats()
            
            # Calculate system health metrics
            system_health = await self._calculate_system_health()
            
            return {
                'timestamp': datetime.utcnow(),
                'active_emergencies': active_count,
                'severity_breakdown': severity_breakdown,
                'type_breakdown': type_breakdown,
                'recent_stats': recent_emergencies,
                'system_health': system_health,
                'monitoring_status': 'active' if self.monitoring_active else 'inactive',
                'response_protocols': len(self.response_protocols)
            }
            
        except Exception as e:
            logger.error(f"Error getting emergency dashboard: {str(e)}")
            return {}
    
    # Private helper methods
    async def _emergency_monitoring_loop(self) -> None:
        """Main emergency monitoring loop"""
        while self.monitoring_active:
            try:
                # Check all active emergencies for resolution
                for alert_id in list(self.active_emergencies.keys()):
                    await self.monitor_emergency_resolution(alert_id)
                
                # Check for new emergency conditions
                await self._scan_for_new_emergencies()
                
                # Wait before next check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in emergency monitoring loop: {str(e)}")
                await asyncio.sleep(60)
    
    async def _analyze_emergency_conditions(
        self, 
        performance_data: Dict[str, Any], 
        context: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Analyze performance data for emergency conditions"""
        conditions = []
        
        # Check engagement collapse
        engagement_rate = performance_data.get('engagement_rate', 0)
        if engagement_rate < 0.005:  # Less than 0.5%
            conditions.append('critical_low_engagement')
        
        # Check sentiment crisis
        sentiment_score = performance_data.get('sentiment_score', 0.5)
        if sentiment_score < 0.2:  # Very negative sentiment
            conditions.append('negative_sentiment_crisis')
        
        # Check velocity drop
        velocity = performance_data.get('velocity', 0)
        if velocity < 0.1:  # Very low content velocity
            conditions.append('velocity_collapse')
        
        # Check for viral crisis indicators
        viral_potential = performance_data.get('viral_potential', 0)
        negative_mentions = performance_data.get('negative_mentions', 0)
        if viral_potential > 0.8 and negative_mentions > 100:
            conditions.append('viral_crisis')
        
        # Check for platform violations
        if context and context.get('platform_warnings', 0) > 0:
            conditions.append('platform_violation_risk')
        
        return conditions
    
    async def _determine_emergency_type(self, conditions: List[str]) -> EmergencyType:
        """Determine emergency type from conditions"""
        if 'viral_crisis' in conditions:
            return EmergencyType.VIRAL_CRISIS
        elif 'negative_sentiment_crisis' in conditions:
            return EmergencyType.NEGATIVE_SENTIMENT
        elif 'critical_low_engagement' in conditions or 'velocity_collapse' in conditions:
            return EmergencyType.ENGAGEMENT_COLLAPSE
        elif 'platform_violation_risk' in conditions:
            return EmergencyType.PLATFORM_VIOLATION
        else:
            return EmergencyType.ENGAGEMENT_COLLAPSE  # Default
    
    async def _calculate_emergency_severity(
        self, 
        emergency_type: EmergencyType, 
        conditions: List[str], 
        performance_data: Dict[str, Any]
    ) -> EmergencySeverity:
        """Calculate emergency severity"""
        severity_score = 0
        
        # Base severity by type
        type_severity = {
            EmergencyType.VIRAL_CRISIS: 4,
            EmergencyType.PLATFORM_VIOLATION: 4,
            EmergencyType.NEGATIVE_SENTIMENT: 3,
            EmergencyType.ENGAGEMENT_COLLAPSE: 2,
            EmergencyType.SECURITY_BREACH: 5,
            EmergencyType.REPUTATION_DAMAGE: 3
        }
        
        severity_score = type_severity.get(emergency_type, 1)
        
        # Adjust based on performance metrics
        engagement_rate = performance_data.get('engagement_rate', 0)
        if engagement_rate < 0.001:
            severity_score += 1
        
        sentiment_score = performance_data.get('sentiment_score', 0.5)
        if sentiment_score < 0.1:
            severity_score += 2
        
        # Map score to severity enum
        if severity_score >= 5:
            return EmergencySeverity.CATASTROPHIC
        elif severity_score >= 4:
            return EmergencySeverity.CRITICAL
        elif severity_score >= 3:
            return EmergencySeverity.HIGH
        elif severity_score >= 2:
            return EmergencySeverity.MEDIUM
        else:
            return EmergencySeverity.LOW
    
    async def _generate_emergency_description(
        self, 
        emergency_type: EmergencyType, 
        conditions: List[str], 
        performance_data: Dict[str, Any]
    ) -> str:
        """Generate human-readable emergency description"""
        base_descriptions = {
            EmergencyType.VIRAL_CRISIS: "Viral content crisis detected with high negative sentiment",
            EmergencyType.ENGAGEMENT_COLLAPSE: "Severe engagement rate collapse detected",
            EmergencyType.NEGATIVE_SENTIMENT: "Critical negative sentiment crisis",
            EmergencyType.PLATFORM_VIOLATION: "Platform policy violation risk detected",
            EmergencyType.SECURITY_BREACH: "Security breach detected",
            EmergencyType.REPUTATION_DAMAGE: "Reputation damage crisis"
        }
        
        description = base_descriptions.get(emergency_type, "Emergency situation detected")
        
        # Add specific metrics
        engagement_rate = performance_data.get('engagement_rate', 0)
        sentiment_score = performance_data.get('sentiment_score', 0.5)
        
        description += f" (Engagement: {engagement_rate:.3f}, Sentiment: {sentiment_score:.3f})"
        
        return description
    
    async def _get_recommended_actions(
        self, 
        emergency_type: EmergencyType, 
        severity: EmergencySeverity
    ) -> List[str]:
        """Get recommended actions for emergency type and severity"""
        action_mapping = {
            EmergencyType.VIRAL_CRISIS: [
                'immediate_content_pause',
                'crisis_communication_activation',
                'legal_team_notification',
                'damage_control_measures'
            ],
            EmergencyType.ENGAGEMENT_COLLAPSE: [
                'emergency_content_boost',
                'cross_platform_promotion',
                'influencer_outreach',
                'content_strategy_review'
            ],
            EmergencyType.NEGATIVE_SENTIMENT: [
                'sentiment_recovery_campaign',
                'community_engagement',
                'public_relations_response',
                'content_moderation_increase'
            ],
            EmergencyType.PLATFORM_VIOLATION: [
                'immediate_compliance_review',
                'content_removal_if_necessary',
                'platform_appeal_preparation',
                'legal_consultation'
            ]
        }
        
        return action_mapping.get(emergency_type, ['general_crisis_response'])
    
    async def _execute_automatic_actions(
        self, 
        alert: EmergencyAlert, 
        actions: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute automatic emergency response actions"""
        executed_actions = []
        
        for action in actions:
            try:
                result = await self._execute_single_emergency_action(alert, action)
                executed_actions.append(result)
                
            except Exception as e:
                logger.error(f"Failed to execute emergency action {action}: {str(e)}")
                executed_actions.append({
                    'action': action,
                    'status': 'failed',
                    'error': str(e),
                    'cost': 0.0
                })
        
        return executed_actions
    
    async def _execute_single_emergency_action(
        self, 
        alert: EmergencyAlert, 
        action: str
    ) -> Dict[str, Any]:
        """Execute a single emergency action"""
        # Placeholder implementation - would integrate with actual systems
        action_costs = {
            'emergency_content_boost': 100.0,
            'cross_platform_amplification': 200.0,
            'influencer_outreach': 500.0,
            'pause_automated_posting': 0.0,
            'increase_monitoring_frequency': 0.0,
            'activate_crisis_communication': 50.0
        }
        
        cost = action_costs.get(action, 0.0)
        
        # Simulate action execution
        await asyncio.sleep(0.1)
        
        return {
            'action': action,
            'status': 'success',
            'executed_at': datetime.utcnow(),
            'cost': cost,
            'details': f"Executed {action} for emergency {alert.alert_id}"
        }
    
    async def _send_emergency_notifications(self, alert -> None: EmergencyAlert, protocol -> None: ResponseProtocol) -> None:
        """Send emergency notifications through configured channels"""
        for channel in protocol.notification_channels:
            try:
                await self._send_notification(channel, alert, protocol)
            except Exception as e:
                logger.error(f"Failed to send notification via {channel}: {str(e)}")
    
    async def _send_notification(self, channel -> None: str, alert -> None: EmergencyAlert, protocol -> None: ResponseProtocol) -> None:
        """Send notification through specific channel"""
        # Placeholder implementation
        logger.info(f"Sending {alert.severity.value} emergency notification via {channel}")
    
    async def _request_manual_approval(self, alert: EmergencyAlert, protocol: ResponseProtocol) -> Dict[str, Any]:
        """Request manual approval for emergency response"""
        # Placeholder - would integrate with approval system
        return {'approved': True, 'approver': 'system', 'timestamp': datetime.utcnow()}
    
    async def _create_default_protocol(self, emergency_type: EmergencyType) -> ResponseProtocol:
        """Create default protocol for emergency type"""
        return ResponseProtocol(
            protocol_id='default',
            emergency_type=emergency_type,
            severity_threshold=EmergencySeverity.MEDIUM,
            response_time_seconds=300,
            automatic_actions=['increase_monitoring', 'notify_team'],
            manual_approval_required=True,
            escalation_chain=['content_manager'],
            cost_limit=100.0,
            notification_channels=['email'],
            rollback_conditions=['manual_resolution']
        )
    
    async def _start_escalation_process(self, alert -> None: EmergencyAlert, protocol -> None: ResponseProtocol) -> None:
        """Start escalation process for emergency"""
        logger.warning(f"Starting escalation for emergency: {alert.alert_id}")
        # Placeholder implementation
    
    async def _store_emergency_response(self, response -> None: EmergencyResponse) -> None:
        """Store emergency response record"""
        if response.alert_id not in self.emergency_history:
            self.emergency_history[response.alert_id] = []
        self.emergency_history[response.alert_id].append(response)
    
    async def _get_current_performance(self, content_id: str, platform: str) -> Dict[str, Any]:
        """Get current performance data for content"""
        # Placeholder implementation
        return {
            'engagement_rate': 0.02,
            'sentiment_score': 0.6,
            'velocity': 1.0,
            'viral_potential': 0.3
        }
    
    async def _check_resolution_conditions(
        self, 
        alert: EmergencyAlert, 
        current_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if emergency resolution conditions are met"""
        # Placeholder implementation
        return {'resolved': False, 'needs_escalation': False}
    
    async def _resolve_emergency(self, alert_id -> None: str, resolution_status -> None: Dict[str, Any]) -> None:
        """Mark emergency as resolved"""
        if alert_id in self.active_emergencies:
            del self.active_emergencies[alert_id]
        logger.info(f"Emergency resolved: {alert_id}")
    
    async def _escalate_emergency(self, alert_id -> None: str) -> None:
        """Escalate emergency to next level"""
        logger.warning(f"Escalating emergency: {alert_id}")
    
    async def _scan_for_new_emergencies(self) -> None:
        """Scan for new emergency conditions"""
        # Placeholder implementation
        pass
    
    async def _get_recent_emergency_stats(self) -> Dict[str, Any]:
        """Get recent emergency statistics"""
        return {
            'last_24h': 3,
            'average_response_time': 120,
            'resolution_rate': 0.95
        }
    
    async def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate emergency response system health"""
        return {
            'status': 'healthy',
            'response_time_avg': 90,
            'success_rate': 0.98
        }
    
    async def _create_denied_response(self, alert: EmergencyAlert, protocol: ResponseProtocol) -> EmergencyResponse:
        """Create response record for denied emergency response"""
        return EmergencyResponse(
            response_id=f"denied_{alert.alert_id}",
            alert_id=alert.alert_id,
            protocol_used=protocol.protocol_id,
            actions_taken=[{'action': 'approval_denied', 'status': 'denied'}],
            response_time=0,
            cost_incurred=0.0,
            effectiveness_score=0.0,
            resolution_status='denied',
            created_at=datetime.utcnow(),
            resolved_at=None
        )


__all__ = [
    'EmergencyResponseSystem', 'EmergencyAlert', 'EmergencyResponse', 'ResponseProtocol',
    'EmergencyType', 'EmergencySeverity'
]