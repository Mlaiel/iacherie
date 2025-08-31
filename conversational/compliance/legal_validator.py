"""Legal Validator - Advanced Legal Compliance Validation System

This module provides comprehensive legal validation for conversational AI content,
including risk assessment, regulatory compliance, and legal disclaimer management.

Author: Fahed Mlaiel
Contact: mlaiel@live.de
Copyright: © 2025 Fahed Mlaiel. All rights reserved.
"""import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from enum import Enum

from ..core.database import DatabaseManager
from ..core.cache import CacheManager
from ..ml.nlp_processor import NLPProcessor
from ..security.encryption import EncryptionService


class LegalRiskLevel(Enum):
    """Legal risk severity levels"""    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class LegalDomain(Enum):
    """Legal domain categories"""    INTELLECTUAL_PROPERTY = "intellectual_property"
    PRIVACY_DATA = "privacy_data"
    DEFAMATION = "defamation"
    HARASSMENT = "harassment"
    FINANCIAL_ADVICE = "financial_advice"
    MEDICAL_ADVICE = "medical_advice"
    LEGAL_ADVICE = "legal_advice"
    DISCRIMINATION = "discrimination"
    HATE_SPEECH = "hate_speech"
    REGULATORY_COMPLIANCE = "regulatory_compliance"


@dataclass
class LegalRisk:
    """Legal risk assessment structure"""    domain: LegalDomain
    risk_level: LegalRiskLevel
    description: str
    evidence: List[str]
    recommendations: List[str]
    jurisdictions: List[str]
    confidence_score: float
    legal_precedents: List[str]
    mitigation_strategies: List[str]


@dataclass
class LegalValidationResult:
    """Legal validation result structure"""    is_compliant: bool
    overall_risk_level: LegalRiskLevel
    risks: List[LegalRisk]
    violations: List[Dict[str, Any]]
    warnings: List[str]
    recommendations: List[str]
    legal_disclaimers: List[str]
    jurisdiction_compliance: Dict[str, bool]
    processing_time_ms: int
    confidence_score: float


class LegalValidator:
    """    Advanced legal compliance validation system.
    
    Provides comprehensive legal risk assessment for conversational AI content
    including regulatory compliance, risk categorization, and mitigation strategies.
    """    
    def __init__(
        self,
        db_manager: DatabaseManager,
        cache_manager: CacheManager,
        nlp_processor: Optional[NLPProcessor] = None
    ):
        self.db_manager = db_manager
        self.cache_manager = cache_manager
        self.nlp_processor = nlp_processor or NLPProcessor()
        self.logger = logging.getLogger(__name__)
        
        # Legal pattern databases
        self.legal_patterns = self._load_legal_patterns()
        self.jurisdiction_rules = self._load_jurisdiction_rules()
        self.disclaimer_templates = self._load_disclaimer_templates()
        
        # Risk assessment models
        self.risk_thresholds = {
            LegalRiskLevel.CRITICAL: 0.9,
            LegalRiskLevel.HIGH: 0.7,
            LegalRiskLevel.MEDIUM: 0.5,
            LegalRiskLevel.LOW: 0.3
        }
        
        self.logger.info("LegalValidator initialized with legal pattern database")
    
    def _load_legal_patterns(self) -> Dict[LegalDomain, List[Dict[str, Any]]]:
        """Load legal risk patterns from database or configuration"""        patterns = {
            LegalDomain.FINANCIAL_ADVICE: [
                {
                    "pattern": r"\b(investment|stock|trading|financial|portfolio|profit|guaranteed return)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Financial advice without proper licensing",
                    "jurisdictions": ["US", "EU", "UK", "CA"]
                },
                {
                    "pattern": r"\b(buy|sell|invest in|recommend)\s+\w+\s+(stock|bond|cryptocurrency|forex)\b",
                    "risk_level": LegalRiskLevel.CRITICAL,
                    "description": "Specific investment recommendations",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                }
            ],
            LegalDomain.MEDICAL_ADVICE: [
                {
                    "pattern": r"\b(diagnose|treat|cure|medicine|prescription|dosage)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Medical advice without proper licensing",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                },
                {
                    "pattern": r"\b(take|stop taking|increase|decrease)\s+\w+\s+(medication|pills|drugs)\b",
                    "risk_level": LegalRiskLevel.CRITICAL,
                    "description": "Specific medication recommendations",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                }
            ],
            LegalDomain.LEGAL_ADVICE: [
                {
                    "pattern": r"\b(sue|lawsuit|legal action|attorney|lawyer|court|litigation)\b",
                    "risk_level": LegalRiskLevel.MEDIUM,
                    "description": "Legal guidance without proper licensing",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                },
                {
                    "pattern": r"\byou should\s+(file|contact|hire)\s+(lawyer|attorney|legal counsel)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Specific legal action recommendations",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                }
            ],
            LegalDomain.DEFAMATION: [
                {
                    "pattern": r"\b(liar|fraud|criminal|scam|dishonest)\s+(?:person|individual|company|organization)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Potentially defamatory statements",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                }
            ],
            LegalDomain.HATE_SPEECH: [
                {
                    "pattern": r"\b(hate|despise|discriminate)\s+\w+\s+(race|religion|gender|sexuality|nationality)\b",
                    "risk_level": LegalRiskLevel.CRITICAL,
                    "description": "Hate speech content",
                    "jurisdictions": ["EU", "UK", "CA", "AU", "DE", "FR"]
                }
            ],
            LegalDomain.PRIVACY_DATA: [
                {
                    "pattern": r"\b(social security|ssn|credit card|bank account|password|personal data)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Personal data handling concerns",
                    "jurisdictions": ["US", "EU", "UK", "CA"]
                }
            ],
            LegalDomain.INTELLECTUAL_PROPERTY: [
                {
                    "pattern": r"\b(copy|reproduce|distribute|download|pirate)\s+\w+\s+(copyrighted|patented|trademarked)\b",
                    "risk_level": LegalRiskLevel.HIGH,
                    "description": "Intellectual property infringement",
                    "jurisdictions": ["US", "EU", "UK", "CA", "AU"]
                }
            ]
        }
        
        return patterns
    
    def _load_jurisdiction_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load jurisdiction-specific legal rules"""        return {
            "US": {
                "financial_licensing_required": True,
                "medical_licensing_required": True,
                "legal_licensing_required": True,
                "hate_speech_protection": False,
                "defamation_standards": "actual_malice",
                "privacy_regulations": ["CCPA", "COPPA"],
                "content_liability": "section_230"
            },
            "EU": {
                "financial_licensing_required": True,
                "medical_licensing_required": True,
                "legal_licensing_required": True,
                "hate_speech_protection": True,
                "defamation_standards": "negligence",
                "privacy_regulations": ["GDPR"],
                "content_liability": "dsa_regulation"
            },
            "UK": {
                "financial_licensing_required": True,
                "medical_licensing_required": True,
                "legal_licensing_required": True,
                "hate_speech_protection": True,
                "defamation_standards": "serious_harm",
                "privacy_regulations": ["UK_GDPR", "DPA_2018"],
                "content_liability": "online_safety_act"
            },
            "CA": {
                "financial_licensing_required": True,
                "medical_licensing_required": True,
                "legal_licensing_required": True,
                "hate_speech_protection": True,
                "defamation_standards": "negligence",
                "privacy_regulations": ["PIPEDA"],
                "content_liability": "safe_harbor"
            },
            "DE": {
                "financial_licensing_required": True,
                "medical_licensing_required": True,
                "legal_licensing_required": True,
                "hate_speech_protection": True,
                "defamation_standards": "negligence",
                "privacy_regulations": ["GDPR", "BDSG"],
                "content_liability": "netzwerkdurchsetzungsgesetz"
            }
        }
    
    def _load_disclaimer_templates(self) -> Dict[LegalDomain, List[str]]:
        """Load legal disclaimer templates"""        return {
            LegalDomain.FINANCIAL_ADVICE: [
                "This information is for educational purposes only and does not constitute financial advice.",
                "Please consult with a qualified financial advisor before making investment decisions.",
                "Past performance does not guarantee future results."
            ],
            LegalDomain.MEDICAL_ADVICE: [
                "This information is for educational purposes only and does not constitute medical advice.",
                "Please consult with a qualified healthcare professional for medical concerns.",
                "Do not use this information to diagnose or treat medical conditions."
            ],
            LegalDomain.LEGAL_ADVICE: [
                "This information is for educational purposes only and does not constitute legal advice.",
                "Please consult with a qualified attorney for legal matters.",
                "Laws vary by jurisdiction and individual circumstances."
            ]
        }
    
    async def validate_content(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]] = None
    ) -> LegalValidationResult:
        """        Comprehensive legal validation of conversational content.
        
        Args:
            user_input: User's input text
            ai_response: AI's generated response
            context: Additional context information
            
        Returns:
            LegalValidationResult: Comprehensive legal assessment
        """        start_time = datetime.now()
        
        try:
            self.logger.debug("Starting legal content validation")
            
            # Check cache for recent validation
            cache_key = f"legal_validation_{hash(user_input + ai_response)}"
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                return cached_result
            
            # Initialize result
            result = LegalValidationResult(
                is_compliant=True,
                overall_risk_level=LegalRiskLevel.NONE,
                risks=[],
                violations=[],
                warnings=[],
                recommendations=[],
                legal_disclaimers=[],
                jurisdiction_compliance={},
                processing_time_ms=0,
                confidence_score=1.0
            )
            
            # Combine content for analysis
            combined_content = f"{user_input} {ai_response}".lower()
            
            # Pattern-based risk detection
            detected_risks = await self._detect_legal_risks(combined_content, context)
            result.risks.extend(detected_risks)
            
            # NLP-based risk analysis
            nlp_risks = await self._analyze_nlp_risks(user_input, ai_response, context)
            result.risks.extend(nlp_risks)
            
            # Jurisdiction compliance check
            result.jurisdiction_compliance = await self._check_jurisdiction_compliance(
                result.risks, context
            )
            
            # Calculate overall risk level
            result.overall_risk_level = self._calculate_overall_risk(result.risks)
            
            # Generate violations for high-risk content
            result.violations = self._generate_violations(result.risks)
            
            # Generate recommendations and disclaimers
            result.recommendations = self._generate_recommendations(result.risks)
            result.legal_disclaimers = self._generate_disclaimers(result.risks)
            
            # Determine compliance status
            result.is_compliant = (
                result.overall_risk_level in [LegalRiskLevel.NONE, LegalRiskLevel.LOW] and
                not result.violations
            )
            
            # Calculate confidence score
            result.confidence_score = self._calculate_confidence_score(result.risks)
            
            # Calculate processing time
            processing_time = datetime.now() - start_time
            result.processing_time_ms = int(processing_time.total_seconds() * 1000)
            
            # Cache result
            await self.cache_manager.set(cache_key, result, ttl=3600)  # 1 hour
            
            self.logger.info(
                f"Legal validation completed with risk level: {result.overall_risk_level.value}"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in legal validation: {str(e)}")
            processing_time = datetime.now() - start_time
            return LegalValidationResult(
                is_compliant=False,
                overall_risk_level=LegalRiskLevel.HIGH,
                risks=[],
                violations=[{"type": "validation_error", "message": str(e)}],
                warnings=[f"Legal validation error: {str(e)}"],
                recommendations=["Manual legal review required due to validation error"],
                legal_disclaimers=["Legal validation incomplete - seek professional advice"],
                jurisdiction_compliance={},
                processing_time_ms=int(processing_time.total_seconds() * 1000),
                confidence_score=0.0
            )
    
    async def _detect_legal_risks(
        self,
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> List[LegalRisk]:
        """Detect legal risks using pattern matching"""        detected_risks = []
        
        for domain, patterns in self.legal_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                if matches:
                    evidence = [match.group() for match in re.finditer(pattern, content, re.IGNORECASE)]
                    
                    risk = LegalRisk(
                        domain=domain,
                        risk_level=pattern_config["risk_level"],
                        description=pattern_config["description"],
                        evidence=evidence,
                        recommendations=self._get_domain_recommendations(domain),
                        jurisdictions=pattern_config["jurisdictions"],
                        confidence_score=0.8,  # Pattern-based detection confidence
                        legal_precedents=self._get_legal_precedents(domain),
                        mitigation_strategies=self._get_mitigation_strategies(domain)
                    )
                    
                    detected_risks.append(risk)
        
        return detected_risks
    
    async def _analyze_nlp_risks(
        self,
        user_input: str,
        ai_response: str,
        context: Optional[Dict[str, Any]]
    ) -> List[LegalRisk]:
        """Analyze legal risks using NLP processing"""        nlp_risks = []
        
        try:
            # Sentiment analysis for defamation risk
            sentiment_score = await self.nlp_processor.analyze_sentiment(ai_response)
            if sentiment_score < -0.7:  # Very negative sentiment
                nlp_risks.append(LegalRisk(
                    domain=LegalDomain.DEFAMATION,
                    risk_level=LegalRiskLevel.MEDIUM,
                    description="Negative sentiment potentially indicating defamatory content",
                    evidence=[f"Negative sentiment score: {sentiment_score}"],
                    recommendations=["Review content for potentially defamatory statements"],
                    jurisdictions=["US", "EU", "UK", "CA"],
                    confidence_score=abs(sentiment_score),
                    legal_precedents=[],
                    mitigation_strategies=["Add factual disclaimers", "Use neutral language"]
                ))
            
            # Entity extraction for person/organization mentions
            entities = await self.nlp_processor.extract_entities(ai_response)
            person_entities = [e for e in entities if e.get("label") in ["PERSON", "ORG"]]
            
            if person_entities and sentiment_score < -0.5:
                nlp_risks.append(LegalRisk(
                    domain=LegalDomain.DEFAMATION,
                    risk_level=LegalRiskLevel.HIGH,
                    description="Negative statements about identified persons/organizations",
                    evidence=[f"Entities: {[e['text'] for e in person_entities]}"],
                    recommendations=["Verify factual accuracy", "Add opinion disclaimers"],
                    jurisdictions=["US", "EU", "UK", "CA"],
                    confidence_score=0.7,
                    legal_precedents=[],
                    mitigation_strategies=["Use alleged/reportedly qualifiers", "Cite sources"]
                ))
            
            # Intent classification for advice-giving
            intent = await self.nlp_processor.classify_intent(ai_response)
            if intent in ["financial_advice", "medical_advice", "legal_advice"]:
                domain_map = {
                    "financial_advice": LegalDomain.FINANCIAL_ADVICE,
                    "medical_advice": LegalDomain.MEDICAL_ADVICE,
                    "legal_advice": LegalDomain.LEGAL_ADVICE
                }
                
                nlp_risks.append(LegalRisk(
                    domain=domain_map[intent],
                    risk_level=LegalRiskLevel.HIGH,
                    description=f"Content classified as {intent.replace('_', ' ')}",
                    evidence=[f"Intent classification: {intent}"],
                    recommendations=[f"Add {intent.replace('_', ' ')} disclaimers"],
                    jurisdictions=["US", "EU", "UK", "CA"],
                    confidence_score=0.8,
                    legal_precedents=[],
                    mitigation_strategies=["Add educational disclaimers", "Suggest professional consultation"]
                ))
            
        except Exception as e:
            self.logger.error(f"Error in NLP risk analysis: {str(e)}")
        
        return nlp_risks
    
    async def _check_jurisdiction_compliance(
        self,
        risks: List[LegalRisk],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Check compliance with jurisdiction-specific rules"""        compliance = {}
        
        # Get user jurisdiction from context
        user_jurisdiction = context.get("user_jurisdiction", "US") if context else "US"
        applicable_jurisdictions = set([user_jurisdiction])
        
        # Add jurisdictions from detected risks
        for risk in risks:
            applicable_jurisdictions.update(risk.jurisdictions)
        
        for jurisdiction in applicable_jurisdictions:
            jurisdiction_rules = self.jurisdiction_rules.get(jurisdiction, {})
            is_compliant = True
            
            for risk in risks:
                if jurisdiction in risk.jurisdictions:
                    # Check jurisdiction-specific compliance rules
                    if risk.domain == LegalDomain.FINANCIAL_ADVICE:
                        if jurisdiction_rules.get("financial_licensing_required", True):
                            if risk.risk_level in [LegalRiskLevel.HIGH, LegalRiskLevel.CRITICAL]:
                                is_compliant = False
                    
                    elif risk.domain == LegalDomain.MEDICAL_ADVICE:
                        if jurisdiction_rules.get("medical_licensing_required", True):
                            if risk.risk_level in [LegalRiskLevel.HIGH, LegalRiskLevel.CRITICAL]:
                                is_compliant = False
                    
                    elif risk.domain == LegalDomain.HATE_SPEECH:
                        if jurisdiction_rules.get("hate_speech_protection", False):
                            if risk.risk_level in [LegalRiskLevel.MEDIUM, LegalRiskLevel.HIGH, LegalRiskLevel.CRITICAL]:
                                is_compliant = False
            
            compliance[jurisdiction] = is_compliant
        
        return compliance
    
    def _calculate_overall_risk(self, risks: List[LegalRisk]) -> LegalRiskLevel:
        """Calculate overall risk level from individual risks"""        if not risks:
            return LegalRiskLevel.NONE
        
        risk_scores = {
            LegalRiskLevel.CRITICAL: 4,
            LegalRiskLevel.HIGH: 3,
            LegalRiskLevel.MEDIUM: 2,
            LegalRiskLevel.LOW: 1,
            LegalRiskLevel.NONE: 0
        }
        
        max_risk_score = max(risk_scores[risk.risk_level] for risk in risks)
        
        for level, score in risk_scores.items():
            if score == max_risk_score:
                return level
        
        return LegalRiskLevel.NONE
    
    def _generate_violations(self, risks: List[LegalRisk]) -> List[Dict[str, Any]]:
        """Generate violation records for high-risk content"""        violations = []
        
        for risk in risks:
            if risk.risk_level in [LegalRiskLevel.HIGH, LegalRiskLevel.CRITICAL]:
                violations.append({
                    "type": "legal_risk",
                    "domain": risk.domain.value,
                    "severity": risk.risk_level.value,
                    "description": risk.description,
                    "evidence": risk.evidence,
                    "jurisdictions": risk.jurisdictions,
                    "confidence": risk.confidence_score
                })
        
        return violations
    
    def _generate_recommendations(self, risks: List[LegalRisk]) -> List[str]:
        """Generate recommendations based on detected risks"""        recommendations = set()
        
        for risk in risks:
            recommendations.update(risk.recommendations)
            recommendations.update(risk.mitigation_strategies)
        
        return list(recommendations)
    
    def _generate_disclaimers(self, risks: List[LegalRisk]) -> List[str]:
        """Generate appropriate legal disclaimers"""        disclaimers = set()
        
        for risk in risks:
            domain_disclaimers = self.disclaimer_templates.get(risk.domain, [])
            disclaimers.update(domain_disclaimers)
        
        return list(disclaimers)
    
    def _calculate_confidence_score(self, risks: List[LegalRisk]) -> float:
        """Calculate confidence score for legal validation"""        if not risks:
            return 1.0
        
        total_confidence = sum(risk.confidence_score for risk in risks)
        return total_confidence / len(risks)
    
    def _get_domain_recommendations(self, domain: LegalDomain) -> List[str]:
        """Get domain-specific recommendations"""        recommendations = {
            LegalDomain.FINANCIAL_ADVICE: [
                "Add financial advice disclaimers",
                "Suggest consulting licensed financial advisors",
                "Include risk warnings"
            ],
            LegalDomain.MEDICAL_ADVICE: [
                "Add medical advice disclaimers",
                "Suggest consulting healthcare professionals",
                "Include health risk warnings"
            ],
            LegalDomain.LEGAL_ADVICE: [
                "Add legal advice disclaimers",
                "Suggest consulting licensed attorneys",
                "Include jurisdiction-specific warnings"
            ],
            LegalDomain.DEFAMATION: [
                "Verify factual accuracy",
                "Add opinion disclaimers",
                "Use neutral language"
            ],
            LegalDomain.HATE_SPEECH: [
                "Remove discriminatory language",
                "Use inclusive terminology",
                "Review content guidelines"
            ]
        }
        
        return recommendations.get(domain, [])
    
    def _get_legal_precedents(self, domain: LegalDomain) -> List[str]:
        """Get relevant legal precedents for domain"""        precedents = {
            LegalDomain.FINANCIAL_ADVICE: [
                "SEC v. Howey Co. (1946)",
                "Investment Advisers Act of 1940"
            ],
            LegalDomain.MEDICAL_ADVICE: [
                "Practice of Medicine statutes",
                "FDA guidance on medical claims"
            ],
            LegalDomain.DEFAMATION: [
                "New York Times Co. v. Sullivan (1964)",
                "Gertz v. Robert Welch, Inc. (1974)"
            ]
        }
        
        return precedents.get(domain, [])
    
    def _get_mitigation_strategies(self, domain: LegalDomain) -> List[str]:
        """Get risk mitigation strategies for domain"""        strategies = {
            LegalDomain.FINANCIAL_ADVICE: [
                "Use educational framing",
                "Add 'not personalized advice' disclaimers",
                "Include risk disclosures"
            ],
            LegalDomain.MEDICAL_ADVICE: [
                "Use general health information framing",
                "Add 'consult healthcare provider' disclaimers",
                "Avoid specific medical recommendations"
            ],
            LegalDomain.LEGAL_ADVICE: [
                "Use general legal information framing",
                "Add 'not legal advice' disclaimers",
                "Include jurisdiction limitations"
            ]
        }
        
        return strategies.get(domain, [])
    
    async def get_risk_assessment_history(
        self,
        days: int = 30,
        domain: Optional[LegalDomain] = None
    ) -> List[Dict[str, Any]]:
        """Get historical risk assessment data"""        try:
            where_clauses = ["created_at >= $1"]
            params = [datetime.now() - timedelta(days=days)]
            
            if domain:
                where_clauses.append("domain = $2")
                params.append(domain.value)
            
            where_clause = " AND ".join(where_clauses)
            
            query = f"""                SELECT * FROM legal_risk_assessments 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT 1000
            """            
            return await self.db_manager.fetch_all(query, *params)
            
        except Exception as e:
            self.logger.error(f"Error fetching risk assessment history: {str(e)}")
            return []
    
    async def update_legal_patterns(self, new_patterns: Dict[LegalDomain, List[Dict[str, Any]]]) -> None:
        """Update legal risk patterns"""        self.legal_patterns.update(new_patterns)
        await self.cache_manager.clear_pattern("legal_validation_*")
        self.logger.info("Legal patterns updated and cache cleared")
    
    async def add_jurisdiction_rules(self, jurisdiction: str, rules: Dict[str, Any]) -> None:
        """Add or update jurisdiction-specific rules"""        self.jurisdiction_rules[jurisdiction] = rules
        await self.cache_manager.clear_pattern("legal_validation_*")
        self.logger.info(f"Jurisdiction rules updated for {jurisdiction}")
    
    def get_supported_jurisdictions(self) -> List[str]:
        """Get list of supported jurisdictions"""        return list(self.jurisdiction_rules.keys())
    
    def get_risk_patterns_by_domain(self, domain: LegalDomain) -> List[Dict[str, Any]]:
        """Get risk patterns for specific legal domain"""        return self.legal_patterns.get(domain, [])
