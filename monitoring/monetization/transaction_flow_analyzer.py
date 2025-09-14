"""
Ainflue Platform - Transaction Flow Analyzer
===========================================

Advanced transaction flow analysis system for the Ainflue platform.
Provides real-time monitoring, pattern analysis, and optimization insights
for payment transactions and revenue flows across all monetization channels.

Features:
- Real-time transaction flow monitoring
- Payment funnel analysis
- Conversion optimization tracking
- Revenue flow visualization
- Bottleneck detection and resolution
- Performance analytics

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
import json
import statistics
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import math
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionStage(Enum):
    """Transaction flow stages."""
    INITIATED = "initiated"
    AUTHORIZATION = "authorization"
    AUTHENTICATION = "authentication"
    PROCESSING = "processing"
    GATEWAY_SUBMISSION = "gateway_submission"
    BANK_PROCESSING = "bank_processing"
    SETTLEMENT = "settlement"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FlowType(Enum):
    """Types of transaction flows."""
    SUBSCRIPTION_PAYMENT = "subscription_payment"
    ONE_TIME_PURCHASE = "one_time_purchase"
    UPGRADE_PAYMENT = "upgrade_payment"
    RENEWAL_PAYMENT = "renewal_payment"
    REFUND_PROCESSING = "refund_processing"
    CHARGEBACK_PROCESSING = "chargeback_processing"
    PAYOUT_PROCESSING = "payout_processing"

class BottleneckType(Enum):
    """Types of flow bottlenecks."""
    AUTHORIZATION_DELAYS = "authorization_delays"
    GATEWAY_TIMEOUTS = "gateway_timeouts"
    AUTHENTICATION_FAILURES = "authentication_failures"
    PROCESSING_ERRORS = "processing_errors"
    NETWORK_LATENCY = "network_latency"
    FRAUD_CHECKS = "fraud_checks"
    COMPLIANCE_DELAYS = "compliance_delays"

@dataclass
class TransactionFlowEvent:
    """Individual transaction flow event."""
    event_id: str
    transaction_id: str
    stage: TransactionStage
    timestamp: datetime
    duration_ms: Optional[int] = None
    status: str = "success"  # success, failure, pending
    gateway: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TransactionFlow:
    """Complete transaction flow record."""
    flow_id: str
    transaction_id: str
    customer_id: str
    flow_type: FlowType
    amount: float
    currency: str
    events: List[TransactionFlowEvent] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_duration_ms: Optional[int] = None
    final_status: str = "pending"
    conversion_funnel_stage: str = "initiated"
    optimization_opportunities: List[str] = field(default_factory=list)

@dataclass
class FlowBottleneck:
    """Identified bottleneck in transaction flow."""
    bottleneck_id: str
    bottleneck_type: BottleneckType
    stage: TransactionStage
    impact_score: float  # 0.0 to 1.0
    affected_transactions: int
    average_delay_ms: int
    description: str
    recommended_actions: List[str]
    detected_at: datetime = field(default_factory=datetime.now)

@dataclass
class FlowMetrics:
    """Transaction flow performance metrics."""
    total_flows: int = 0
    completed_flows: int = 0
    failed_flows: int = 0
    average_completion_time_ms: float = 0.0
    success_rate: float = 0.0
    conversion_rate: float = 0.0
    throughput_per_minute: float = 0.0
    bottlenecks_detected: int = 0
    optimization_score: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

class TransactionFlowAnalyzer:
    """
    Advanced transaction flow analyzer for the Ainflue platform.
    
    Monitors transaction flows in real-time, identifies bottlenecks,
    analyzes conversion funnels, and provides optimization recommendations.
    """
    
    def __init__(self) -> None:
        """Initialize the transaction flow analyzer."""
        self.active_flows: Dict[str, TransactionFlow] = {}
        self.completed_flows: List[TransactionFlow] = []
        self.flow_bottlenecks: List[FlowBottleneck] = []
        self.flow_metrics = FlowMetrics()
        self.stage_performance: Dict[TransactionStage, Dict[str, float]] = {}
        self.gateway_performance: Dict[str, Dict[str, Any]] = {}
        self.conversion_funnels: Dict[FlowType, Dict[str, float]] = {}
        self.optimization_rules: List[Dict[str, Any]] = []
        
        logger.info("Initializing Transaction Flow Analyzer")
        self._initialize_stage_tracking()
        self._setup_optimization_rules()
    
    def _initialize_stage_tracking(self) -> None:
        """Initialize performance tracking for each stage."""
        for stage in TransactionStage:
            self.stage_performance[stage] = {
                "average_duration_ms": 0.0,
                "success_rate": 0.0,
                "throughput": 0.0,
                "error_rate": 0.0,
                "bottleneck_score": 0.0
            }
    
    def _setup_optimization_rules(self) -> None:
        """Setup transaction flow optimization rules."""
        self.optimization_rules = [
            {
                "rule_id": "auth_timeout_001",
                "name": "Authorization Timeout Optimization",
                "description": "Optimize authorization timeouts to reduce abandonment",
                "conditions": {
                    "stage": TransactionStage.AUTHORIZATION,
                    "duration_threshold_ms": 5000,
                    "failure_rate_threshold": 0.1
                },
                "recommendations": [
                    "Implement fallback authorization methods",
                    "Optimize timeout configuration",
                    "Add retry logic with exponential backoff"
                ]
            },
            {
                "rule_id": "gateway_selection_002",
                "name": "Gateway Performance Optimization",
                "description": "Route transactions to best-performing gateways",
                "conditions": {
                    "gateway_success_rate_threshold": 0.95,
                    "average_processing_time_threshold": 3000
                },
                "recommendations": [
                    "Implement intelligent gateway routing",
                    "Load balance across multiple gateways",
                    "Monitor gateway SLA compliance"
                ]
            },
            {
                "rule_id": "fraud_check_003",
                "name": "Fraud Check Optimization",
                "description": "Balance fraud prevention with user experience",
                "conditions": {
                    "fraud_check_duration_threshold": 2000,
                    "false_positive_rate_threshold": 0.05
                },
                "recommendations": [
                    "Implement parallel fraud checks",
                    "Use ML for faster risk assessment",
                    "Optimize fraud rules and thresholds"
                ]
            },
            {
                "rule_id": "mobile_optimization_004",
                "name": "Mobile Transaction Optimization",
                "description": "Optimize flows for mobile devices",
                "conditions": {
                    "mobile_conversion_rate_threshold": 0.8,
                    "mobile_abandonment_rate_threshold": 0.3
                },
                "recommendations": [
                    "Simplify mobile checkout flow",
                    "Implement one-click payments",
                    "Optimize for touch interfaces"
                ]
            }
        ]
    
    def start_transaction_flow(
        self,
        transaction_id: str,
        customer_id: str,
        flow_type: FlowType,
        amount: float,
        currency: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start tracking a new transaction flow."""
        
        flow_id = f"flow_{uuid.uuid4().hex[:8]}"
        
        flow = TransactionFlow(
            flow_id=flow_id,
            transaction_id=transaction_id,
            customer_id=customer_id,
            flow_type=flow_type,
            amount=amount,
            currency=currency,
            started_at=datetime.now()
        )
        
        # Create initial event
        initial_event = TransactionFlowEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            transaction_id=transaction_id,
            stage=TransactionStage.INITIATED,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        flow.events.append(initial_event)
        self.active_flows[flow_id] = flow
        
        logger.info(f"Started transaction flow {flow_id} for transaction {transaction_id}")
        return flow_id
    
    def add_flow_event(
        self,
        flow_id: str,
        stage: TransactionStage,
        status: str = "success",
        duration_ms: Optional[int] = None,
        gateway: Optional[str] = None,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add an event to an existing transaction flow."""
        
        if flow_id not in self.active_flows:
            logger.error(f"Flow {flow_id} not found")
            return False
        
        flow = self.active_flows[flow_id]
        
        event = TransactionFlowEvent(
            event_id=f"evt_{uuid.uuid4().hex[:8]}",
            transaction_id=flow.transaction_id,
            stage=stage,
            timestamp=datetime.now(),
            duration_ms=duration_ms,
            status=status,
            gateway=gateway,
            error_code=error_code,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        flow.events.append(event)
        
        # Update flow status if this is a terminal stage
        if stage in [TransactionStage.COMPLETED, TransactionStage.FAILED, TransactionStage.CANCELLED]:
            self._complete_flow(flow_id, stage, status)
        
        # Update stage performance metrics
        self._update_stage_metrics(stage, duration_ms, status)
        
        # Update gateway performance if applicable
        if gateway:
            self._update_gateway_metrics(gateway, stage, duration_ms, status)
        
        logger.debug(f"Added {stage.value} event to flow {flow_id}")
        return True
    
    def _complete_flow(self, flow_id -> None: str, final_stage -> None: TransactionStage, final_status -> None: str) -> None:
        """Complete a transaction flow."""
        
        flow = self.active_flows[flow_id]
        flow.completed_at = datetime.now()
        flow.final_status = final_status
        
        # Calculate total duration
        if flow.started_at:
            flow.total_duration_ms = int((flow.completed_at - flow.started_at).total_seconds() * 1000)
        
        # Analyze conversion funnel
        flow.conversion_funnel_stage = self._determine_funnel_stage(flow)
        
        # Identify optimization opportunities
        flow.optimization_opportunities = self._identify_optimization_opportunities(flow)
        
        # Move to completed flows
        self.completed_flows.append(flow)
        del self.active_flows[flow_id]
        
        # Update overall metrics
        self._update_flow_metrics()
        
        # Check for bottlenecks
        self._check_for_bottlenecks(flow)
        
        logger.info(f"Completed flow {flow_id}: {final_status} in {flow.total_duration_ms}ms")
    
    def _update_stage_metrics(self, stage -> None: TransactionStage, duration_ms -> None: Optional[int], status -> None: str) -> None:
        """Update performance metrics for a specific stage."""
        
        stage_metrics = self.stage_performance[stage]
        
        # Update duration if provided
        if duration_ms is not None:
            # Simple moving average (in production, would use more sophisticated aggregation)
            current_avg = stage_metrics["average_duration_ms"]
            stage_metrics["average_duration_ms"] = (current_avg * 0.9) + (duration_ms * 0.1)
        
        # Update success rate
        if status == "success":
            stage_metrics["success_rate"] = min(1.0, stage_metrics["success_rate"] + 0.001)
        else:
            stage_metrics["success_rate"] = max(0.0, stage_metrics["success_rate"] - 0.001)
        
        # Update error rate
        stage_metrics["error_rate"] = 1.0 - stage_metrics["success_rate"]
    
    def _update_gateway_metrics(self, gateway -> None: str, stage -> None: TransactionStage, duration_ms -> None: Optional[int], status -> None: str) -> None:
        """Update performance metrics for a specific gateway."""
        
        if gateway not in self.gateway_performance:
            self.gateway_performance[gateway] = {
                "total_transactions": 0,
                "successful_transactions": 0,
                "average_processing_time_ms": 0.0,
                "success_rate": 0.0,
                "uptime": 1.0,
                "last_updated": datetime.now()
            }
        
        gateway_metrics = self.gateway_performance[gateway]
        gateway_metrics["total_transactions"] += 1
        
        if status == "success":
            gateway_metrics["successful_transactions"] += 1
        
        # Update success rate
        gateway_metrics["success_rate"] = gateway_metrics["successful_transactions"] / gateway_metrics["total_transactions"]
        
        # Update processing time
        if duration_ms is not None:
            current_avg = gateway_metrics["average_processing_time_ms"]
            gateway_metrics["average_processing_time_ms"] = (current_avg * 0.9) + (duration_ms * 0.1)
        
        gateway_metrics["last_updated"] = datetime.now()
    
    def _determine_funnel_stage(self, flow: TransactionFlow) -> str:
        """Determine the furthest stage reached in the conversion funnel."""
        
        stages_reached = [event.stage for event in flow.events]
        
        # Define funnel progression
        funnel_stages = [
            TransactionStage.INITIATED,
            TransactionStage.AUTHORIZATION,
            TransactionStage.AUTHENTICATION,
            TransactionStage.PROCESSING,
            TransactionStage.GATEWAY_SUBMISSION,
            TransactionStage.BANK_PROCESSING,
            TransactionStage.SETTLEMENT,
            TransactionStage.COMPLETED
        ]
        
        furthest_stage = TransactionStage.INITIATED
        for stage in funnel_stages:
            if stage in stages_reached:
                furthest_stage = stage
            else:
                break
        
        return furthest_stage.value
    
    def _identify_optimization_opportunities(self, flow: TransactionFlow) -> List[str]:
        """Identify optimization opportunities for the completed flow."""
        
        opportunities = []
        
        # Check duration thresholds
        if flow.total_duration_ms and flow.total_duration_ms > 10000:  # > 10 seconds
            opportunities.append("Reduce overall transaction processing time")
        
        # Check for failed stages
        failed_events = [event for event in flow.events if event.status == "failure"]
        if failed_events:
            opportunities.append("Address failure points in transaction flow")
        
        # Check for authentication issues
        auth_events = [event for event in flow.events if event.stage == TransactionStage.AUTHENTICATION]
        if any(event.status != "success" for event in auth_events):
            opportunities.append("Improve authentication success rate")
        
        # Check gateway performance
        gateway_events = [event for event in flow.events if event.gateway]
        slow_gateways = [event for event in gateway_events if event.duration_ms and event.duration_ms > 5000]
        if slow_gateways:
            opportunities.append("Optimize gateway selection and routing")
        
        # Check mobile optimization
        if flow.events[0].metadata.get("device_type") == "mobile" and flow.final_status != "success":
            opportunities.append("Optimize mobile transaction experience")
        
        return opportunities
    
    def _update_flow_metrics(self) -> None:
        """Update overall flow performance metrics."""
        
        total_flows = len(self.completed_flows)
        if total_flows == 0:
            return
        
        # Calculate success metrics
        successful_flows = len([f for f in self.completed_flows if f.final_status == "success"])
        failed_flows = len([f for f in self.completed_flows if f.final_status in ["failure", "cancelled"]])
        
        self.flow_metrics.total_flows = total_flows
        self.flow_metrics.completed_flows = successful_flows
        self.flow_metrics.failed_flows = failed_flows
        self.flow_metrics.success_rate = successful_flows / total_flows if total_flows > 0 else 0.0
        
        # Calculate average completion time
        completed_with_duration = [f for f in self.completed_flows if f.total_duration_ms]
        if completed_with_duration:
            self.flow_metrics.average_completion_time_ms = statistics.mean([f.total_duration_ms for f in completed_with_duration])
        
        # Calculate conversion rate (initiated to completed)
        self.flow_metrics.conversion_rate = self.flow_metrics.success_rate
        
        # Calculate throughput (recent flows per minute)
        recent_flows = [f for f in self.completed_flows if f.completed_at and (datetime.now() - f.completed_at).total_seconds() <= 3600]
        self.flow_metrics.throughput_per_minute = len(recent_flows) / 60 if recent_flows else 0.0
        
        # Update optimization score
        self.flow_metrics.optimization_score = self._calculate_optimization_score()
        
        self.flow_metrics.last_updated = datetime.now()
    
    def _calculate_optimization_score(self) -> float:
        """Calculate overall flow optimization score."""
        
        factors = []
        
        # Success rate factor (40% weight)
        factors.append(("success_rate", self.flow_metrics.success_rate, 0.4))
        
        # Speed factor (30% weight)
        target_duration = 5000  # 5 seconds target
        if self.flow_metrics.average_completion_time_ms > 0:
            speed_score = max(0.0, 1.0 - (self.flow_metrics.average_completion_time_ms - target_duration) / target_duration)
        else:
            speed_score = 1.0
        factors.append(("speed", speed_score, 0.3))
        
        # Bottleneck factor (20% weight)
        active_bottlenecks = len([b for b in self.flow_bottlenecks if (datetime.now() - b.detected_at).hours <= 24])
        bottleneck_score = max(0.0, 1.0 - (active_bottlenecks * 0.1))
        factors.append(("bottlenecks", bottleneck_score, 0.2))
        
        # Throughput factor (10% weight)
        target_throughput = 10.0  # 10 transactions per minute
        throughput_score = min(1.0, self.flow_metrics.throughput_per_minute / target_throughput)
        factors.append(("throughput", throughput_score, 0.1))
        
        # Calculate weighted score
        total_weighted_score = sum(score * weight for _, score, weight in factors)
        return round(total_weighted_score, 3)
    
    def _check_for_bottlenecks(self, flow -> None: TransactionFlow) -> None:
        """Check for bottlenecks in the completed flow."""
        
        # Analyze each stage for potential bottlenecks
        for event in flow.events:
            if event.duration_ms and event.duration_ms > 5000:  # > 5 seconds
                # Check if this is a new bottleneck or existing one
                existing_bottleneck = self._find_existing_bottleneck(event.stage)
                
                if existing_bottleneck:
                    # Update existing bottleneck
                    existing_bottleneck.affected_transactions += 1
                    existing_bottleneck.average_delay_ms = int(
                        (existing_bottleneck.average_delay_ms + event.duration_ms) / 2
                    )
                else:
                    # Create new bottleneck
                    bottleneck = FlowBottleneck(
                        bottleneck_id=f"btn_{uuid.uuid4().hex[:8]}",
                        bottleneck_type=self._classify_bottleneck_type(event),
                        stage=event.stage,
                        impact_score=self._calculate_bottleneck_impact(event),
                        affected_transactions=1,
                        average_delay_ms=event.duration_ms,
                        description=f"Delays detected in {event.stage.value} stage",
                        recommended_actions=self._get_bottleneck_recommendations(event.stage)
                    )
                    self.flow_bottlenecks.append(bottleneck)
                    
                    logger.warning(f"New bottleneck detected: {bottleneck.bottleneck_type.value} in {event.stage.value}")
    
    def _find_existing_bottleneck(self, stage: TransactionStage) -> Optional[FlowBottleneck]:
        """Find existing bottleneck for the given stage."""
        
        for bottleneck in self.flow_bottlenecks:
            if bottleneck.stage == stage and (datetime.now() - bottleneck.detected_at).hours <= 24:
                return bottleneck
        return None
    
    def _classify_bottleneck_type(self, event: TransactionFlowEvent) -> BottleneckType:
        """Classify the type of bottleneck based on the event."""
        
        if event.stage == TransactionStage.AUTHORIZATION:
            return BottleneckType.AUTHORIZATION_DELAYS
        elif event.stage == TransactionStage.AUTHENTICATION:
            return BottleneckType.AUTHENTICATION_FAILURES
        elif event.stage == TransactionStage.GATEWAY_SUBMISSION:
            return BottleneckType.GATEWAY_TIMEOUTS
        elif event.stage == TransactionStage.PROCESSING:
            if "fraud" in str(event.metadata).lower():
                return BottleneckType.FRAUD_CHECKS
            elif "compliance" in str(event.metadata).lower():
                return BottleneckType.COMPLIANCE_DELAYS
            else:
                return BottleneckType.PROCESSING_ERRORS
        else:
            return BottleneckType.NETWORK_LATENCY
    
    def _calculate_bottleneck_impact(self, event: TransactionFlowEvent) -> float:
        """Calculate the impact score of a bottleneck."""
        
        # Impact based on duration
        duration_impact = min(1.0, event.duration_ms / 10000) if event.duration_ms else 0.5
        
        # Impact based on stage criticality
        stage_criticality = {
            TransactionStage.INITIATED: 0.1,
            TransactionStage.AUTHORIZATION: 0.8,
            TransactionStage.AUTHENTICATION: 0.7,
            TransactionStage.PROCESSING: 0.9,
            TransactionStage.GATEWAY_SUBMISSION: 0.8,
            TransactionStage.BANK_PROCESSING: 0.6,
            TransactionStage.SETTLEMENT: 0.4,
            TransactionStage.COMPLETED: 0.1
        }
        
        stage_impact = stage_criticality.get(event.stage, 0.5)
        
        # Combined impact score
        return (duration_impact * 0.6) + (stage_impact * 0.4)
    
    def _get_bottleneck_recommendations(self, stage: TransactionStage) -> List[str]:
        """Get recommendations for resolving bottlenecks in a specific stage."""
        
        recommendations = {
            TransactionStage.AUTHORIZATION: [
                "Implement faster authorization services",
                "Add authorization caching for repeat customers",
                "Use parallel authorization checks"
            ],
            TransactionStage.AUTHENTICATION: [
                "Optimize 2FA methods",
                "Implement biometric authentication",
                "Reduce authentication steps for trusted users"
            ],
            TransactionStage.PROCESSING: [
                "Scale processing infrastructure",
                "Implement asynchronous processing",
                "Optimize database queries"
            ],
            TransactionStage.GATEWAY_SUBMISSION: [
                "Implement gateway failover",
                "Optimize network connections",
                "Use faster gateway endpoints"
            ],
            TransactionStage.BANK_PROCESSING: [
                "Work with banks to optimize processing",
                "Implement batch processing for lower priority transactions",
                "Use multiple banking partners"
            ]
        }
        
        return recommendations.get(stage, ["Analyze stage performance and optimize accordingly"])
    
    def get_flow_analytics(
        self,
        flow_type: Optional[FlowType] = None,
        time_range_hours: int = 24
    ) -> Dict[str, Any]:
        """Get comprehensive flow analytics."""
        
        cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
        
        # Filter flows
        if flow_type:
            relevant_flows = [f for f in self.completed_flows if f.flow_type == flow_type and f.completed_at and f.completed_at > cutoff_time]
        else:
            relevant_flows = [f for f in self.completed_flows if f.completed_at and f.completed_at > cutoff_time]
        
        if not relevant_flows:
            return {"message": "No flows found for the specified criteria"}
        
        # Calculate analytics
        total_flows = len(relevant_flows)
        successful_flows = len([f for f in relevant_flows if f.final_status == "success"])
        failed_flows = len([f for f in relevant_flows if f.final_status in ["failure", "cancelled"]])
        
        # Duration analysis
        flows_with_duration = [f for f in relevant_flows if f.total_duration_ms]
        avg_duration = statistics.mean([f.total_duration_ms for f in flows_with_duration]) if flows_with_duration else 0
        
        # Conversion funnel analysis
        funnel_analysis = defaultdict(int)
        for flow in relevant_flows:
            funnel_analysis[flow.conversion_funnel_stage] += 1
        
        # Gateway performance
        gateway_analysis = defaultdict(lambda: {"total": 0, "successful": 0, "avg_duration": 0})
        for flow in relevant_flows:
            for event in flow.events:
                if event.gateway:
                    gateway_analysis[event.gateway]["total"] += 1
                    if event.status == "success":
                        gateway_analysis[event.gateway]["successful"] += 1
                    if event.duration_ms:
                        current_avg = gateway_analysis[event.gateway]["avg_duration"]
                        gateway_analysis[event.gateway]["avg_duration"] = (current_avg + event.duration_ms) / 2
        
        # Stage performance analysis
        stage_analysis = {}
        for stage in TransactionStage:
            stage_events = []
            for flow in relevant_flows:
                stage_events.extend([e for e in flow.events if e.stage == stage])
            
            if stage_events:
                successful_events = [e for e in stage_events if e.status == "success"]
                stage_analysis[stage.value] = {
                    "total_events": len(stage_events),
                    "successful_events": len(successful_events),
                    "success_rate": len(successful_events) / len(stage_events),
                    "avg_duration_ms": statistics.mean([e.duration_ms for e in stage_events if e.duration_ms]) if any(e.duration_ms for e in stage_events) else 0
                }
        
        return {
            "time_range_hours": time_range_hours,
            "flow_type": flow_type.value if flow_type else "all",
            "overview": {
                "total_flows": total_flows,
                "successful_flows": successful_flows,
                "failed_flows": failed_flows,
                "success_rate": round(successful_flows / total_flows, 3),
                "average_duration_ms": round(avg_duration, 2),
                "active_flows": len(self.active_flows)
            },
            "conversion_funnel": dict(funnel_analysis),
            "stage_performance": stage_analysis,
            "gateway_performance": {
                gateway: {
                    "success_rate": round(data["successful"] / data["total"], 3) if data["total"] > 0 else 0,
                    "average_duration_ms": round(data["avg_duration"], 2),
                    "total_transactions": data["total"]
                }
                for gateway, data in gateway_analysis.items()
            },
            "bottlenecks": [
                {
                    "type": b.bottleneck_type.value,
                    "stage": b.stage.value,
                    "impact_score": round(b.impact_score, 3),
                    "affected_transactions": b.affected_transactions,
                    "average_delay_ms": b.average_delay_ms
                }
                for b in self.flow_bottlenecks if (datetime.now() - b.detected_at).hours <= time_range_hours
            ],
            "optimization_opportunities": self._get_flow_optimization_opportunities(relevant_flows),
            "analyzed_at": datetime.now().isoformat()
        }
    
    def _get_flow_optimization_opportunities(self, flows: List[TransactionFlow]) -> List[Dict[str, Any]]:
        """Get optimization opportunities based on flow analysis."""
        
        opportunities = []
        
        # Analyze success rates by stage
        stage_success_rates = {}
        for stage in TransactionStage:
            stage_events = []
            for flow in flows:
                stage_events.extend([e for e in flow.events if e.stage == stage])
            
            if stage_events:
                successful_events = len([e for e in stage_events if e.status == "success"])
                stage_success_rates[stage] = successful_events / len(stage_events)
        
        # Identify stages with low success rates
        for stage, success_rate in stage_success_rates.items():
            if success_rate < 0.9:
                opportunities.append({
                    "type": "success_rate_improvement",
                    "stage": stage.value,
                    "current_success_rate": round(success_rate, 3),
                    "impact": "high" if success_rate < 0.8 else "medium",
                    "recommendation": f"Improve {stage.value} success rate from {success_rate:.1%} to >90%"
                })
        
        # Analyze duration outliers
        durations = [f.total_duration_ms for f in flows if f.total_duration_ms]
        if durations:
            avg_duration = statistics.mean(durations)
            if avg_duration > 8000:  # > 8 seconds
                opportunities.append({
                    "type": "duration_optimization",
                    "current_avg_duration_ms": round(avg_duration, 2),
                    "target_duration_ms": 5000,
                    "impact": "high",
                    "recommendation": "Reduce average transaction time to under 5 seconds"
                })
        
        # Gateway optimization
        gateway_performance = {}
        for flow in flows:
            for event in flow.events:
                if event.gateway:
                    if event.gateway not in gateway_performance:
                        gateway_performance[event.gateway] = {"total": 0, "successful": 0}
                    gateway_performance[event.gateway]["total"] += 1
                    if event.status == "success":
                        gateway_performance[event.gateway]["successful"] += 1
        
        for gateway, perf in gateway_performance.items():
            success_rate = perf["successful"] / perf["total"] if perf["total"] > 0 else 0
            if success_rate < 0.95:
                opportunities.append({
                    "type": "gateway_optimization",
                    "gateway": gateway,
                    "success_rate": round(success_rate, 3),
                    "impact": "medium",
                    "recommendation": f"Improve {gateway} gateway performance or consider alternatives"
                })
        
        return opportunities[:10]  # Return top 10 opportunities
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time transaction flow dashboard."""
        
        # Recent activity (last hour)
        recent_flows = [f for f in self.completed_flows if f.completed_at and (datetime.now() - f.completed_at).total_seconds() <= 3600]
        active_flows_count = len(self.active_flows)
        
        # Performance metrics
        recent_success_rate = len([f for f in recent_flows if f.final_status == "success"]) / len(recent_flows) if recent_flows else 0
        
        # Current bottlenecks
        active_bottlenecks = [b for b in self.flow_bottlenecks if (datetime.now() - b.detected_at).hours <= 1]
        
        return {
            "real_time_status": {
                "active_flows": active_flows_count,
                "completed_last_hour": len(recent_flows),
                "success_rate_last_hour": round(recent_success_rate, 3),
                "active_bottlenecks": len(active_bottlenecks),
                "current_throughput_per_minute": round(len(recent_flows) / 60, 2)
            },
            "overall_metrics": {
                "total_flows_processed": self.flow_metrics.total_flows,
                "overall_success_rate": round(self.flow_metrics.success_rate, 3),
                "average_completion_time_ms": round(self.flow_metrics.average_completion_time_ms, 2),
                "optimization_score": round(self.flow_metrics.optimization_score, 3)
            },
            "stage_health": {
                stage.value: {
                    "success_rate": round(metrics["success_rate"], 3),
                    "avg_duration_ms": round(metrics["average_duration_ms"], 2),
                    "status": "healthy" if metrics["success_rate"] > 0.95 else "warning" if metrics["success_rate"] > 0.9 else "critical"
                }
                for stage, metrics in self.stage_performance.items()
            },
            "gateway_status": {
                gateway: {
                    "success_rate": round(metrics["success_rate"], 3),
                    "avg_processing_time_ms": round(metrics["average_processing_time_ms"], 2),
                    "status": "operational" if metrics["success_rate"] > 0.95 else "degraded" if metrics["success_rate"] > 0.9 else "issues"
                }
                for gateway, metrics in self.gateway_performance.items()
            },
            "recent_bottlenecks": [
                {
                    "type": b.bottleneck_type.value,
                    "stage": b.stage.value,
                    "impact_score": round(b.impact_score, 3),
                    "detected_at": b.detected_at.isoformat()
                }
                for b in active_bottlenecks
            ],
            "recommendations": self._get_real_time_recommendations(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _get_real_time_recommendations(self) -> List[str]:
        """Get real-time optimization recommendations."""
        
        recommendations = []
        
        # Based on success rate
        if self.flow_metrics.success_rate < 0.95:
            recommendations.append("Investigate and address transaction failure causes")
        
        # Based on duration
        if self.flow_metrics.average_completion_time_ms > 8000:
            recommendations.append("Optimize transaction processing speed")
        
        # Based on active bottlenecks
        active_bottlenecks = [b for b in self.flow_bottlenecks if (datetime.now() - b.detected_at).hours <= 24]
        if len(active_bottlenecks) > 3:
            recommendations.append("Address multiple bottlenecks affecting transaction flow")
        
        # Based on gateway performance
        poor_gateways = [g for g, m in self.gateway_performance.items() if m["success_rate"] < 0.95]
        if poor_gateways:
            recommendations.append(f"Review and optimize gateway performance: {', '.join(poor_gateways[:3])}")
        
        return recommendations[:5]

# Initialize the global transaction flow analyzer
transaction_flow_analyzer = TransactionFlowAnalyzer()

def create_flow_analyzer_config() -> Dict[str, Any]:
    """Create default configuration for transaction flow analysis."""
    return {
        "supported_flow_types": [flow_type.value for flow_type in FlowType],
        "tracked_stages": [stage.value for stage in TransactionStage],
        "optimization_rules": len(transaction_flow_analyzer.optimization_rules),
        "real_time_monitoring": True,
        "bottleneck_detection": True,
        "performance_targets": {
            "success_rate": 0.95,
            "average_duration_ms": 5000,
            "throughput_per_minute": 10
        }
    }

# Export main components
__all__ = [
    'TransactionFlowAnalyzer',
    'TransactionStage',
    'FlowType',
    'BottleneckType',
    'TransactionFlowEvent',
    'TransactionFlow',
    'FlowBottleneck',
    'transaction_flow_analyzer',
    'create_flow_analyzer_config'
]