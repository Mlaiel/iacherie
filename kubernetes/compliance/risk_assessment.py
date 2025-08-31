"""
IA Influencer Agent - Risk Assessment Engine
Comprehensive compliance and operational risk assessment system

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import HTTPException

from backend.core.database import get_db_session
from backend.core.config import settings
from backend.models.risk import RiskAssessment, RiskMitigation, RiskIncident
from backend.models.audit import AuditLog
from backend.utils.ml_risk_scoring import calculate_risk_score, predict_risk_trends
from backend.core.logging import get_logger
from .audit_logger import AuditLogger, AuditCategory, AuditLevel, ComplianceFramework
from .compliance_monitor import ComplianceMonitor

logger = get_logger(__name__)


class RiskCategory(str, Enum):
    """Risk assessment categories"""
    OPERATIONAL = "operational"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    STRATEGIC = "strategic"
    LEGAL = "legal"
    TECHNICAL = "technical"


class RiskLevel(str, Enum):
    """Risk severity levels"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    CRITICAL = "critical"


class RiskStatus(str, Enum):
    """Risk status states"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    TRANSFERRED = "transferred"
    AVOIDED = "avoided"
    MONITORING = "monitoring"
    CLOSED = "closed"


class MitigationStrategy(str, Enum):
    """Risk mitigation strategies"""
    AVOID = "avoid"
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    ACCEPT = "accept"
    MONITOR = "monitor"


@dataclass
class RiskFactor:
    """Individual risk factor definition"""
    factor_id: str
    name: str
    description: str
    category: RiskCategory
    likelihood: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    detection_difficulty: float  # 0.0 to 1.0
    time_horizon: int  # days
    data_sources: List[str]
    indicators: List[str]
    dependencies: List[str]


@dataclass
class RiskScenario:
    """Risk scenario modeling"""
    scenario_id: str
    name: str
    description: str
    risk_factors: List[str]
    probability: float
    potential_impact: Dict[str, float]
    timeline: str
    triggers: List[str]
    early_warning_signs: List[str]
    cascading_effects: List[str]


@dataclass
class ComprehensiveRiskAssessment:
    """Complete risk assessment result"""
    assessment_id: str
    assessment_date: datetime
    scope: str
    methodology: str
    risk_appetite: Dict[str, float]
    identified_risks: List[Dict[str, Any]]
    risk_scenarios: List[RiskScenario]
    overall_risk_score: float
    risk_distribution: Dict[RiskCategory, float]
    heat_map: Dict[str, Dict[str, float]]
    top_risks: List[Dict[str, Any]]
    mitigation_recommendations: List[Dict[str, Any]]
    residual_risk: float
    assessment_confidence: float
    next_review_date: datetime
    assessor: str


@dataclass
class RiskMitigationPlan:
    """Risk mitigation action plan"""
    plan_id: str
    risk_id: str
    strategy: MitigationStrategy
    actions: List[Dict[str, Any]]
    responsible_parties: List[str]
    timeline: Dict[str, datetime]
    budget_required: float
    success_metrics: List[str]
    monitoring_frequency: str
    review_dates: List[datetime]
    status: str


class RiskAssessmentEngine:
    """Comprehensive risk assessment and management system"""
    
    def __init__(self):
        self.logger = logger
        self.audit_logger = AuditLogger()
        self.compliance_monitor = ComplianceMonitor()
        self.automated_assessment = settings.AUTOMATED_RISK_ASSESSMENT
        self.ml_risk_scoring = settings.ML_RISK_SCORING_ENABLED
        self.risk_monitoring_interval = settings.RISK_MONITORING_INTERVAL
        
        # Risk assessment frameworks
        self.risk_frameworks = {
            "ISO31000": "ISO 31000:2018 Risk Management",
            "COSO": "COSO Enterprise Risk Management",
            "NIST": "NIST Risk Management Framework",
            "FAIR": "Factor Analysis of Information Risk"
        }
        
        # Risk factors library
        self.risk_factors = self._load_risk_factors()
        
        # Risk scenarios library  
        self.risk_scenarios = self._load_risk_scenarios()
        
        # Risk appetite definitions
        self.risk_appetite = self._define_risk_appetite()
        
        # Active monitoring tasks
        self._monitoring_tasks: Set[asyncio.Task] = set()
        self._monitoring_active = False
    
    async def start_risk_monitoring(self) -> None:
        """Start continuous risk monitoring"""



        try:
            if self._monitoring_active:
                self.logger.warning("Risk monitoring already active")
                return
            
            self._monitoring_active = True
            
            # Start continuous risk assessment task
            assessment_task = asyncio.create_task(self._continuous_risk_assessment())
            self._monitoring_tasks.add(assessment_task)
            
            # Start risk indicator monitoring
            indicator_task = asyncio.create_task(self._monitor_risk_indicators())
            self._monitoring_tasks.add(indicator_task)
            
            # Start mitigation tracking
            mitigation_task = asyncio.create_task(self._track_mitigation_progress())
            self._monitoring_tasks.add(mitigation_task)
            
            self.logger.info("Risk monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start risk monitoring: {str(e)}")
            raise
    
    async def stop_risk_monitoring(self) -> None:
        """Stop risk monitoring"""



        try:
            self._monitoring_active = False
            
            # Cancel all monitoring tasks
            for task in self._monitoring_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)
            self._monitoring_tasks.clear()
            
            self.logger.info("Risk monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping risk monitoring: {str(e)}")
    
    async def conduct_comprehensive_risk_assessment(
        self,
        scope: str,
        framework: str = "ISO31000",
        assessment_type: str = "full",
        assessor: str = "system"
    ) -> ComprehensiveRiskAssessment:
        """Conduct comprehensive enterprise risk assessment"""



        try:
            # Generate assessment ID
            assessment_id = f"RA-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Collect risk data
            risk_data = await self._collect_risk_assessment_data(scope)
            
            # Identify and assess risks
            identified_risks = await self._identify_risks(risk_data, scope)
            
            # Evaluate risk scenarios
            scenario_assessments = await self._evaluate_risk_scenarios(identified_risks, risk_data)
            
            # Calculate overall risk scores
            risk_scores = await self._calculate_risk_scores(identified_risks, scenario_assessments)
            
            # Generate risk distribution and heat map
            risk_distribution = self._calculate_risk_distribution(identified_risks)
            heat_map = self._generate_risk_heat_map(identified_risks)
            
            # Identify top risks
            top_risks = sorted(
                identified_risks,
                key=lambda r: r["risk_score"],
                reverse=True
            )[:10]
            
            # Generate mitigation recommendations
            mitigation_recommendations = await self._generate_mitigation_recommendations(
                top_risks, self.risk_appetite
            )
            
            # Calculate residual risk
            residual_risk = self._calculate_residual_risk(
                risk_scores["overall_score"], mitigation_recommendations
            )
            
            # Create comprehensive assessment
            assessment = ComprehensiveRiskAssessment(
                assessment_id=assessment_id,
                assessment_date=datetime.utcnow(),
                scope=scope,
                methodology=framework,
                risk_appetite=self.risk_appetite,
                identified_risks=identified_risks,
                risk_scenarios=scenario_assessments,
                overall_risk_score=risk_scores["overall_score"],
                risk_distribution=risk_distribution,
                heat_map=heat_map,
                top_risks=top_risks,
                mitigation_recommendations=mitigation_recommendations,
                residual_risk=residual_risk,
                assessment_confidence=risk_scores["confidence"],
                next_review_date=datetime.utcnow() + timedelta(days=90),
                assessor=assessor
            )
            
            # Store assessment
            await self._store_risk_assessment(assessment)
            
            # Log assessment completion
            await self.audit_logger.log_audit_event(
                event_type="risk_assessment_completed",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Comprehensive risk assessment completed: {assessment_id}",
                details={
                    "assessment_id": assessment_id,
                    "scope": scope,
                    "framework": framework,
                    "risks_identified": len(identified_risks),
                    "overall_risk_score": risk_scores["overall_score"],
                    "assessor": assessor
                }
            )
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Error conducting risk assessment: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to conduct risk assessment")
    
    async def assess_compliance_risks(
        self,
        framework: ComplianceFramework,
        jurisdiction: str = None
    ) -> Dict[str, Any]:
        """Assess compliance-specific risks"""



        try:
            # Get compliance status
            compliance_status = await self.compliance_monitor.evaluate_compliance_status(
                framework, self.compliance_monitor.MonitoringScope.SYSTEM
            )
            
            # Identify compliance risk factors
            compliance_risks = []
            
            # Risk from non-compliance
            if compliance_status["overall_status"] in ["non_compliant", "critical"]:
                compliance_risks.append({
                    "risk_id": f"COMP-{framework.value}-001",
                    "name": f"{framework.value} Non-Compliance Risk",
                    "category": RiskCategory.COMPLIANCE,
                    "likelihood": 0.9,
                    "impact": 0.8,
                    "description": f"High risk of regulatory penalties due to {framework.value} non-compliance",
                    "current_controls": compliance_status.get("controls", []),
                    "gaps": compliance_status.get("violations", [])
                })
            
            # Risk from pending violations
            if compliance_status.get("critical_violations", 0) > 0:
                compliance_risks.append({
                    "risk_id": f"COMP-{framework.value}-002",
                    "name": f"{framework.value} Critical Violations",
                    "category": RiskCategory.LEGAL,
                    "likelihood": 0.7,
                    "impact": 0.9,
                    "description": f"Critical compliance violations requiring immediate attention",
                    "violation_count": compliance_status.get("critical_violations", 0),
                    "estimated_penalties": self._estimate_compliance_penalties(framework, compliance_status)
                })
            
            # Risk from incomplete compliance programs
            program_completeness = compliance_status.get("compliance_score", 100) / 100
            if program_completeness < 0.8:
                compliance_risks.append({
                    "risk_id": f"COMP-{framework.value}-003",
                    "name": f"{framework.value} Program Gaps",
                    "category": RiskCategory.OPERATIONAL,
                    "likelihood": 0.6,
                    "impact": 0.6,
                    "description": f"Incomplete compliance program increases operational risk",
                    "program_completeness": program_completeness,
                    "missing_controls": compliance_status.get("missing_controls", [])
                })
            
            # Calculate overall compliance risk score
            if compliance_risks:
                overall_risk = sum(r["likelihood"] * r["impact"] for r in compliance_risks) / len(compliance_risks)
            else:
                overall_risk = 0.1  # Minimal residual risk
            
            return {
                "framework": framework.value,
                "jurisdiction": jurisdiction,
                "assessment_date": datetime.utcnow().isoformat(),
                "overall_compliance_risk": overall_risk,
                "risk_level": self._get_risk_level(overall_risk),
                "identified_risks": compliance_risks,
                "compliance_score": compliance_status.get("compliance_score", 100),
                "recommendations": self._generate_compliance_risk_recommendations(compliance_risks),
                "next_assessment": (datetime.utcnow() + timedelta(days=30)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing compliance risks: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to assess compliance risks")
    
    async def create_risk_mitigation_plan(
        self,
        risk_id: str,
        strategy: MitigationStrategy,
        actions: List[Dict[str, Any]],
        responsible_parties: List[str],
        budget: float = 0,
        timeline_days: int = 90
    ) -> str:
        """Create comprehensive risk mitigation plan"""



        try:
            # Generate plan ID
            plan_id = f"RMP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{risk_id[-8:]}"
            
            # Validate actions
            validated_actions = []
            for action in actions:
                if not all(key in action for key in ["description", "owner", "due_date"]):
                    raise ValueError("Each action must have description, owner, and due_date")
                validated_actions.append({
                    **action,
                    "status": "planned",
                    "created_at": datetime.utcnow().isoformat()
                })
            
            # Create timeline
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=timeline_days)
            timeline = {
                "start_date": start_date,
                "end_date": end_date,
                "milestones": self._generate_milestone_schedule(validated_actions, timeline_days)
            }
            
            # Define success metrics
            success_metrics = self._define_success_metrics(strategy, risk_id)
            
            # Create mitigation plan
            mitigation_plan = RiskMitigationPlan(
                plan_id=plan_id,
                risk_id=risk_id,
                strategy=strategy,
                actions=validated_actions,
                responsible_parties=responsible_parties,
                timeline=timeline,
                budget_required=budget,
                success_metrics=success_metrics,
                monitoring_frequency="weekly",
                review_dates=[
                    start_date + timedelta(days=30),
                    start_date + timedelta(days=60),
                    end_date
                ],
                status="active"
            )
            
            # Store mitigation plan
            async with get_db_session() as session:
                mitigation_record = RiskMitigation(
                    plan_id=plan_id,
                    risk_id=risk_id,
                    strategy=strategy.value,
                    plan_details=json.dumps(asdict(mitigation_plan)),
                    status="active",
                    created_at=datetime.utcnow(),
                    target_completion=end_date,
                    budget_allocated=budget
                )
                
                session.add(mitigation_record)
                await session.commit()
            
            # Log plan creation
            await self.audit_logger.log_audit_event(
                event_type="risk_mitigation_plan_created",
                category=AuditCategory.COMPLIANCE,
                level=AuditLevel.INFO,
                message=f"Risk mitigation plan created: {plan_id}",
                details={
                    "plan_id": plan_id,
                    "risk_id": risk_id,
                    "strategy": strategy.value,
                    "actions_count": len(validated_actions),
                    "budget": budget,
                    "timeline_days": timeline_days
                }
            )
            
            return plan_id
            
        except Exception as e:
            self.logger.error(f"Error creating mitigation plan: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create mitigation plan")
    
    async def monitor_risk_indicators(
        self,
        risk_category: Optional[RiskCategory] = None
    ) -> Dict[str, Any]:
        """Monitor real-time risk indicators"""



        try:
            indicators = {
                "monitoring_timestamp": datetime.utcnow().isoformat(),
                "overall_risk_level": RiskLevel.MEDIUM,
                "category_risks": {},
                "trending_risks": [],
                "alert_conditions": [],
                "recommendations": []
            }
            
            categories_to_monitor = [risk_category] if risk_category else list(RiskCategory)
            
            for category in categories_to_monitor:
                try:
                    category_indicators = await self._monitor_category_indicators(category)
                    indicators["category_risks"][category.value] = category_indicators
                    
                    # Check for alert conditions
                    if category_indicators["risk_score"] > 0.8:
                        indicators["alert_conditions"].append({
                            "category": category.value,
                            "risk_score": category_indicators["risk_score"],
                            "alert_type": "high_risk",
                            "description": f"High risk detected in {category.value} category"
                        })
                
                except Exception as e:
                    self.logger.error(f"Error monitoring {category.value} indicators: {str(e)}")
                    continue
            
            # Calculate overall risk level
            if indicators["category_risks"]:
                avg_risk = sum(
                    cat_data["risk_score"] 
                    for cat_data in indicators["category_risks"].values()
                ) / len(indicators["category_risks"])
                indicators["overall_risk_level"] = self._get_risk_level(avg_risk)
            
            # Identify trending risks
            indicators["trending_risks"] = await self._identify_trending_risks()
            
            # Generate recommendations
            if indicators["alert_conditions"]:
                indicators["recommendations"].extend([
                    "Review high-risk categories immediately",
                    "Implement additional monitoring",
                    "Consider emergency mitigation measures"
                ])
            
            return indicators
            
        except Exception as e:
            self.logger.error(f"Error monitoring risk indicators: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to monitor risk indicators")
    
    def _load_risk_factors(self) -> Dict[str, RiskFactor]:
        """Load predefined risk factors library"""



        return {
            "data_breach": RiskFactor(
                factor_id="RF-001",
                name="Data Breach Risk",
                description="Risk of unauthorized access to personal data",
                category=RiskCategory.SECURITY,
                likelihood=0.3,
                impact=0.9,
                detection_difficulty=0.7,
                time_horizon=365,
                data_sources=["security_logs", "audit_logs", "incident_reports"],
                indicators=["failed_login_attempts", "suspicious_access_patterns", "data_access_anomalies"],
                dependencies=["system_vulnerabilities", "user_behavior", "external_threats"]
            ),
            "regulatory_penalty": RiskFactor(
                factor_id="RF-002",
                name="Regulatory Penalty Risk",
                description="Risk of fines and penalties for non-compliance",
                category=RiskCategory.COMPLIANCE,
                likelihood=0.4,
                impact=0.8,
                detection_difficulty=0.3,
                time_horizon=180,
                data_sources=["compliance_metrics", "audit_results", "regulatory_updates"],
                indicators=["compliance_score", "outstanding_violations", "audit_findings"],
                dependencies=["regulatory_changes", "compliance_program_maturity", "monitoring_effectiveness"]
            ),
            "system_outage": RiskFactor(
                factor_id="RF-003",
                name="System Outage Risk",
                description="Risk of service disruption and downtime",
                category=RiskCategory.OPERATIONAL,
                likelihood=0.2,
                impact=0.6,
                detection_difficulty=0.4,
                time_horizon=90,
                data_sources=["system_metrics", "performance_logs", "infrastructure_monitoring"],
                indicators=["system_performance", "error_rates", "resource_utilization"],
                dependencies=["infrastructure_reliability", "capacity_planning", "disaster_recovery"]
            )
        }
    
    def _define_risk_appetite(self) -> Dict[str, float]:
        """Define organizational risk appetite thresholds"""



        return {
            "overall": 0.5,  # Maximum acceptable overall risk score
            "operational": 0.6,
            "compliance": 0.3,  # Low tolerance for compliance risks
            "security": 0.4,
            "financial": 0.5,
            "reputational": 0.3,  # Low tolerance for reputation risks
            "strategic": 0.6,
            "legal": 0.3,
            "technical": 0.6
        }
    
    def _get_risk_level(self, risk_score: float) -> RiskLevel:
        """Convert risk score to risk level"""
        if risk_score >= 0.9:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.7:
            return RiskLevel.VERY_HIGH
        elif risk_score >= 0.5:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        elif risk_score >= 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW


# Export for use in other modules
__all__ = ["RiskAssessmentEngine", "RiskCategory", "RiskLevel", "RiskStatus", "MitigationStrategy"]
