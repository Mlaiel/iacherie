"""Compliance Checker - Legal & Regulatory Compliance Management System

Comprehensive legal compliance monitoring, regulatory adherence checking,
and automated compliance reporting for content licensing operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

⚠️  IMPORTANT LEGAL NOTICE:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, copying, distribution, or commercialization without explicit written permission is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.

Team Specialties:
- Lead AI Developer & Backend Senior Engineer
- Machine Learning Engineer & Audio Processing Specialist  
- Database Administrator & Security Expert
- Microservices Architect & DevOps Engineer
- AI Prompt Engineer & Content Protection Specialist
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from decimal import Decimal

try:
    from core.exceptions import ComplianceError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    ComplianceError, ValidationError = globals().get('ComplianceError, ValidationError', Exception)
from ...integrations.legal.regulations import RegulationDatabase
from ...integrations.legal.courts import CourtDecisionAPI
from ...integrations.government.apis import GovernmentAPIManager
from ...ml.compliance_models import ComplianceAnalysisAI
from ...utils.legal_document_parser import LegalDocumentParser
from ...security.audit_logger import ComplianceAuditLogger

logger = logging.getLogger(__name__)

class ComplianceArea(Enum):
    """Areas of compliance monitoring"""    COPYRIGHT_LAW = "copyright_law"
    DATA_PROTECTION = "data_protection"
    CONSUMER_PROTECTION = "consumer_protection"
    ANTI_MONEY_LAUNDERING = "anti_money_laundering"
    TAX_COMPLIANCE = "tax_compliance"
    INTERNATIONAL_TRADE = "international_trade"
    CONTENT_REGULATION = "content_regulation"
    PLATFORM_POLICIES = "platform_policies"

class ComplianceStatus(Enum):
    """Compliance status levels"""    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"
    REQUIRES_ACTION = "requires_action"

class RiskLevel(Enum):
    """Risk assessment levels"""    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class JurisdictionType(Enum):
    """Types of legal jurisdictions"""    NATIONAL = "national"
    REGIONAL = "regional"
    INTERNATIONAL = "international"
    PLATFORM_SPECIFIC = "platform_specific"

@dataclass
class ComplianceRule:
    """Individual compliance rule definition"""    rule_id: str
    name: str
    description: str
    compliance_area: ComplianceArea
    jurisdiction: str
    jurisdiction_type: JurisdictionType
    mandatory: bool
    effective_date: datetime
    expiry_date: Optional[datetime]
    rule_text: str
    interpretation_notes: str
    penalties: Dict[str, Any]
    monitoring_frequency: str  # daily, weekly, monthly
    automated_check: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComplianceViolation:
    """Compliance violation record"""    violation_id: str
    rule_id: str
    content_id: str
    license_id: Optional[str]
    violation_type: str
    severity: RiskLevel
    description: str
    evidence: List[Dict[str, Any]]
    detected_at: datetime
    status: str  # open, investigating, resolved, dismissed
    resolution_steps: List[str]
    estimated_penalty: Optional[Decimal]
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None

@dataclass
class ComplianceReport:
    """Comprehensive compliance assessment report"""    report_id: str
    assessment_period: Dict[str, datetime]
    overall_status: ComplianceStatus
    risk_score: float
    areas_assessed: List[ComplianceArea]
    jurisdictions_covered: List[str]
    rules_checked: int
    violations_found: int
    critical_issues: int
    recommendations: List[Dict[str, Any]]
    detailed_findings: Dict[str, Any]
    next_assessment_date: datetime
    generated_at: datetime = field(default_factory=datetime.utcnow)

class ComplianceChecker:
    """    Advanced Legal & Regulatory Compliance Management System
    
    Monitors compliance with copyright laws, data protection regulations,
    consumer protection rules, and platform-specific policies across jurisdictions.
    """    
    def __init__(self):
        self.regulation_db = RegulationDatabase()
        self.court_api = CourtDecisionAPI()
        self.government_apis = GovernmentAPIManager()
        self.compliance_ai = ComplianceAnalysisAI()
        self.document_parser = LegalDocumentParser()
        self.audit_logger = ComplianceAuditLogger()
        
        # Compliance rules and monitoring
        self.active_rules = {}
        self.jurisdiction_mapping = {}
        self.risk_assessments = {}
        self.violation_history = {}
        
        # Performance metrics
        self.metrics = {
            "rules_monitored": 0,
            "violations_detected": 0,
            "compliance_score": 1.0,
            "risk_alerts_generated": 0,
            "successful_remediations": 0
        }

    async def initialize(self):
        """Initialize compliance checker with current regulations"""        await self._load_compliance_rules()
        await self._initialize_jurisdiction_mapping()
        await self._setup_monitoring_schedules()

    async def perform_comprehensive_compliance_check(
        self,
        content_id: str,
        license_id: Optional[str] = None,
        jurisdictions: Optional[List[str]] = None,
        areas: Optional[List[ComplianceArea]] = None
    ) -> ComplianceReport:
        """        Perform comprehensive compliance assessment
        
        Args:
            content_id: Content to assess
            license_id: Related license (optional)
            jurisdictions: Specific jurisdictions to check
            areas: Specific compliance areas to assess
            
        Returns:
            Detailed compliance assessment report
        """        try:
            assessment_start = datetime.utcnow()
            
            # Determine scope of assessment
            target_jurisdictions = jurisdictions or await self._determine_relevant_jurisdictions(content_id)
            target_areas = areas or list(ComplianceArea)
            
            # Collect content and license data
            content_data = await self._collect_content_data(content_id)
            license_data = await self._collect_license_data(license_id) if license_id else {}
            
            # Perform rule-by-rule assessment
            assessment_results = {}
            total_violations = 0
            critical_issues = 0
            
            for area in target_areas:
                area_rules = await self._get_rules_for_area(area, target_jurisdictions)
                area_results = {
                    "rules_checked": len(area_rules),
                    "violations": [],
                    "warnings": [],
                    "status": ComplianceStatus.COMPLIANT
                }
                
                for rule in area_rules:
                    # Check compliance with individual rule
                    rule_result = await self._check_rule_compliance(
                        rule, content_data, license_data
                    )
                    
                    if rule_result["compliant"]:
                        continue
                    
                    # Record violation
                    violation = ComplianceViolation(
                        violation_id=str(uuid.uuid4()),
                        rule_id=rule.rule_id,
                        content_id=content_id,
                        license_id=license_id,
                        violation_type=rule_result["violation_type"],
                        severity=RiskLevel(rule_result["severity"]),
                        description=rule_result["description"],
                        evidence=rule_result["evidence"],
                        detected_at=datetime.utcnow(),
                        status="open",
                        resolution_steps=rule_result["resolution_steps"],
                        estimated_penalty=rule_result.get("estimated_penalty")
                    )
                    
                    if violation.severity == RiskLevel.CRITICAL:
                        critical_issues += 1
                        area_results["violations"].append(violation.__dict__)
                    else:
                        area_results["warnings"].append(violation.__dict__)
                    
                    total_violations += 1
                
                # Determine area status
                if area_results["violations"]:
                    area_results["status"] = ComplianceStatus.NON_COMPLIANT
                elif area_results["warnings"]:
                    area_results["status"] = ComplianceStatus.PARTIALLY_COMPLIANT
                
                assessment_results[area.value] = area_results
            
            # Calculate overall compliance status and risk score
            overall_status = await self._calculate_overall_status(assessment_results)
            risk_score = await self._calculate_risk_score(assessment_results, total_violations)
            
            # Generate recommendations
            recommendations = await self._generate_compliance_recommendations(
                assessment_results, content_data, license_data
            )
            
            # Create comprehensive report
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                assessment_period={
                    "start": assessment_start,
                    "end": datetime.utcnow()
                },
                overall_status=overall_status,
                risk_score=risk_score,
                areas_assessed=target_areas,
                jurisdictions_covered=target_jurisdictions,
                rules_checked=sum(r["rules_checked"] for r in assessment_results.values()),
                violations_found=total_violations,
                critical_issues=critical_issues,
                recommendations=recommendations,
                detailed_findings=assessment_results,
                next_assessment_date=datetime.utcnow() + timedelta(days=30)
            )
            
            # Store report and log audit
            await self._store_compliance_report(report)
            await self.audit_logger.log_compliance_assessment(report)
            
            # Update metrics
            self.metrics["rules_monitored"] += report.rules_checked
            self.metrics["violations_detected"] += total_violations
            self.metrics["risk_alerts_generated"] += critical_issues
            
            return report
            
        except Exception as e:
            logger.error(f"Error performing compliance check: {str(e)}")
            raise ComplianceError(f"Failed to perform compliance assessment: {str(e)}")

    async def monitor_regulatory_changes(
        self,
        jurisdictions: List[str],
        areas: List[ComplianceArea]
    ) -> Dict[str, Any]:
        """        Monitor for new regulatory changes and updates
        
        Args:
            jurisdictions: Jurisdictions to monitor
            areas: Compliance areas to track
            
        Returns:
            Summary of regulatory changes and impacts
        """        try:
            monitoring_results = {
                "new_regulations": [],
                "updated_regulations": [],
                "court_decisions": [],
                "policy_changes": [],
                "impact_assessment": {}
            }
            
            # Monitor each jurisdiction
            for jurisdiction in jurisdictions:
                # Check for new regulations
                new_regs = await self.regulation_db.get_recent_regulations(
                    jurisdiction, areas, days_back=30
                )
                monitoring_results["new_regulations"].extend(new_regs)
                
                # Check for regulation updates
                updated_regs = await self.regulation_db.get_updated_regulations(
                    jurisdiction, areas, days_back=30
                )
                monitoring_results["updated_regulations"].extend(updated_regs)
                
                # Monitor court decisions
                court_decisions = await self.court_api.get_relevant_decisions(
                    jurisdiction, areas, days_back=30
                )
                monitoring_results["court_decisions"].extend(court_decisions)
                
                # Check government policy changes
                policy_changes = await self.government_apis.get_policy_updates(
                    jurisdiction, areas, days_back=30
                )
                monitoring_results["policy_changes"].extend(policy_changes)
            
            # Assess impact of changes
            for change_type, changes in monitoring_results.items():
                if change_type == "impact_assessment":
                    continue
                    
                for change in changes:
                    impact = await self._assess_regulatory_impact(change, change_type)
                    if change["id"] not in monitoring_results["impact_assessment"]:
                        monitoring_results["impact_assessment"][change["id"]] = impact
            
            # Generate alerts for high-impact changes
            high_impact_changes = [
                change for change_id, impact in monitoring_results["impact_assessment"].items()
                if impact["risk_level"] in ["high", "critical"]
                for change_list in monitoring_results.values()
                if isinstance(change_list, list)
                for change in change_list
                if change.get("id") == change_id
            ]
            
            if high_impact_changes:
                await self._generate_regulatory_alerts(high_impact_changes)
            
            return monitoring_results
            
        except Exception as e:
            logger.error(f"Error monitoring regulatory changes: {str(e)}")
            raise ComplianceError(f"Failed to monitor regulations: {str(e)}")

    async def validate_contract_compliance(
        self,
        contract_text: str,
        contract_type: str,
        jurisdictions: List[str]
    ) -> Dict[str, Any]:
        """        Validate contract for legal compliance across jurisdictions
        
        Args:
            contract_text: Full contract text
            contract_type: Type of contract
            jurisdictions: Applicable jurisdictions
            
        Returns:
            Detailed compliance validation report
        """        try:
            validation_results = {
                "overall_compliant": True,
                "jurisdiction_compliance": {},
                "missing_clauses": [],
                "problematic_clauses": [],
                "recommendations": [],
                "risk_assessment": {}
            }
            
            # Parse contract structure
            parsed_contract = await self.document_parser.parse_contract(contract_text)
            
            # Validate against each jurisdiction
            for jurisdiction in jurisdictions:
                jurisdiction_rules = await self._get_contract_rules(jurisdiction, contract_type)
                jurisdiction_result = {
                    "compliant": True,
                    "missing_required_clauses": [],
                    "invalid_clauses": [],
                    "warnings": []
                }
                
                # Check required clauses
                for rule in jurisdiction_rules:
                    if rule.mandatory:
                        clause_present = await self._check_clause_presence(
                            parsed_contract, rule
                        )
                        if not clause_present:
                            jurisdiction_result["missing_required_clauses"].append({
                                "rule_id": rule.rule_id,
                                "clause_type": rule.name,
                                "description": rule.description,
                                "penalty_risk": rule.penalties
                            })
                            jurisdiction_result["compliant"] = False
                
                # Check for invalid clause patterns
                invalid_patterns = await self._check_invalid_patterns(
                    parsed_contract, jurisdiction, contract_type
                )
                jurisdiction_result["invalid_clauses"].extend(invalid_patterns)
                
                if invalid_patterns:
                    jurisdiction_result["compliant"] = False
                
                validation_results["jurisdiction_compliance"][jurisdiction] = jurisdiction_result
                
                if not jurisdiction_result["compliant"]:
                    validation_results["overall_compliant"] = False
            
            # AI-powered compliance analysis
            ai_analysis = await self.compliance_ai.analyze_contract_compliance(
                contract_text, contract_type, jurisdictions
            )
            
            # Merge AI insights
            validation_results["ai_insights"] = ai_analysis
            validation_results["recommendations"].extend(ai_analysis.get("recommendations", []))
            
            # Calculate risk score
            risk_factors = await self._calculate_contract_risk_factors(
                validation_results, parsed_contract
            )
            validation_results["risk_assessment"] = risk_factors
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating contract compliance: {str(e)}")
            raise ComplianceError(f"Failed to validate contract: {str(e)}")

    async def generate_compliance_dashboard(
        self,
        period_days: int = 30,
        jurisdictions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """        Generate compliance monitoring dashboard data
        
        Args:
            period_days: Period for dashboard data
            jurisdictions: Specific jurisdictions to include
            
        Returns:
            Dashboard data with metrics and visualizations
        """        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=period_days)
            
            # Collect compliance metrics
            metrics_data = await self._collect_compliance_metrics(
                start_date, end_date, jurisdictions
            )
            
            # Generate trend analysis
            trends = await self._analyze_compliance_trends(
                start_date, end_date, jurisdictions
            )
            
            # Risk heat map
            risk_heatmap = await self._generate_risk_heatmap(jurisdictions)
            
            # Upcoming regulatory changes
            upcoming_changes = await self._get_upcoming_regulatory_changes(
                jurisdictions, days_ahead=90
            )
            
            # Action items
            action_items = await self._get_priority_action_items(jurisdictions)
            
            dashboard = {
                "period": {"start": start_date, "end": end_date},
                "summary_metrics": {
                    "overall_compliance_score": metrics_data["overall_score"],
                    "total_violations": metrics_data["violations_count"],
                    "critical_issues": metrics_data["critical_count"],
                    "resolved_issues": metrics_data["resolved_count"],
                    "pending_actions": len(action_items)
                },
                "compliance_by_area": metrics_data["area_breakdown"],
                "compliance_by_jurisdiction": metrics_data["jurisdiction_breakdown"],
                "trend_analysis": trends,
                "risk_heatmap": risk_heatmap,
                "upcoming_changes": upcoming_changes,
                "priority_actions": action_items,
                "generated_at": datetime.utcnow()
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating compliance dashboard: {str(e)}")
            raise ComplianceError(f"Failed to generate dashboard: {str(e)}")

    async def _check_rule_compliance(
        self,
        rule: ComplianceRule,
        content_data: Dict[str, Any],
        license_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check compliance with individual rule"""        # Rule-specific compliance checking logic
        if rule.automated_check:
            # Use AI/ML model for automated checking
            result = await self.compliance_ai.check_rule_compliance(
                rule, content_data, license_data
            )
        else:
            # Manual review required
            result = {
                "compliant": None,  # Requires manual review
                "confidence": 0.0,
                "requires_manual_review": True
            }
        
        # Enhance result with context
        if not result.get("compliant", True):
            result.update({
                "violation_type": self._determine_violation_type(rule, content_data),
                "severity": self._assess_violation_severity(rule, content_data),
                "evidence": self._collect_evidence(rule, content_data, license_data),
                "resolution_steps": self._generate_resolution_steps(rule),
                "estimated_penalty": self._estimate_penalty(rule, content_data)
            })
        
        return result

    async def _load_compliance_rules(self):
        """Load current compliance rules from regulation database"""        try:
            # Load rules by jurisdiction and area
            all_rules = await self.regulation_db.get_active_rules()
            
            for rule_data in all_rules:
                rule = ComplianceRule(
                    rule_id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data["description"],
                    compliance_area=ComplianceArea(rule_data["area"]),
                    jurisdiction=rule_data["jurisdiction"],
                    jurisdiction_type=JurisdictionType(rule_data["jurisdiction_type"]),
                    mandatory=rule_data["mandatory"],
                    effective_date=datetime.fromisoformat(rule_data["effective_date"]),
                    expiry_date=datetime.fromisoformat(rule_data["expiry_date"]) if rule_data.get("expiry_date") else None,
                    rule_text=rule_data["text"],
                    interpretation_notes=rule_data.get("notes", ""),
                    penalties=rule_data.get("penalties", {}),
                    monitoring_frequency=rule_data.get("frequency", "monthly"),
                    automated_check=rule_data.get("automated", False),
                    metadata=rule_data.get("metadata", {})
                )
                
                self.active_rules[rule.rule_id] = rule
            
            logger.info(f"Loaded {len(self.active_rules)} compliance rules")
            
        except Exception as e:
            logger.error(f"Error loading compliance rules: {str(e)}")
            raise ComplianceError(f"Failed to load rules: {str(e)}")


class LegalValidator:
    """    Legal Validation and Advisory System
    """    
    def __init__(self, compliance_checker: ComplianceChecker):
        self.compliance_checker = compliance_checker
        self.legal_research_ai = None  # Will be initialized with legal AI
        self.precedent_database = None
        
    async def validate_licensing_strategy(
        self,
        strategy: Dict[str, Any],
        target_markets: List[str]
    ) -> Dict[str, Any]:
        """Validate licensing strategy for legal soundness across multiple jurisdictions"""        try:
            validation_id = str(uuid.uuid4())
            logger.info(f"Validating licensing strategy {validation_id} for {len(target_markets)} markets")
            
            # Validate strategy structure
            required_strategy_fields = ["content_types", "licensing_model", "pricing_structure", "territory_approach"]
            missing_fields = [field for field in required_strategy_fields if field not in strategy]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required strategy fields: {', '.join(missing_fields)}"
                }
            
            validation_results = {
                "validation_id": validation_id,
                "strategy": strategy,
                "target_markets": target_markets,
                "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                "market_validations": {},
                "overall_compliance": True,
                "recommendations": [],
                "risk_factors": []
            }
            
            # Validate strategy for each target market
            for market in target_markets:
                try:
                    market_validation = await self._validate_strategy_for_market(strategy, market)
                    validation_results["market_validations"][market] = market_validation
                    
                    # Update overall compliance
                    if not market_validation["compliant"]:
                        validation_results["overall_compliance"] = False
                    
                    # Collect recommendations and risk factors
                    validation_results["recommendations"].extend(market_validation.get("recommendations", []))
                    validation_results["risk_factors"].extend(market_validation.get("risk_factors", []))
                    
                except Exception as e:
                    logger.error(f"Error validating strategy for market {market}: {str(e)}")
                    validation_results["market_validations"][market] = {
                        "error": str(e),
                        "compliant": False
                    }
                    validation_results["overall_compliance"] = False
            
            # Generate strategic recommendations
            strategic_recommendations = await self._generate_strategic_recommendations(
                validation_results["market_validations"],
                strategy
            )
            validation_results["strategic_recommendations"] = strategic_recommendations
            
            # Calculate compliance score
            compliant_markets = len([v for v in validation_results["market_validations"].values() if v.get("compliant", False)])
            validation_results["compliance_score"] = compliant_markets / len(target_markets) if target_markets else 0
            
            # Store validation results
            await self._store_strategy_validation(validation_results)
            
            return {
                "success": True,
                "validation_results": validation_results,
                "immediate_action_required": not validation_results["overall_compliance"]
            }
            
        except Exception as e:
            logger.error(f"Error validating licensing strategy: {str(e)}")
            return {"success": False, "error": str(e)}
        
    async def generate_legal_opinion(
        self,
        legal_question: str,
        jurisdiction: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive legal opinion on licensing matters using AI-powered legal analysis"""        try:
            opinion_id = str(uuid.uuid4())
            logger.info(f"Generating legal opinion {opinion_id} for jurisdiction {jurisdiction}")
            
            # Validate input parameters
            if not legal_question or not jurisdiction:
                return {
                    "success": False,
                    "error": "Legal question and jurisdiction are required"
                }
            
            # Research applicable laws and regulations
            applicable_laws = await self._research_applicable_laws(legal_question, jurisdiction)
            
            # Analyze relevant case law
            case_law_analysis = await self._analyze_case_law(legal_question, jurisdiction)
            
            # Get regulatory guidance
            regulatory_guidance = await self._get_regulatory_guidance(legal_question, jurisdiction)
            
            # Generate legal analysis using AI
            legal_analysis = await self._perform_ai_legal_analysis(
                question=legal_question,
                laws=applicable_laws,
                case_law=case_law_analysis,
                regulatory_guidance=regulatory_guidance,
                context=context
            )
            
            # Assess risk levels
            risk_assessment = await self._assess_legal_risks(
                legal_question, jurisdiction, legal_analysis
            )
            
            # Generate practical recommendations
            recommendations = await self._generate_legal_recommendations(
                legal_analysis, risk_assessment, context
            )
            
            # Construct comprehensive legal opinion
            legal_opinion = {
                "opinion_id": opinion_id,
                "generation_timestamp": datetime.now(timezone.utc).isoformat(),
                "legal_question": legal_question,
                "jurisdiction": jurisdiction,
                "context": context,
                
                # Legal research
                "applicable_laws": applicable_laws,
                "case_law_analysis": case_law_analysis,
                "regulatory_guidance": regulatory_guidance,
                
                # Analysis and conclusions
                "legal_analysis": legal_analysis,
                "risk_assessment": risk_assessment,
                "recommendations": recommendations,
                
                # Opinion summary
                "executive_summary": legal_analysis.get("summary", ""),
                "confidence_level": legal_analysis.get("confidence", 0.8),
                "certainty_factors": legal_analysis.get("certainty_factors", []),
                
                # Disclaimers
                "disclaimers": [
                    "This opinion is generated by AI and should not replace professional legal advice",
                    "Laws and regulations may change; consult current legal sources",
                    "Jurisdiction-specific variations may apply",
                    "Consult qualified legal counsel for binding legal advice"
                ],
                
                # Follow-up actions
                "suggested_actions": recommendations.get("immediate_actions", []),
                "monitoring_requirements": recommendations.get("ongoing_monitoring", [])
            }
            
            # Store legal opinion for future reference
            await self._store_legal_opinion(legal_opinion)
            
            # Generate citation and verification data
            citation_data = await self._generate_opinion_citations(legal_opinion)
            legal_opinion["citations"] = citation_data
            
            return {
                "success": True,
                "legal_opinion": legal_opinion,
                "requires_attorney_review": risk_assessment.get("high_risk", False)
            }
            
        except Exception as e:
            logger.error(f"Error generating legal opinion: {str(e)}")
            return {"success": False, "error": str(e)}
