"""
🛡️ Protection Enforcer - IA Influencer Agent Surveillance Module
==============================================================

Advanced protection enforcement system that coordinates all protective measures,
automated responses, and content safeguarding strategies.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """Protection enforcement levels"""
    PASSIVE = "passive"          # Monitor only
    DEFENSIVE = "defensive"      # Basic automated protection
    AGGRESSIVE = "aggressive"    # Active enforcement
    MAXIMUM = "maximum"          # All available measures
    EMERGENCY = "emergency"      # Emergency lockdown mode


class ProtectionAction(Enum):
    """Available protection actions"""
    MONITOR = "monitor"
    ALERT = "alert"
    TAKEDOWN_REQUEST = "takedown_request"
    LEGAL_NOTICE = "legal_notice"
    CONTENT_BLOCK = "content_block"
    WATERMARK_INJECTION = "watermark_injection"
    FINGERPRINT_PROTECTION = "fingerprint_protection"
    PLATFORM_REPORT = "platform_report"
    RATE_LIMIT = "rate_limit"
    GEO_BLOCK = "geo_block"
    DMCA_STRIKE = "dmca_strike"
    ACCOUNT_FLAG = "account_flag"
    CONTENT_CLAIM = "content_claim"
    EMERGENCY_SHUTDOWN = "emergency_shutdown"


class ThreatLevel(Enum):
    """Threat assessment levels"""
    MINIMAL = "minimal"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class ProtectionRule:
    """Protection rule definition"""
    rule_id: str
    name: str
    description: str
    
    # Trigger conditions
    trigger_conditions: Dict[str, Any] = field(default_factory=dict)
    threat_level_threshold: ThreatLevel = ThreatLevel.MODERATE
    
    # Actions to execute
    actions: List[ProtectionAction] = field(default_factory=list)
    protection_level: ProtectionLevel = ProtectionLevel.DEFENSIVE
    
    # Rule constraints
    max_executions_per_hour: Optional[int] = None
    cooldown_minutes: int = 0
    priority: int = 1  # 1-10, higher is more priority
    
    # Conditions
    creator_ids: Optional[List[str]] = None
    content_types: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_executed: Optional[datetime] = None
    execution_count: int = 0


@dataclass
class ProtectionIncident:
    """Protection incident tracking"""
    incident_id: str
    creator_id: str
    content_id: Optional[str] = None
    
    # Incident details
    threat_type: str = "unknown"
    threat_level: ThreatLevel = ThreatLevel.LOW
    threat_description: str = ""
    
    # Detection information
    detected_by: str = "system"
    detection_confidence: float = 0.0
    detection_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Protection response
    triggered_rules: List[str] = field(default_factory=list)
    executed_actions: List[ProtectionAction] = field(default_factory=list)
    protection_effectiveness: float = 0.0
    
    # Incident tracking
    status: str = "open"  # open, investigating, mitigated, closed
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    # Timeline
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
    
    # Impact assessment
    estimated_damage: float = 0.0
    potential_reach: int = 0
    infringement_urls: List[str] = field(default_factory=list)


@dataclass
class ProtectionMetrics:
    """Protection system metrics"""
    period_start: datetime
    period_end: datetime
    
    # Incident statistics
    total_incidents: int = 0
    incidents_by_threat_level: Dict[str, int] = field(default_factory=dict)
    incidents_by_type: Dict[str, int] = field(default_factory=dict)
    
    # Protection effectiveness
    successful_protections: int = 0
    failed_protections: int = 0
    avg_response_time_minutes: float = 0.0
    
    # Action statistics
    actions_executed: Dict[str, int] = field(default_factory=dict)
    rules_triggered: Dict[str, int] = field(default_factory=dict)
    
    # Financial impact
    estimated_damage_prevented: float = 0.0
    protection_cost: float = 0.0
    roi_percentage: float = 0.0


class BaseProtectionAction:
    """Base class for protection actions"""
    
    def __init__(self, action_type: ProtectionAction, config: Dict[str, Any]):
        self.action_type = action_type
        self.config = config
        self.enabled = config.get("enabled", True)
        self.max_concurrent = config.get("max_concurrent", 10)
        self.timeout_seconds = config.get("timeout", 30)
        self.active_executions = 0
    
    async def execute(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute protection action"""
        if not self.enabled:
            return {"success": False, "reason": "action_disabled"}
        
        if self.active_executions >= self.max_concurrent:
            return {"success": False, "reason": "max_concurrent_reached"}
        
        self.active_executions += 1
        
        try:
            result = await self._execute_action(incident, context)
            return result
        finally:
            self.active_executions -= 1
    
    async def _execute_action(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Implement specific action logic"""
        # Default implementation for protection actions without specific logic
        logging.warning(f"Action execution not implemented for {self.__class__.__name__}")
        return {
            "action_type": self.__class__.__name__,
            "status": "not_implemented",
            "message": f"Action execution not implemented for {self.__class__.__name__}",
            "incident_id": incident.id if hasattr(incident, 'id') else "unknown"
        }


class TakedownRequestAction(BaseProtectionAction):
    """Automated takedown request action"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProtectionAction.TAKEDOWN_REQUEST, config)
    
    async def _execute_action(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute takedown request"""
        try:
            # Get takedown manager from context
            takedown_manager = context.get("takedown_manager")
            if not takedown_manager:
                return {"success": False, "reason": "takedown_manager_not_available"}
            
            # Create takedown request for each infringing URL
            results = []
            
            for url in incident.infringement_urls:
                # Extract platform from URL (simplified)
                platform = self._extract_platform_from_url(url)
                
                # Create mock infringement data
                infringement_data = type('InfringementData', (), {
                    'infringing_url': url,
                    'platform': platform,
                    'similarity_score': incident.detection_confidence,
                    'estimated_revenue_loss': incident.estimated_damage,
                    'infringement_type': incident.threat_type
                })()
                
                # Create takedown request
                request = await takedown_manager.create_takedown_request(
                    creator_id=incident.creator_id,
                    content_id=incident.content_id or "unknown",
                    infringement_data=infringement_data,
                    priority="high" if incident.threat_level in [ThreatLevel.SEVERE, ThreatLevel.CRITICAL] else "normal"
                )
                
                results.append({
                    "url": url,
                    "platform": platform,
                    "request_id": request.request_id,
                    "success": request.success
                })
            
            success_count = len([r for r in results if r["success"]])
            
            return {
                "success": success_count > 0,
                "takedown_requests": results,
                "total_requests": len(results),
                "successful_requests": success_count
            }
            
        except Exception as e:
            logger.error(f"Takedown request action failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_platform_from_url(self, url: str) -> str:
        """Extract platform from URL"""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'tiktok.com' in url_lower:
            return 'tiktok'
        elif 'instagram.com' in url_lower:
            return 'instagram'
        elif 'facebook.com' in url_lower:
            return 'facebook'
        elif 'twitter.com' in url_lower or 'x.com' in url_lower:
            return 'twitter'
        else:
            return 'unknown'


class AlertAction(BaseProtectionAction):
    """Alert notification action"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProtectionAction.ALERT, config)
    
    async def _execute_action(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute alert action"""
        try:
            alert_system = context.get("alert_system")
            if not alert_system:
                return {"success": False, "reason": "alert_system_not_available"}
            
            # Map threat level to alert severity
            severity_mapping = {
                ThreatLevel.MINIMAL: "info",
                ThreatLevel.LOW: "low", 
                ThreatLevel.MODERATE: "medium",
                ThreatLevel.HIGH: "high",
                ThreatLevel.SEVERE: "critical",
                ThreatLevel.CRITICAL: "emergency"
            }
            
            # Create alert
            alert = await alert_system.create_alert(
                alert_type="INFRINGEMENT_DETECTED",  # This would be imported from AlertType
                creator_id=incident.creator_id,
                title=f"Protection Incident: {incident.threat_type}",
                message=f"A {incident.threat_level.value} level threat has been detected: {incident.threat_description}",
                severity=severity_mapping.get(incident.threat_level, "medium"),
                content_id=incident.content_id,
                data={
                    "incident_id": incident.incident_id,
                    "threat_type": incident.threat_type,
                    "threat_level": incident.threat_level.value,
                    "detection_confidence": incident.detection_confidence,
                    "infringement_urls": incident.infringement_urls,
                    "estimated_damage": incident.estimated_damage
                }
            )
            
            return {
                "success": True,
                "alert_id": alert.alert_id,
                "severity": alert.severity.value
            }
            
        except Exception as e:
            logger.error(f"Alert action failed: {e}")
            return {"success": False, "error": str(e)}


class ContentBlockAction(BaseProtectionAction):
    """Content blocking action"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProtectionAction.CONTENT_BLOCK, config)
    
    async def _execute_action(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content blocking"""
        try:
            # In production, this would interface with CDN/firewall systems
            blocked_urls = []
            
            for url in incident.infringement_urls:
                # Simulate content blocking
                block_result = await self._simulate_content_block(url)
                if block_result["success"]:
                    blocked_urls.append(url)
                
                # Add to simulated blocked content list
                logger.info(f"Content blocked: {url}")
            
            return {
                "success": len(blocked_urls) > 0,
                "blocked_urls": blocked_urls,
                "total_blocks": len(blocked_urls),
                "failed_blocks": len(incident.infringement_urls) - len(blocked_urls)
            }
            
        except Exception as e:
            logger.error(f"Content block action failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _simulate_content_block(self, url: str) -> Dict[str, Any]:
        """Simulate content blocking"""
        # Simulate 90% success rate
        success = hash(url) % 10 != 0
        return {"success": success, "url": url}


class FingerprintProtectionAction(BaseProtectionAction):
    """Fingerprint protection enhancement action"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(ProtectionAction.FINGERPRINT_PROTECTION, config)
    
    async def _execute_action(self, incident: ProtectionIncident, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fingerprint protection enhancement"""
        try:
            # Simulate enhancing fingerprint protection
            if incident.content_id:
                # In production, this would update fingerprint databases,
                # add additional hash variants, update matching algorithms, etc.
                
                enhanced_features = {
                    "additional_hash_variants": 5,
                    "enhanced_sensitivity": True,
                    "cross_platform_monitoring": True,
                    "real_time_matching": True
                }
                
                logger.info(f"Enhanced fingerprint protection for content {incident.content_id}")
                
                return {
                    "success": True,
                    "content_id": incident.content_id,
                    "enhancements": enhanced_features
                }
            else:
                return {"success": False, "reason": "no_content_id"}
                
        except Exception as e:
            logger.error(f"Fingerprint protection action failed: {e}")
            return {"success": False, "error": str(e)}


class ProtectionEnforcer:
    """
    Advanced protection enforcement system that coordinates all protective measures,
    automated responses, and content safeguarding strategies
    """
    
    def __init__(self, surveillance_system):
        self.surveillance_system = surveillance_system
        self.protection_rules: Dict[str, ProtectionRule] = {}
        self.action_handlers: Dict[ProtectionAction, BaseProtectionAction] = {}
        self.active_incidents: Dict[str, ProtectionIncident] = {}
        self.incident_history: deque = deque(maxlen=10000)  # Keep last 10k incidents
        self.protection_queue: asyncio.Queue = asyncio.Queue()
        self.enforcement_task: Optional[asyncio.Task] = None
        self.initialized = False
        
        # Metrics tracking
        self.current_metrics = ProtectionMetrics(
            period_start=datetime.now(timezone.utc),
            period_end=datetime.now(timezone.utc)
        )
        
        # Rate limiting
        self.rule_execution_counts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
    
    async def initialize(self) -> None:
        """Initialize protection enforcer"""
        try:
            # Initialize action handlers
            action_config = self.surveillance_system.config.get("protection_actions", {})
            
            self.action_handlers[ProtectionAction.TAKEDOWN_REQUEST] = TakedownRequestAction(
                action_config.get("takedown_request", {})
            )
            self.action_handlers[ProtectionAction.ALERT] = AlertAction(
                action_config.get("alert", {})
            )
            self.action_handlers[ProtectionAction.CONTENT_BLOCK] = ContentBlockAction(
                action_config.get("content_block", {})
            )
            self.action_handlers[ProtectionAction.FINGERPRINT_PROTECTION] = FingerprintProtectionAction(
                action_config.get("fingerprint_protection", {})
            )
            
            # Load default protection rules
            await self._load_default_protection_rules()
            
            # Start enforcement task
            self.enforcement_task = asyncio.create_task(self._process_protection_queue())
            
            self.initialized = True
            logger.info(f"Protection Enforcer initialized with {len(self.protection_rules)} rules and {len(self.action_handlers)} actions")
            
        except Exception as e:
            logger.error(f"Failed to initialize Protection Enforcer: {e}")
            raise
    
    async def _load_default_protection_rules(self) -> None:
        """Load default protection rules"""
        default_rules = [
            ProtectionRule(
                rule_id="high_similarity_infringement",
                name="High Similarity Infringement Response",
                description="Automated response to high-similarity content infringements",
                trigger_conditions={"similarity_score": {">=": 0.85}},
                threat_level_threshold=ThreatLevel.HIGH,
                actions=[ProtectionAction.ALERT, ProtectionAction.TAKEDOWN_REQUEST],
                protection_level=ProtectionLevel.AGGRESSIVE,
                max_executions_per_hour=20,
                cooldown_minutes=30,
                priority=8
            ),
            
            ProtectionRule(
                rule_id="viral_content_protection",
                name="Viral Content Protection",
                description="Enhanced protection for viral content",
                trigger_conditions={
                    "views": {">=": 100000},
                    "similarity_score": {">=": 0.7}
                },
                threat_level_threshold=ThreatLevel.SEVERE,
                actions=[
                    ProtectionAction.ALERT,
                    ProtectionAction.TAKEDOWN_REQUEST,
                    ProtectionAction.FINGERPRINT_PROTECTION,
                    ProtectionAction.CONTENT_BLOCK
                ],
                protection_level=ProtectionLevel.MAXIMUM,
                max_executions_per_hour=5,
                cooldown_minutes=60,
                priority=9
            ),
            
            ProtectionRule(
                rule_id="mass_infringement_emergency",
                name="Mass Infringement Emergency Response",
                description="Emergency response to mass infringement events",
                trigger_conditions={"infringement_count": {">=": 10}},
                threat_level_threshold=ThreatLevel.CRITICAL,
                actions=[
                    ProtectionAction.ALERT,
                    ProtectionAction.TAKEDOWN_REQUEST,
                    ProtectionAction.CONTENT_BLOCK,
                    ProtectionAction.FINGERPRINT_PROTECTION
                ],
                protection_level=ProtectionLevel.EMERGENCY,
                max_executions_per_hour=2,
                cooldown_minutes=120,
                priority=10
            ),
            
            ProtectionRule(
                rule_id="moderate_infringement_monitoring",
                name="Moderate Infringement Monitoring",
                description="Monitor and alert for moderate infringements",
                trigger_conditions={"similarity_score": {">=": 0.6}},
                threat_level_threshold=ThreatLevel.MODERATE,
                actions=[ProtectionAction.ALERT, ProtectionAction.MONITOR],
                protection_level=ProtectionLevel.DEFENSIVE,
                max_executions_per_hour=50,
                cooldown_minutes=10,
                priority=3
            ),
            
            ProtectionRule(
                rule_id="revenue_impact_protection",
                name="Revenue Impact Protection",
                description="Protect against high revenue impact infringements",
                trigger_conditions={"estimated_loss": {">=": 1000}},
                threat_level_threshold=ThreatLevel.HIGH,
                actions=[
                    ProtectionAction.ALERT,
                    ProtectionAction.TAKEDOWN_REQUEST,
                    ProtectionAction.LEGAL_NOTICE
                ],
                protection_level=ProtectionLevel.AGGRESSIVE,
                max_executions_per_hour=10,
                cooldown_minutes=45,
                priority=7
            )
        ]
        
        for rule in default_rules:
            self.protection_rules[rule.rule_id] = rule
        
        logger.info(f"Loaded {len(default_rules)} default protection rules")
    
    async def report_threat(
        self,
        creator_id: str,
        threat_type: str,
        threat_level: ThreatLevel,
        threat_description: str,
        content_id: Optional[str] = None,
        infringement_urls: Optional[List[str]] = None,
        detection_confidence: float = 0.0,
        estimated_damage: float = 0.0,
        **kwargs
    ) -> str:
        """Report a security threat for protection enforcement"""
        incident_id = f"incident_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        incident = ProtectionIncident(
            incident_id=incident_id,
            creator_id=creator_id,
            content_id=content_id,
            threat_type=threat_type,
            threat_level=threat_level,
            threat_description=threat_description,
            detection_confidence=detection_confidence,
            estimated_damage=estimated_damage,
            infringement_urls=infringement_urls or [],
            detected_by=kwargs.get("detected_by", "system"),
            potential_reach=kwargs.get("potential_reach", 0)
        )
        
        # Add to active incidents
        self.active_incidents[incident_id] = incident
        
        # Queue for processing
        await self.protection_queue.put(incident)
        
        logger.info(f"Threat reported: {incident_id} ({threat_type}, level: {threat_level.value})")
        
        return incident_id
    
    async def _process_protection_queue(self) -> None:
        """Process protection incidents from queue"""
        while True:
            try:
                # Get incident from queue
                incident = await self.protection_queue.get()
                
                # Process the incident
                await self._process_protection_incident(incident)
                
                # Mark task as done
                self.protection_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing protection queue: {e}")
                await asyncio.sleep(1)
    
    async def _process_protection_incident(self, incident: ProtectionIncident) -> None:
        """Process a single protection incident"""
        try:
            # Find matching protection rules
            matching_rules = await self._find_matching_rules(incident)
            
            if not matching_rules:
                logger.info(f"No matching rules for incident {incident.incident_id}")
                return
            
            # Sort rules by priority (higher priority first)
            matching_rules.sort(key=lambda r: r.priority, reverse=True)
            
            executed_actions = []
            triggered_rules = []
            
            # Execute rules
            for rule in matching_rules:
                # Check rate limiting
                if not await self._check_rate_limit(rule):
                    logger.warning(f"Rule {rule.rule_id} rate limited")
                    continue
                
                # Check cooldown
                if not await self._check_cooldown(rule):
                    logger.info(f"Rule {rule.rule_id} in cooldown")
                    continue
                
                # Execute rule actions
                rule_actions = await self._execute_rule_actions(rule, incident)
                executed_actions.extend(rule_actions)
                triggered_rules.append(rule.rule_id)
                
                # Update rule execution tracking
                rule.last_executed = datetime.now(timezone.utc)
                rule.execution_count += 1
                self.rule_execution_counts[rule.rule_id].append(datetime.now(timezone.utc))
                
                logger.info(f"Executed rule {rule.rule_id} for incident {incident.incident_id}")
            
            # Update incident
            incident.triggered_rules = triggered_rules
            incident.executed_actions = executed_actions
            
            # Calculate protection effectiveness
            incident.protection_effectiveness = await self._calculate_protection_effectiveness(incident, executed_actions)
            
            # Update metrics
            await self._update_protection_metrics(incident, executed_actions)
            
            logger.info(f"Processed incident {incident.incident_id}: {len(triggered_rules)} rules, {len(executed_actions)} actions")
            
        except Exception as e:
            logger.error(f"Failed to process incident {incident.incident_id}: {e}")
            incident.status = "error"
    
    async def _find_matching_rules(self, incident: ProtectionIncident) -> List[ProtectionRule]:
        """Find protection rules that match the incident"""
        matching_rules = []
        
        for rule in self.protection_rules.values():
            if not rule.active:
                continue
            
            # Check threat level threshold
            threat_levels = list(ThreatLevel)
            if threat_levels.index(incident.threat_level) < threat_levels.index(rule.threat_level_threshold):
                continue
            
            # Check creator filter
            if rule.creator_ids and incident.creator_id not in rule.creator_ids:
                continue
            
            # Check content type filter (if applicable)
            # This would need content type information from the incident context
            
            # Check platform filter (if applicable)
            # This would need platform information from infringement URLs
            
            # Check trigger conditions
            if await self._check_trigger_conditions(rule, incident):
                matching_rules.append(rule)
        
        return matching_rules
    
    async def _check_trigger_conditions(self, rule: ProtectionRule, incident: ProtectionIncident) -> bool:
        """Check if incident meets rule trigger conditions"""
        for condition_key, condition_value in rule.trigger_conditions.items():
            # Get incident value
            incident_value = await self._get_incident_value(incident, condition_key)
            
            if incident_value is None:
                continue
            
            if isinstance(condition_value, dict):
                # Handle comparison operators
                for operator, expected_value in condition_value.items():
                    if operator == ">=" and not (incident_value >= expected_value):
                        return False
                    elif operator == ">" and not (incident_value > expected_value):
                        return False
                    elif operator == "<=" and not (incident_value <= expected_value):
                        return False
                    elif operator == "<" and not (incident_value < expected_value):
                        return False
                    elif operator == "==" and not (incident_value == expected_value):
                        return False
                    elif operator == "!=" and not (incident_value != expected_value):
                        return False
            else:
                # Direct value comparison
                if incident_value != condition_value:
                    return False
        
        return True
    
    async def _get_incident_value(self, incident: ProtectionIncident, key: str) -> Any:
        """Get incident value by key"""
        if key == "similarity_score":
            return incident.detection_confidence
        elif key == "estimated_loss":
            return incident.estimated_damage
        elif key == "infringement_count":
            return len(incident.infringement_urls)
        elif key == "threat_level":
            return incident.threat_level.value
        elif key == "views" or key == "potential_reach":
            return incident.potential_reach
        
        return None
    
    async def _check_rate_limit(self, rule: ProtectionRule) -> bool:
        """Check if rule has exceeded rate limit"""
        if not rule.max_executions_per_hour:
            return True
        
        executions = self.rule_execution_counts[rule.rule_id]
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=1)
        
        # Count executions in last hour
        recent_executions = len([t for t in executions if t > cutoff_time])
        
        return recent_executions < rule.max_executions_per_hour
    
    async def _check_cooldown(self, rule: ProtectionRule) -> bool:
        """Check if rule is in cooldown period"""
        if not rule.cooldown_minutes or not rule.last_executed:
            return True
        
        cooldown_end = rule.last_executed + timedelta(minutes=rule.cooldown_minutes)
        return datetime.now(timezone.utc) > cooldown_end
    
    async def _execute_rule_actions(self, rule: ProtectionRule, incident: ProtectionIncident) -> List[ProtectionAction]:
        """Execute all actions for a rule"""
        executed_actions = []
        
        # Prepare context for actions
        context = {
            "surveillance_system": self.surveillance_system,
            "takedown_manager": getattr(self.surveillance_system, 'takedown_manager', None),
            "alert_system": getattr(self.surveillance_system, 'alert_system', None),
            "rule": rule,
            "incident": incident
        }
        
        for action in rule.actions:
            if action in self.action_handlers:
                try:
                    handler = self.action_handlers[action]
                    result = await handler.execute(incident, context)
                    
                    if result.get("success", False):
                        executed_actions.append(action)
                        logger.info(f"Action {action.value} executed successfully for incident {incident.incident_id}")
                    else:
                        logger.warning(f"Action {action.value} failed for incident {incident.incident_id}: {result.get('reason', 'unknown')}")
                        
                except Exception as e:
                    logger.error(f"Action {action.value} execution failed: {e}")
            else:
                logger.warning(f"No handler available for action: {action.value}")
        
        return executed_actions
    
    async def _calculate_protection_effectiveness(self, incident: ProtectionIncident, executed_actions: List[ProtectionAction]) -> float:
        """Calculate protection effectiveness score"""
        base_effectiveness = 0.0
        
        # Weight actions by effectiveness
        action_weights = {
            ProtectionAction.MONITOR: 0.1,
            ProtectionAction.ALERT: 0.2,
            ProtectionAction.TAKEDOWN_REQUEST: 0.8,
            ProtectionAction.CONTENT_BLOCK: 0.9,
            ProtectionAction.FINGERPRINT_PROTECTION: 0.6,
            ProtectionAction.LEGAL_NOTICE: 0.7,
            ProtectionAction.DMCA_STRIKE: 0.85,
            ProtectionAction.EMERGENCY_SHUTDOWN: 1.0
        }
        
        total_weight = 0.0
        for action in executed_actions:
            weight = action_weights.get(action, 0.3)
            total_weight += weight
        
        # Normalize to 0-1 scale
        if total_weight > 0:
            base_effectiveness = min(1.0, total_weight / 2.0)  # Divide by 2 to allow for action combinations
        
        # Adjust based on threat level (higher threat = harder to protect completely)
        threat_multiplier = {
            ThreatLevel.MINIMAL: 1.0,
            ThreatLevel.LOW: 0.95,
            ThreatLevel.MODERATE: 0.9,
            ThreatLevel.HIGH: 0.8,
            ThreatLevel.SEVERE: 0.7,
            ThreatLevel.CRITICAL: 0.6
        }
        
        multiplier = threat_multiplier.get(incident.threat_level, 0.5)
        return base_effectiveness * multiplier
    
    async def _update_protection_metrics(self, incident: ProtectionIncident, executed_actions: List[ProtectionAction]) -> None:
        """Update protection system metrics"""
        metrics = self.current_metrics
        
        # Update incident counts
        metrics.total_incidents += 1
        
        threat_level = incident.threat_level.value
        metrics.incidents_by_threat_level[threat_level] = metrics.incidents_by_threat_level.get(threat_level, 0) + 1
        
        threat_type = incident.threat_type
        metrics.incidents_by_type[threat_type] = metrics.incidents_by_type.get(threat_type, 0) + 1
        
        # Update protection effectiveness
        if incident.protection_effectiveness > 0.7:
            metrics.successful_protections += 1
        else:
            metrics.failed_protections += 1
        
        # Update action statistics
        for action in executed_actions:
            action_name = action.value
            metrics.actions_executed[action_name] = metrics.actions_executed.get(action_name, 0) + 1
        
        # Update rule statistics
        for rule_id in incident.triggered_rules:
            metrics.rules_triggered[rule_id] = metrics.rules_triggered.get(rule_id, 0) + 1
        
        # Update financial metrics
        metrics.estimated_damage_prevented += incident.estimated_damage * incident.protection_effectiveness
    
    async def get_incident_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a protection incident"""
        if incident_id not in self.active_incidents:
            return None
        
        incident = self.active_incidents[incident_id]
        
        return {
            "incident_id": incident.incident_id,
            "creator_id": incident.creator_id,
            "threat_type": incident.threat_type,
            "threat_level": incident.threat_level.value,
            "status": incident.status,
            "triggered_rules": incident.triggered_rules,
            "executed_actions": [action.value for action in incident.executed_actions],
            "protection_effectiveness": incident.protection_effectiveness,
            "estimated_damage": incident.estimated_damage,
            "created_at": incident.created_at.isoformat(),
            "resolved_at": incident.resolved_at.isoformat() if incident.resolved_at else None
        }
    
    async def list_active_incidents(self, creator_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active protection incidents"""
        incidents = []
        
        for incident in self.active_incidents.values():
            if creator_id and incident.creator_id != creator_id:
                continue
            
            incidents.append({
                "incident_id": incident.incident_id,
                "creator_id": incident.creator_id,
                "threat_type": incident.threat_type,
                "threat_level": incident.threat_level.value,
                "status": incident.status,
                "protection_effectiveness": incident.protection_effectiveness,
                "created_at": incident.created_at.isoformat()
            })
        
        return sorted(incidents, key=lambda x: x["created_at"], reverse=True)
    
    async def resolve_incident(self, incident_id: str, resolution_notes: Optional[str] = None) -> bool:
        """Resolve a protection incident"""
        if incident_id not in self.active_incidents:
            return False
        
        incident = self.active_incidents[incident_id]
        incident.status = "closed"
        incident.resolved_at = datetime.now(timezone.utc)
        incident.resolution_notes = resolution_notes
        
        # Move to history
        self.incident_history.append(incident)
        del self.active_incidents[incident_id]
        
        logger.info(f"Incident resolved: {incident_id}")
        return True
    
    async def get_protection_metrics(self, period_hours: int = 24) -> ProtectionMetrics:
        """Get protection metrics for a time period"""
        # For simplicity, return current metrics
        # In production, this would calculate metrics for the specified period
        metrics = self.current_metrics
        metrics.period_end = datetime.now(timezone.utc)
        
        # Calculate ROI
        if metrics.protection_cost > 0:
            metrics.roi_percentage = ((metrics.estimated_damage_prevented - metrics.protection_cost) / metrics.protection_cost) * 100
        
        return metrics
    
    async def update_protection_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update a protection rule"""
        if rule_id not in self.protection_rules:
            return False
        
        rule = self.protection_rules[rule_id]
        
        # Update allowed fields
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        logger.info(f"Protection rule updated: {rule_id}")
        return True
    
    async def add_protection_rule(self, rule: ProtectionRule) -> None:
        """Add a new protection rule"""
        self.protection_rules[rule.rule_id] = rule
        logger.info(f"Protection rule added: {rule.rule_id}")
    
    async def remove_protection_rule(self, rule_id: str) -> bool:
        """Remove a protection rule"""
        if rule_id not in self.protection_rules:
            return False
        
        del self.protection_rules[rule_id]
        logger.info(f"Protection rule removed: {rule_id}")
        return True
    
    async def get_enforcement_statistics(self) -> Dict[str, Any]:
        """Get enforcement statistics"""
        total_incidents = len(self.active_incidents) + len(self.incident_history)
        active_incidents = len(self.active_incidents)
        resolved_incidents = len(self.incident_history)
        
        # Calculate success rate
        if total_incidents > 0:
            success_rate = (self.current_metrics.successful_protections / 
                          (self.current_metrics.successful_protections + self.current_metrics.failed_protections) * 100)
        else:
            success_rate = 0.0
        
        return {
            "total_incidents": total_incidents,
            "active_incidents": active_incidents,
            "resolved_incidents": resolved_incidents,
            "success_rate": round(success_rate, 2),
            "total_rules": len(self.protection_rules),
            "active_rules": len([r for r in self.protection_rules.values() if r.active]),
            "available_actions": len(self.action_handlers),
            "queue_size": self.protection_queue.qsize(),
            "estimated_damage_prevented": round(self.current_metrics.estimated_damage_prevented, 2)
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on protection enforcer"""
        return {
            "enforcer": "healthy" if self.initialized else "unhealthy",
            "protection_rules": len(self.protection_rules),
            "action_handlers": len(self.action_handlers),
            "active_incidents": len(self.active_incidents),
            "queue_size": self.protection_queue.qsize(),
            "enforcement_active": self.enforcement_task is not None and not self.enforcement_task.done(),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def shutdown(self) -> None:
        """Gracefully shutdown protection enforcer"""
        logger.info("Shutting down Protection Enforcer")
        
        if self.enforcement_task:
            self.enforcement_task.cancel()
            try:
                await self.enforcement_task
            except asyncio.CancelledError:
                pass
        
        # Wait for queue to empty
        await self.protection_queue.join()
        
        # Resolve all active incidents
        for incident_id in list(self.active_incidents.keys()):
            await self.resolve_incident(incident_id, "System shutdown")
        
        self.initialized = False
        logger.info("Protection Enforcer shutdown complete")


# Export main components
__all__ = [
    "ProtectionEnforcer",
    "ProtectionLevel",
    "ProtectionAction",
    "ThreatLevel",
    "ProtectionRule",
    "ProtectionIncident",
    "ProtectionMetrics",
    "BaseProtectionAction",
    "TakedownRequestAction",
    "AlertAction",
    "ContentBlockAction",
    "FingerprintProtectionAction"
]
