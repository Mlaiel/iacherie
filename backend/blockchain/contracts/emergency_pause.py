"""Emergency Pause Contract - IA-Influencer-Agent Platform

This module provides emergency pause functionality for critical system
operations with role-based controls, automated triggers, and recovery
mechanisms for platform security and stability.

Features:
- Emergency pause mechanisms
- Role-based pause controls
- Automated trigger conditions
- Graceful recovery procedures
- Audit trail maintenance
- Multi-level pause granularity

(c) 2025 Fahed Mlaiel (mlaiel@live.de) - IA-Influencer-Agent Platform
Propriété Intellectuelle Exclusive - Tous Droits Réservés
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

logger = logging.getLogger(__name__)


class PauseLevel(Enum):
    """Levels of emergency pause"""
    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"
    CRITICAL = "critical"


class PauseReason(Enum):
    """Reasons for emergency pause"""
    SECURITY_BREACH = "security_breach"
    SMART_CONTRACT_BUG = "smart_contract_bug"
    ORACLE_FAILURE = "oracle_failure"
    NETWORK_CONGESTION = "network_congestion"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    MAINTENANCE = "maintenance"
    MARKET_VOLATILITY = "market_volatility"
    ADMIN_REQUEST = "admin_request"


class SystemComponent(Enum):
    """System components that can be paused"""
    PAYMENTS = "payments"
    NFT_MINTING = "nft_minting"
    CONTENT_UPLOADS = "content_uploads"
    MARKETPLACE = "marketplace"
    GOVERNANCE = "governance"
    STAKING = "staking"
    ORACLES = "oracles"
    USER_REGISTRATION = "user_registration"
    WITHDRAWALS = "withdrawals"
    ALL_OPERATIONS = "all_operations"


@dataclass
class PauseEvent:
    """Emergency pause event record"""
    event_id: str
    pause_level: PauseLevel
    reason: PauseReason
    components: Set[SystemComponent]
    triggered_by: str
    triggered_at: datetime
    description: str
    automatic_trigger: bool
    recovery_conditions: Dict[str, Any]
    estimated_duration: Optional[timedelta]


@dataclass
class PauseStatus:
    """Current pause status"""
    is_paused: bool
    pause_level: PauseLevel
    paused_components: Set[SystemComponent]
    active_events: List[str]
    last_pause_at: Optional[datetime]
    total_pause_duration: timedelta
    can_operate: Dict[SystemComponent, bool]


class EmergencyPause:
    """
    Emergency Pause Management System
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Emergency Pause system"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # System state
        self.current_status = PauseStatus(
            is_paused=False,
            pause_level=PauseLevel.NONE,
            paused_components=set(),
            active_events=[],
            last_pause_at=None,
            total_pause_duration=timedelta(),
            can_operate={}
        )
        
        # Event tracking
        self.pause_events: Dict[str, PauseEvent] = {}
        self.pause_history: List[str] = []
        
        # Authorization
        self.authorized_pausers: Set[str] = set(config.get("authorized_pausers", []))
        self.emergency_contacts: List[str] = config.get("emergency_contacts", [])
        
        # Automatic triggers
        self.auto_triggers_enabled = config.get("auto_triggers", True)
        self.max_auto_pause_duration = timedelta(hours=config.get("max_auto_hours", 24))
        
        # Initialize component operational status
        self._init_component_status()
    
    def _init_component_status(self):
        """Initialize component operational status"""
        for component in SystemComponent:
            self.current_status.can_operate[component] = True
    
    async def trigger_pause(
        self,
        pause_level: PauseLevel,
        reason: PauseReason,
        components: List[SystemComponent],
        triggered_by: str,
        description: str,
        automatic: bool = False,
        estimated_duration: Optional[int] = None  # hours
    ) -> PauseEvent:
        """Trigger emergency pause"""
        try:
            event_id = str(uuid.uuid4())
            
            self.logger.critical(f"EMERGENCY PAUSE TRIGGERED: {reason.value} - Level: {pause_level.value}")
            
            # Validate authorization
            if not automatic and triggered_by not in self.authorized_pausers:
                raise ValueError(f"Unauthorized pause request from: {triggered_by}")
            
            # Convert duration
            duration = None
            if estimated_duration:
                duration = timedelta(hours=estimated_duration)
            
            # Create pause event
            pause_event = PauseEvent(
                event_id=event_id,
                pause_level=pause_level,
                reason=reason,
                components=set(components),
                triggered_by=triggered_by,
                triggered_at=datetime.utcnow(),
                description=description,
                automatic_trigger=automatic,
                recovery_conditions=self._generate_recovery_conditions(reason, pause_level),
                estimated_duration=duration
            )
            
            # Apply pause
            await self._apply_pause(pause_event)
            
            # Store event
            self.pause_events[event_id] = pause_event
            self.pause_history.append(event_id)
            
            # Notify stakeholders
            await self._notify_emergency_contacts(pause_event)
            
            self.logger.critical(f"Emergency pause activated: {event_id}")
            return pause_event
            
        except Exception as e:
            self.logger.error(f"Emergency pause failed: {e}")
            raise
    
    async def _apply_pause(self, pause_event: PauseEvent):
        """Apply pause to system components"""
        try:
            # Update system status
            self.current_status.is_paused = True
            self.current_status.pause_level = max(
                self.current_status.pause_level, 
                pause_event.pause_level,
                key=lambda x: self._get_pause_level_severity(x)
            )
            self.current_status.paused_components.update(pause_event.components)
            self.current_status.active_events.append(pause_event.event_id)
            self.current_status.last_pause_at = pause_event.triggered_at
            
            # Update component operational status
            for component in pause_event.components:
                self.current_status.can_operate[component] = False
                await self._pause_component(component, pause_event)
            
            # Handle full system pause
            if pause_event.pause_level in [PauseLevel.FULL, PauseLevel.CRITICAL]:
                for component in SystemComponent:
                    self.current_status.can_operate[component] = False
                    await self._pause_component(component, pause_event)
            
            self.logger.warning(f"Pause applied to components: {pause_event.components}")
            
        except Exception as e:
            self.logger.error(f"Pause application failed: {e}")
            raise
    
    def _get_pause_level_severity(self, level: PauseLevel) -> int:
        """Get numeric severity for pause level comparison"""
        severity_map = {
            PauseLevel.NONE: 0,
            PauseLevel.PARTIAL: 1,
            PauseLevel.FULL: 2,
            PauseLevel.CRITICAL: 3
        }
        return severity_map[level]
    
    async def _pause_component(self, component: SystemComponent, pause_event: PauseEvent):
        """Pause specific system component"""
        try:
            self.logger.warning(f"Pausing component: {component.value}")
            
            if component == SystemComponent.PAYMENTS:
                await self._pause_payment_processing()
            elif component == SystemComponent.NFT_MINTING:
                await self._pause_nft_operations()
            elif component == SystemComponent.MARKETPLACE:
                await self._pause_marketplace_operations()
            elif component == SystemComponent.WITHDRAWALS:
                await self._pause_withdrawal_processing()
            elif component == SystemComponent.ORACLES:
                await self._pause_oracle_feeds()
            # Add more component-specific pause logic as needed
            
        except Exception as e:
            self.logger.error(f"Component pause failed for {component.value}: {e}")
    
    async def _pause_payment_processing(self):
        """Pause payment processing operations"""
        # Mock implementation - in real system would interact with payment processors
        self.logger.warning("Payment processing paused")
    
    async def _pause_nft_operations(self):
        """Pause NFT minting and trading operations"""
        # Mock implementation - in real system would pause NFT contracts
        self.logger.warning("NFT operations paused")
    
    async def _pause_marketplace_operations(self):
        """Pause marketplace trading operations"""
        # Mock implementation - in real system would pause marketplace contracts
        self.logger.warning("Marketplace operations paused")
    
    async def _pause_withdrawal_processing(self):
        """Pause withdrawal operations"""
        # Mock implementation - in real system would pause withdrawal contracts
        self.logger.warning("Withdrawal processing paused")
    
    async def _pause_oracle_feeds(self):
        """Pause oracle data feeds"""
        # Mock implementation - in real system would pause oracle contracts
        self.logger.warning("Oracle feeds paused")
    
    def _generate_recovery_conditions(self, reason: PauseReason, level: PauseLevel) -> Dict[str, Any]:
        """Generate recovery conditions based on pause reason and level"""
        base_conditions = {
            "manual_approval_required": True,
            "min_approval_count": 2 if level in [PauseLevel.FULL, PauseLevel.CRITICAL] else 1,
            "security_audit_required": reason == PauseReason.SECURITY_BREACH,
            "system_health_check": True
        }
        
        # Reason-specific conditions
        if reason == PauseReason.SECURITY_BREACH:
            base_conditions.update({
                "security_audit_required": True,
                "vulnerability_patched": True,
                "incident_report_filed": True
            })
        elif reason == PauseReason.SMART_CONTRACT_BUG:
            base_conditions.update({
                "contract_fix_deployed": True,
                "fix_verification_complete": True
            })
        elif reason == PauseReason.ORACLE_FAILURE:
            base_conditions.update({
                "oracle_connectivity_restored": True,
                "data_integrity_verified": True
            })
        elif reason == PauseReason.NETWORK_CONGESTION:
            base_conditions.update({
                "network_congestion_resolved": True,
                "gas_prices_normalized": True
            })
        
        return base_conditions
    
    async def _notify_emergency_contacts(self, pause_event: PauseEvent):
        """Notify emergency contacts about pause event"""
        try:
            notification_data = {
                "event_id": pause_event.event_id,
                "pause_level": pause_event.pause_level.value,
                "reason": pause_event.reason.value,
                "components": [c.value for c in pause_event.components],
                "triggered_by": pause_event.triggered_by,
                "triggered_at": pause_event.triggered_at.isoformat(),
                "description": pause_event.description,
                "automatic": pause_event.automatic_trigger
            }
            
            # Mock notification - in real system would send actual alerts
            self.logger.critical(f"EMERGENCY NOTIFICATION: {json.dumps(notification_data, indent=2)}")
            
            for contact in self.emergency_contacts:
                # Send notification to contact
                self.logger.critical(f"Notifying emergency contact: {contact}")
            
        except Exception as e:
            self.logger.error(f"Emergency notification failed: {e}")
    
    async def check_component_status(self, component: SystemComponent) -> Dict[str, Any]:
        """Check if a component is operational"""
        is_operational = self.current_status.can_operate.get(component, True)
        
        pause_reasons = []
        blocking_events = []
        
        if not is_operational:
            for event_id in self.current_status.active_events:
                if event_id in self.pause_events:
                    event = self.pause_events[event_id]
                    if component in event.components or event.pause_level in [PauseLevel.FULL, PauseLevel.CRITICAL]:
                        pause_reasons.append(event.reason.value)
                        blocking_events.append(event_id)
        
        return {
            "component": component.value,
            "is_operational": is_operational,
            "pause_reasons": pause_reasons,
            "blocking_events": blocking_events,
            "system_pause_level": self.current_status.pause_level.value,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    async def attempt_recovery(
        self,
        event_id: str,
        recovery_data: Dict[str, Any],
        approver_address: str
    ) -> Dict[str, Any]:
        """Attempt to recover from emergency pause"""
        try:
            if event_id not in self.pause_events:
                raise ValueError(f"Pause event not found: {event_id}")
            
            pause_event = self.pause_events[event_id]
            
            # Validate authorization
            if approver_address not in self.authorized_pausers:
                raise ValueError(f"Unauthorized recovery request from: {approver_address}")
            
            self.logger.info(f"Attempting recovery for pause event: {event_id}")
            
            # Check recovery conditions
            conditions_met = await self._check_recovery_conditions(
                pause_event, recovery_data
            )
            
            if not conditions_met["all_met"]:
                return {
                    "recovery_approved": False,
                    "event_id": event_id,
                    "unmet_conditions": conditions_met["unmet_conditions"],
                    "recovery_progress": conditions_met["progress_percentage"]
                }
            
            # Perform recovery
            recovery_result = await self._perform_recovery(pause_event, approver_address)
            
            result = {
                "recovery_approved": True,
                "event_id": event_id,
                "approver": approver_address,
                "recovered_components": [c.value for c in pause_event.components],
                "recovery_result": recovery_result,
                "recovered_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Recovery completed for pause event: {event_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            raise
    
    async def _check_recovery_conditions(
        self,
        pause_event: PauseEvent,
        recovery_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check if recovery conditions are met"""
        conditions = pause_event.recovery_conditions
        met_conditions = []
        unmet_conditions = []
        
        for condition, required in conditions.items():
            if condition in recovery_data:
                if recovery_data[condition] == required:
                    met_conditions.append(condition)
                else:
                    unmet_conditions.append(condition)
            else:
                unmet_conditions.append(condition)
        
        total_conditions = len(conditions)
        met_count = len(met_conditions)
        progress_percentage = (met_count / total_conditions) * 100 if total_conditions > 0 else 100
        
        return {
            "all_met": len(unmet_conditions) == 0,
            "met_conditions": met_conditions,
            "unmet_conditions": unmet_conditions,
            "progress_percentage": progress_percentage
        }
    
    async def _perform_recovery(self, pause_event: PauseEvent, approver: str) -> Dict[str, Any]:
        """Perform the actual recovery process"""
        try:
            recovered_components = []
            
            # Resume paused components
            for component in pause_event.components:
                await self._resume_component(component)
                recovered_components.append(component.value)
                
                # Update operational status
                if component not in self._get_components_paused_by_other_events(pause_event.event_id):
                    self.current_status.can_operate[component] = True
            
            # Remove from active events
            if pause_event.event_id in self.current_status.active_events:
                self.current_status.active_events.remove(pause_event.event_id)
            
            # Update pause status if no active events
            if not self.current_status.active_events:
                self.current_status.is_paused = False
                self.current_status.pause_level = PauseLevel.NONE
                self.current_status.paused_components.clear()
            else:
                # Recalculate pause level based on remaining events
                self._recalculate_pause_status()
            
            # Calculate total pause duration
            pause_duration = datetime.utcnow() - pause_event.triggered_at
            self.current_status.total_pause_duration += pause_duration
            
            return {
                "recovered_components": recovered_components,
                "pause_duration": str(pause_duration),
                "approver": approver,
                "remaining_active_events": len(self.current_status.active_events)
            }
            
        except Exception as e:
            self.logger.error(f"Recovery execution failed: {e}")
            raise
    
    def _get_components_paused_by_other_events(self, exclude_event_id: str) -> Set[SystemComponent]:
        """Get components that are still paused by other active events"""
        paused_components = set()
        
        for event_id in self.current_status.active_events:
            if event_id != exclude_event_id and event_id in self.pause_events:
                event = self.pause_events[event_id]
                paused_components.update(event.components)
        
        return paused_components
    
    def _recalculate_pause_status(self):
        """Recalculate pause status based on active events"""
        if not self.current_status.active_events:
            self.current_status.pause_level = PauseLevel.NONE
            return
        
        max_level = PauseLevel.NONE
        all_paused_components = set()
        
        for event_id in self.current_status.active_events:
            if event_id in self.pause_events:
                event = self.pause_events[event_id]
                if self._get_pause_level_severity(event.pause_level) > self._get_pause_level_severity(max_level):
                    max_level = event.pause_level
                all_paused_components.update(event.components)
        
        self.current_status.pause_level = max_level
        self.current_status.paused_components = all_paused_components
    
    async def _resume_component(self, component: SystemComponent):
        """Resume specific system component"""
        try:
            self.logger.info(f"Resuming component: {component.value}")
            
            if component == SystemComponent.PAYMENTS:
                await self._resume_payment_processing()
            elif component == SystemComponent.NFT_MINTING:
                await self._resume_nft_operations()
            elif component == SystemComponent.MARKETPLACE:
                await self._resume_marketplace_operations()
            elif component == SystemComponent.WITHDRAWALS:
                await self._resume_withdrawal_processing()
            elif component == SystemComponent.ORACLES:
                await self._resume_oracle_feeds()
            
        except Exception as e:
            self.logger.error(f"Component resume failed for {component.value}: {e}")
    
    async def _resume_payment_processing(self):
        """Resume payment processing operations"""
        self.logger.info("Payment processing resumed")
    
    async def _resume_nft_operations(self):
        """Resume NFT operations"""
        self.logger.info("NFT operations resumed")
    
    async def _resume_marketplace_operations(self):
        """Resume marketplace operations"""
        self.logger.info("Marketplace operations resumed")
    
    async def _resume_withdrawal_processing(self):
        """Resume withdrawal processing"""
        self.logger.info("Withdrawal processing resumed")
    
    async def _resume_oracle_feeds(self):
        """Resume oracle feeds"""
        self.logger.info("Oracle feeds resumed")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        component_status = {}
        for component in SystemComponent:
            component_status[component.value] = self.current_status.can_operate.get(component, True)
        
        active_events_info = []
        for event_id in self.current_status.active_events:
            if event_id in self.pause_events:
                event = self.pause_events[event_id]
                active_events_info.append({
                    "event_id": event_id,
                    "reason": event.reason.value,
                    "level": event.pause_level.value,
                    "triggered_at": event.triggered_at.isoformat(),
                    "triggered_by": event.triggered_by
                })
        
        return {
            "is_paused": self.current_status.is_paused,
            "pause_level": self.current_status.pause_level.value,
            "paused_components": [c.value for c in self.current_status.paused_components],
            "component_status": component_status,
            "active_events": active_events_info,
            "total_events_in_history": len(self.pause_history),
            "last_pause_at": self.current_status.last_pause_at.isoformat() if self.current_status.last_pause_at else None,
            "total_pause_duration": str(self.current_status.total_pause_duration),
            "status_checked_at": datetime.utcnow().isoformat()
        }


class PauseManager:
    """High-level manager for emergency pause operations"""
    
    def __init__(self, emergency_pause: EmergencyPause):
        self.emergency_pause = emergency_pause
        self.logger = logging.getLogger(__name__)
    
    async def security_emergency_pause(
        self,
        triggered_by: str,
        description: str
    ) -> PauseEvent:
        """Trigger security emergency pause"""
        return await self.emergency_pause.trigger_pause(
            PauseLevel.CRITICAL,
            PauseReason.SECURITY_BREACH,
            [SystemComponent.ALL_OPERATIONS],
            triggered_by,
            f"Security Emergency: {description}",
            automatic=False
        )
    
    async def maintenance_pause(
        self,
        components: List[SystemComponent],
        triggered_by: str,
        duration_hours: int
    ) -> PauseEvent:
        """Trigger maintenance pause for specific components"""
        return await self.emergency_pause.trigger_pause(
            PauseLevel.PARTIAL,
            PauseReason.MAINTENANCE,
            components,
            triggered_by,
            "Scheduled maintenance",
            automatic=False,
            estimated_duration=duration_hours
        )