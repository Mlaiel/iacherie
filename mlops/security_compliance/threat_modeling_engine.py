"""
Threat Modeling Engine
Enterprise threat modeling for ML systems and infrastructure

Features:
- ML-specific threat modeling
- Attack surface analysis
- Risk assessment and mitigation
- Threat scenario generation
- Security architecture validation
- Compliance mapping

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from datetime import datetime
import uuid


class ThreatCategory(Enum):
    """Categories of ML threats"""
    DATA_POISONING = "data_poisoning"
    MODEL_THEFT = "model_theft"
    ADVERSARIAL_ATTACKS = "adversarial_attacks"
    PRIVACY_LEAKAGE = "privacy_leakage"
    BACKDOOR_ATTACKS = "backdoor_attacks"
    INFRASTRUCTURE = "infrastructure"
    SUPPLY_CHAIN = "supply_chain"


class AttackVector(Enum):
    """Attack vectors for ML systems"""
    TRAINING_DATA = "training_data"
    MODEL_INFERENCE = "model_inference"
    MODEL_UPDATES = "model_updates"
    API_ENDPOINTS = "api_endpoints"
    INFRASTRUCTURE = "infrastructure"
    HUMAN_FACTOR = "human_factor"


class RiskLevel(Enum):
    """Risk severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


@dataclass
class ThreatScenario:
    """Individual threat scenario"""
    scenario_id: str
    name: str
    category: ThreatCategory
    attack_vector: AttackVector
    description: str
    likelihood: float  # 0.0 to 1.0
    impact: float     # 0.0 to 1.0
    risk_score: float
    risk_level: RiskLevel
    preconditions: List[str]
    attack_steps: List[str]
    potential_damage: List[str]
    mitigations: List[str]
    detection_methods: List[str]


@dataclass
class AssetInventory:
    """ML asset inventory for threat modeling"""
    asset_id: str
    asset_type: str  # model, data, infrastructure, etc.
    name: str
    description: str
    criticality: RiskLevel
    data_sensitivity: str
    access_points: List[str]
    dependencies: List[str]
    security_controls: List[str]


@dataclass
class ThreatModel:
    """Complete threat model for ML system"""
    model_id: str
    system_name: str
    created_at: datetime
    last_updated: datetime
    scope: str
    assets: List[AssetInventory]
    threats: List[ThreatScenario]
    overall_risk: RiskLevel
    risk_summary: Dict[str, Any]
    recommendations: List[str]


class ThreatModelingEngine:
    """
    Enterprise Threat Modeling Engine
    Comprehensive threat modeling for ML systems
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.threat_models: Dict[str, ThreatModel] = {}
        self.threat_templates: Dict[str, ThreatScenario] = {}
        self.mitigation_catalog: Dict[str, List[str]] = {}
        
        # Initialize threat templates and mitigation catalog
        self._initialize_threat_templates()
        self._initialize_mitigation_catalog()
    
    def _initialize_threat_templates(self):
        """Initialize standard ML threat scenario templates"""
        templates = [
            ThreatScenario(
                scenario_id="TT-001",
                name="Training Data Poisoning",
                category=ThreatCategory.DATA_POISONING,
                attack_vector=AttackVector.TRAINING_DATA,
                description="Attacker injects malicious samples into training data to compromise model behavior",
                likelihood=0.6,
                impact=0.8,
                risk_score=0.48,
                risk_level=RiskLevel.HIGH,
                preconditions=["Access to training data", "Knowledge of model architecture"],
                attack_steps=[
                    "Gain access to training data source",
                    "Inject carefully crafted malicious samples",
                    "Ensure poisoned data passes validation",
                    "Wait for model retraining cycle"
                ],
                potential_damage=[
                    "Model misclassification on target inputs",
                    "Reduced model accuracy",
                    "Biased decision making",
                    "Regulatory violations"
                ],
                mitigations=[
                    "Data validation and sanitization",
                    "Outlier detection in training data",
                    "Federated learning with secure aggregation",
                    "Byzantine-robust training algorithms"
                ],
                detection_methods=[
                    "Statistical analysis of training data",
                    "Model performance monitoring",
                    "Gradient analysis during training"
                ]
            ),
            ThreatScenario(
                scenario_id="TT-002",
                name="Model Extraction Attack",
                category=ThreatCategory.MODEL_THEFT,
                attack_vector=AttackVector.MODEL_INFERENCE,
                description="Attacker queries model to extract its functionality and create a copy",
                likelihood=0.7,
                impact=0.6,
                risk_score=0.42,
                risk_level=RiskLevel.MEDIUM,
                preconditions=["API access to model", "Query budget"],
                attack_steps=[
                    "Design query strategy",
                    "Submit strategic queries to model",
                    "Collect prediction outputs",
                    "Train surrogate model on collected data"
                ],
                potential_damage=[
                    "Intellectual property theft",
                    "Competitive advantage loss",
                    "Revenue impact",
                    "Follow-on attacks using stolen model"
                ],
                mitigations=[
                    "Query rate limiting",
                    "Differential privacy on outputs",
                    "Output obfuscation",
                    "Authentication and access controls"
                ],
                detection_methods=[
                    "Query pattern analysis",
                    "Unusual usage monitoring",
                    "Honeypot queries"
                ]
            ),
            ThreatScenario(
                scenario_id="TT-003",
                name="Adversarial Example Attack",
                category=ThreatCategory.ADVERSARIAL_ATTACKS,
                attack_vector=AttackVector.MODEL_INFERENCE,
                description="Attacker crafts inputs with small perturbations to fool the model",
                likelihood=0.8,
                impact=0.7,
                risk_score=0.56,
                risk_level=RiskLevel.HIGH,
                preconditions=["Knowledge of input format", "Access to model predictions"],
                attack_steps=[
                    "Analyze model input requirements",
                    "Generate adversarial examples",
                    "Test examples against model",
                    "Deploy in real-world scenario"
                ],
                potential_damage=[
                    "Model misclassification",
                    "Safety-critical failures",
                    "Security bypass",
                    "System manipulation"
                ],
                mitigations=[
                    "Adversarial training",
                    "Input validation and sanitization",
                    "Ensemble methods",
                    "Randomized smoothing"
                ],
                detection_methods=[
                    "Statistical input analysis",
                    "Prediction confidence monitoring",
                    "Adversarial detectors"
                ]
            ),
            ThreatScenario(
                scenario_id="TT-004",
                name="Membership Inference Attack",
                category=ThreatCategory.PRIVACY_LEAKAGE,
                attack_vector=AttackVector.MODEL_INFERENCE,
                description="Attacker determines if specific data was used in model training",
                likelihood=0.5,
                impact=0.8,
                risk_score=0.40,
                risk_level=RiskLevel.MEDIUM,
                preconditions=["Model access", "Sample data points"],
                attack_steps=[
                    "Collect target data samples",
                    "Query model with samples",
                    "Analyze prediction confidence patterns",
                    "Infer membership probability"
                ],
                potential_damage=[
                    "Privacy violations",
                    "Regulatory compliance issues",
                    "Sensitive data exposure",
                    "Reputation damage"
                ],
                mitigations=[
                    "Differential privacy",
                    "Model regularization",
                    "Output noise injection",
                    "Limited query access"
                ],
                detection_methods=[
                    "Query pattern monitoring",
                    "Privacy audit tools",
                    "Statistical testing"
                ]
            )
        ]
        
        for template in templates:
            self.threat_templates[template.scenario_id] = template
    
    def _initialize_mitigation_catalog(self):
        """Initialize catalog of security mitigations"""
        self.mitigation_catalog = {
            "data_protection": [
                "Implement data encryption at rest and in transit",
                "Use secure data pipelines with validation",
                "Apply data anonymization techniques",
                "Implement access controls and audit logging"
            ],
            "model_security": [
                "Use model encryption and secure storage", 
                "Implement model versioning and integrity checks",
                "Apply differential privacy to model outputs",
                "Use federated learning for sensitive data"
            ],
            "infrastructure": [
                "Secure container deployment",
                "Network segmentation and firewalls",
                "Regular security patching",
                "Intrusion detection systems"
            ],
            "access_control": [
                "Multi-factor authentication",
                "Role-based access control",
                "API rate limiting and quotas",
                "Session management and timeout"
            ],
            "monitoring": [
                "Real-time threat detection",
                "Model performance monitoring",
                "Audit trail and logging",
                "Anomaly detection systems"
            ]
        }
    
    async def create_threat_model(
        self,
        system_name: str,
        scope: str,
        assets: List[AssetInventory]
    ) -> str:
        """Create new threat model for ML system"""
        try:
            model_id = str(uuid.uuid4())
            
            # Generate threat scenarios based on assets
            threats = await self._generate_threat_scenarios(assets)
            
            # Calculate overall risk
            overall_risk = self._calculate_overall_risk(threats)
            
            # Generate risk summary
            risk_summary = self._generate_risk_summary(threats)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(threats, assets)
            
            # Create threat model
            threat_model = ThreatModel(
                model_id=model_id,
                system_name=system_name,
                created_at=datetime.now(),
                last_updated=datetime.now(),
                scope=scope,
                assets=assets,
                threats=threats,
                overall_risk=overall_risk,
                risk_summary=risk_summary,
                recommendations=recommendations
            )
            
            self.threat_models[model_id] = threat_model
            
            self.logger.info(f"Threat model created for system {system_name}")
            return model_id
            
        except Exception as e:
            self.logger.error(f"Failed to create threat model: {str(e)}")
            raise
    
    async def analyze_attack_surface(
        self,
        model_id: str
    ) -> Dict[str, Any]:
        """Analyze attack surface of ML system"""
        try:
            threat_model = self.threat_models.get(model_id)
            if not threat_model:
                raise ValueError(f"Threat model {model_id} not found")
            
            attack_surface = {
                "model_id": model_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "attack_vectors": {},
                "entry_points": [],
                "critical_assets": [],
                "exposure_score": 0.0,
                "recommendations": []
            }
            
            # Analyze attack vectors
            vector_analysis = {}
            for threat in threat_model.threats:
                vector = threat.attack_vector.value
                if vector not in vector_analysis:
                    vector_analysis[vector] = {
                        "threat_count": 0,
                        "avg_risk_score": 0.0,
                        "max_impact": 0.0,
                        "scenarios": []
                    }
                
                vector_analysis[vector]["threat_count"] += 1
                vector_analysis[vector]["scenarios"].append(threat.scenario_id)
                vector_analysis[vector]["max_impact"] = max(
                    vector_analysis[vector]["max_impact"], threat.impact
                )
            
            # Calculate average risk scores for vectors
            for vector, data in vector_analysis.items():
                relevant_threats = [t for t in threat_model.threats if t.attack_vector.value == vector]
                data["avg_risk_score"] = sum(t.risk_score for t in relevant_threats) / len(relevant_threats)
            
            attack_surface["attack_vectors"] = vector_analysis
            
            # Identify entry points from assets
            for asset in threat_model.assets:
                attack_surface["entry_points"].extend(asset.access_points)
            
            # Identify critical assets
            critical_assets = [
                asset for asset in threat_model.assets
                if asset.criticality in [RiskLevel.CRITICAL, RiskLevel.HIGH]
            ]
            attack_surface["critical_assets"] = [
                {"asset_id": a.asset_id, "name": a.name, "criticality": a.criticality.value}
                for a in critical_assets
            ]
            
            # Calculate exposure score
            attack_surface["exposure_score"] = self._calculate_exposure_score(threat_model)
            
            # Generate attack surface recommendations
            attack_surface["recommendations"] = self._generate_attack_surface_recommendations(
                vector_analysis, critical_assets
            )
            
            return attack_surface
            
        except Exception as e:
            self.logger.error(f"Attack surface analysis failed: {str(e)}")
            raise
    
    async def assess_threat_likelihood(
        self,
        model_id: str,
        threat_scenario_id: str,
        environmental_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess likelihood of specific threat scenario"""
        try:
            threat_model = self.threat_models.get(model_id)
            if not threat_model:
                raise ValueError(f"Threat model {model_id} not found")
            
            # Find the threat scenario
            threat_scenario = None
            for threat in threat_model.threats:
                if threat.scenario_id == threat_scenario_id:
                    threat_scenario = threat
                    break
            
            if not threat_scenario:
                raise ValueError(f"Threat scenario {threat_scenario_id} not found")
            
            # Base likelihood from template
            base_likelihood = threat_scenario.likelihood
            
            # Adjust based on environmental factors
            adjusted_likelihood = base_likelihood
            
            # Factor in security controls
            if environmental_factors.get("security_controls", 0) > 5:
                adjusted_likelihood *= 0.7
            elif environmental_factors.get("security_controls", 0) < 2:
                adjusted_likelihood *= 1.3
            
            # Factor in exposure level
            exposure = environmental_factors.get("exposure_level", "medium")
            if exposure == "high":
                adjusted_likelihood *= 1.5
            elif exposure == "low":
                adjusted_likelihood *= 0.6
            
            # Factor in threat actor capability
            actor_capability = environmental_factors.get("threat_actor_capability", "medium")
            if actor_capability == "advanced":
                adjusted_likelihood *= 1.4
            elif actor_capability == "basic":
                adjusted_likelihood *= 0.8
            
            # Cap likelihood at 1.0
            adjusted_likelihood = min(1.0, adjusted_likelihood)
            
            # Recalculate risk score
            new_risk_score = adjusted_likelihood * threat_scenario.impact
            new_risk_level = self._determine_risk_level(new_risk_score)
            
            return {
                "threat_scenario_id": threat_scenario_id,
                "base_likelihood": base_likelihood,
                "adjusted_likelihood": adjusted_likelihood,
                "impact": threat_scenario.impact,
                "original_risk_score": threat_scenario.risk_score,
                "adjusted_risk_score": new_risk_score,
                "original_risk_level": threat_scenario.risk_level.value,
                "adjusted_risk_level": new_risk_level.value,
                "environmental_factors": environmental_factors,
                "likelihood_adjustment_factors": {
                    "security_controls": environmental_factors.get("security_controls", 0),
                    "exposure_level": exposure,
                    "threat_actor_capability": actor_capability
                }
            }
            
        except Exception as e:
            self.logger.error(f"Threat likelihood assessment failed: {str(e)}")
            raise
    
    async def generate_mitigation_plan(
        self,
        model_id: str,
        priority_threats: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive mitigation plan"""
        try:
            threat_model = self.threat_models.get(model_id)
            if not threat_model:
                raise ValueError(f"Threat model {model_id} not found")
            
            # Select threats to mitigate
            threats_to_mitigate = threat_model.threats
            if priority_threats:
                threats_to_mitigate = [
                    t for t in threat_model.threats 
                    if t.scenario_id in priority_threats
                ]
            
            # Sort by risk score (highest first)
            threats_to_mitigate.sort(key=lambda x: x.risk_score, reverse=True)
            
            mitigation_plan = {
                "plan_id": str(uuid.uuid4()),
                "model_id": model_id,
                "generated_at": datetime.now().isoformat(),
                "total_threats": len(threats_to_mitigate),
                "mitigation_strategies": [],
                "implementation_timeline": {},
                "cost_estimate": {},
                "risk_reduction": {}
            }
            
            # Generate mitigation strategies for each threat
            for threat in threats_to_mitigate:
                strategy = {
                    "threat_scenario_id": threat.scenario_id,
                    "threat_name": threat.name,
                    "current_risk_level": threat.risk_level.value,
                    "current_risk_score": threat.risk_score,
                    "recommended_mitigations": threat.mitigations,
                    "implementation_priority": self._determine_mitigation_priority(threat),
                    "estimated_risk_reduction": self._estimate_risk_reduction(threat),
                    "implementation_complexity": self._assess_implementation_complexity(threat)
                }
                mitigation_plan["mitigation_strategies"].append(strategy)
            
            # Generate implementation timeline
            mitigation_plan["implementation_timeline"] = self._generate_implementation_timeline(
                threats_to_mitigate
            )
            
            # Estimate costs (simplified)
            mitigation_plan["cost_estimate"] = self._estimate_mitigation_costs(
                threats_to_mitigate
            )
            
            # Calculate total risk reduction
            mitigation_plan["risk_reduction"] = self._calculate_total_risk_reduction(
                threats_to_mitigate
            )
            
            return mitigation_plan
            
        except Exception as e:
            self.logger.error(f"Mitigation plan generation failed: {str(e)}")
            raise
    
    async def validate_security_architecture(
        self,
        model_id: str,
        architecture_components: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate security architecture against threat model"""
        try:
            threat_model = self.threat_models.get(model_id)
            if not threat_model:
                raise ValueError(f"Threat model {model_id} not found")
            
            validation_result = {
                "validation_id": str(uuid.uuid4()),
                "model_id": model_id,
                "validated_at": datetime.now().isoformat(),
                "overall_coverage": 0.0,
                "coverage_by_threat": {},
                "missing_controls": [],
                "recommendations": [],
                "architecture_gaps": []
            }
            
            # Analyze coverage for each threat
            total_coverage = 0.0
            for threat in threat_model.threats:
                coverage = self._assess_threat_coverage(threat, architecture_components)
                validation_result["coverage_by_threat"][threat.scenario_id] = {
                    "threat_name": threat.name,
                    "coverage_percentage": coverage,
                    "risk_level": threat.risk_level.value,
                    "covered_mitigations": [],
                    "missing_mitigations": []
                }
                
                # Identify covered and missing mitigations
                for mitigation in threat.mitigations:
                    if self._is_mitigation_implemented(mitigation, architecture_components):
                        validation_result["coverage_by_threat"][threat.scenario_id]["covered_mitigations"].append(mitigation)
                    else:
                        validation_result["coverage_by_threat"][threat.scenario_id]["missing_mitigations"].append(mitigation)
                        if mitigation not in validation_result["missing_controls"]:
                            validation_result["missing_controls"].append(mitigation)
                
                total_coverage += coverage
            
            # Calculate overall coverage
            validation_result["overall_coverage"] = total_coverage / len(threat_model.threats) if threat_model.threats else 0.0
            
            # Identify architecture gaps
            validation_result["architecture_gaps"] = self._identify_architecture_gaps(
                threat_model, architecture_components
            )
            
            # Generate recommendations
            validation_result["recommendations"] = self._generate_architecture_recommendations(
                validation_result["missing_controls"],
                validation_result["architecture_gaps"],
                validation_result["overall_coverage"]
            )
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Security architecture validation failed: {str(e)}")
            raise
    
    async def get_threat_model(self, model_id: str) -> Optional[ThreatModel]:
        """Get threat model by ID"""
        return self.threat_models.get(model_id)
    
    async def update_threat_model(
        self,
        model_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update existing threat model"""
        try:
            threat_model = self.threat_models.get(model_id)
            if not threat_model:
                return False
            
            # Update specified fields
            if "assets" in updates:
                threat_model.assets = updates["assets"]
                # Regenerate threats based on new assets
                threat_model.threats = await self._generate_threat_scenarios(threat_model.assets)
            
            if "scope" in updates:
                threat_model.scope = updates["scope"]
            
            # Recalculate risk metrics
            threat_model.overall_risk = self._calculate_overall_risk(threat_model.threats)
            threat_model.risk_summary = self._generate_risk_summary(threat_model.threats)
            threat_model.recommendations = self._generate_recommendations(threat_model.threats, threat_model.assets)
            threat_model.last_updated = datetime.now()
            
            self.threat_models[model_id] = threat_model
            
            self.logger.info(f"Threat model {model_id} updated")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update threat model: {str(e)}")
            return False
    
    # Private methods for threat modeling logic
    
    async def _generate_threat_scenarios(self, assets: List[AssetInventory]) -> List[ThreatScenario]:
        """Generate threat scenarios based on system assets"""
        scenarios = []
        
        # Use templates as base and customize based on assets
        for template in self.threat_templates.values():
            # Check if template is relevant to the assets
            if self._is_template_relevant(template, assets):
                # Create customized scenario
                custom_scenario = ThreatScenario(
                    scenario_id=f"{template.scenario_id}_{len(scenarios)}",
                    name=template.name,
                    category=template.category,
                    attack_vector=template.attack_vector,
                    description=template.description,
                    likelihood=self._adjust_likelihood_for_assets(template, assets),
                    impact=self._adjust_impact_for_assets(template, assets),
                    risk_score=0.0,  # Will be calculated below
                    risk_level=RiskLevel.MEDIUM,  # Will be calculated below
                    preconditions=template.preconditions,
                    attack_steps=template.attack_steps,
                    potential_damage=template.potential_damage,
                    mitigations=template.mitigations,
                    detection_methods=template.detection_methods
                )
                
                # Calculate risk score and level
                custom_scenario.risk_score = custom_scenario.likelihood * custom_scenario.impact
                custom_scenario.risk_level = self._determine_risk_level(custom_scenario.risk_score)
                
                scenarios.append(custom_scenario)
        
        return scenarios
    
    def _is_template_relevant(self, template: ThreatScenario, assets: List[AssetInventory]) -> bool:
        """Check if threat template is relevant to the assets"""
        # Check if any assets are vulnerable to this threat type
        for asset in assets:
            if template.category == ThreatCategory.DATA_POISONING and "data" in asset.asset_type.lower():
                return True
            elif template.category == ThreatCategory.MODEL_THEFT and "model" in asset.asset_type.lower():
                return True
            elif template.category == ThreatCategory.ADVERSARIAL_ATTACKS and "model" in asset.asset_type.lower():
                return True
            elif template.category == ThreatCategory.PRIVACY_LEAKAGE and asset.data_sensitivity in ["sensitive", "personal"]:
                return True
            elif template.category == ThreatCategory.INFRASTRUCTURE and "infrastructure" in asset.asset_type.lower():
                return True
        
        return True  # Default to relevant
    
    def _adjust_likelihood_for_assets(self, template: ThreatScenario, assets: List[AssetInventory]) -> float:
        """Adjust threat likelihood based on system assets"""
        base_likelihood = template.likelihood
        
        # Adjust based on asset criticality and security controls
        high_value_assets = [a for a in assets if a.criticality in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        if high_value_assets:
            base_likelihood *= 1.2  # Higher likelihood for high-value assets
        
        # Adjust based on number of access points
        total_access_points = sum(len(a.access_points) for a in assets)
        if total_access_points > 10:
            base_likelihood *= 1.1  # More access points = higher likelihood
        
        return min(1.0, base_likelihood)
    
    def _adjust_impact_for_assets(self, template: ThreatScenario, assets: List[AssetInventory]) -> float:
        """Adjust threat impact based on system assets"""
        base_impact = template.impact
        
        # Adjust based on asset criticality
        critical_assets = [a for a in assets if a.criticality == RiskLevel.CRITICAL]
        if critical_assets:
            base_impact *= 1.3  # Higher impact for critical assets
        
        # Adjust based on data sensitivity
        sensitive_assets = [a for a in assets if a.data_sensitivity in ["sensitive", "personal"]]
        if sensitive_assets:
            base_impact *= 1.2  # Higher impact for sensitive data
        
        return min(1.0, base_impact)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Determine risk level from risk score"""
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        elif risk_score >= 0.2:
            return RiskLevel.LOW
        else:
            return RiskLevel.NEGLIGIBLE
    
    def _calculate_overall_risk(self, threats: List[ThreatScenario]) -> RiskLevel:
        """Calculate overall risk level from all threats"""
        if not threats:
            return RiskLevel.LOW
        
        # Find highest risk level
        max_risk_score = max(threat.risk_score for threat in threats)
        return self._determine_risk_level(max_risk_score)
    
    def _generate_risk_summary(self, threats: List[ThreatScenario]) -> Dict[str, Any]:
        """Generate risk summary from threats"""
        summary = {
            "total_threats": len(threats),
            "risk_distribution": {level.value: 0 for level in RiskLevel},
            "category_distribution": {cat.value: 0 for cat in ThreatCategory},
            "average_risk_score": 0.0,
            "max_risk_score": 0.0,
            "high_priority_threats": 0
        }
        
        if threats:
            for threat in threats:
                summary["risk_distribution"][threat.risk_level.value] += 1
                summary["category_distribution"][threat.category.value] += 1
                
                if threat.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    summary["high_priority_threats"] += 1
            
            summary["average_risk_score"] = sum(t.risk_score for t in threats) / len(threats)
            summary["max_risk_score"] = max(t.risk_score for t in threats)
        
        return summary
    
    def _generate_recommendations(self, threats: List[ThreatScenario], assets: List[AssetInventory]) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if not threats:
            return ["No threats identified - maintain current security posture"]
        
        # High-priority threat recommendations
        high_risk_threats = [t for t in threats if t.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]
        if high_risk_threats:
            recommendations.append(f"Address {len(high_risk_threats)} high-priority threats immediately")
        
        # Category-specific recommendations
        threat_categories = set(t.category for t in threats)
        if ThreatCategory.DATA_POISONING in threat_categories:
            recommendations.append("Implement robust data validation and anomaly detection")
        if ThreatCategory.ADVERSARIAL_ATTACKS in threat_categories:
            recommendations.append("Deploy adversarial defense mechanisms")
        if ThreatCategory.PRIVACY_LEAKAGE in threat_categories:
            recommendations.append("Enhance privacy-preserving techniques")
        
        # Asset-based recommendations
        critical_assets = [a for a in assets if a.criticality == RiskLevel.CRITICAL]
        if critical_assets:
            recommendations.append("Implement additional security controls for critical assets")
        
        return recommendations
    
    def _calculate_exposure_score(self, threat_model: ThreatModel) -> float:
        """Calculate system exposure score"""
        if not threat_model.threats:
            return 0.0
        
        # Factor in threat count, risk scores, and asset exposure
        threat_factor = len(threat_model.threats) / 10.0  # Normalize
        risk_factor = sum(t.risk_score for t in threat_model.threats) / len(threat_model.threats)
        
        access_points = sum(len(a.access_points) for a in threat_model.assets)
        access_factor = min(1.0, access_points / 20.0)  # Normalize
        
        return min(1.0, (threat_factor + risk_factor + access_factor) / 3.0)
    
    def _generate_attack_surface_recommendations(
        self,
        vector_analysis: Dict[str, Any],
        critical_assets: List[AssetInventory]
    ) -> List[str]:
        """Generate attack surface reduction recommendations"""
        recommendations = []
        
        # Analyze high-risk attack vectors
        for vector, data in vector_analysis.items():
            if data["avg_risk_score"] > 0.6:
                recommendations.append(f"Reduce exposure through {vector.replace('_', ' ')} attack vector")
        
        # Critical asset recommendations
        if critical_assets:
            recommendations.append("Implement additional access controls for critical assets")
            recommendations.append("Consider network segmentation for critical asset protection")
        
        return recommendations
    
    def _determine_mitigation_priority(self, threat: ThreatScenario) -> str:
        """Determine implementation priority for threat mitigation"""
        if threat.risk_level == RiskLevel.CRITICAL:
            return "immediate"
        elif threat.risk_level == RiskLevel.HIGH:
            return "high"
        elif threat.risk_level == RiskLevel.MEDIUM:
            return "medium"
        else:
            return "low"
    
    def _estimate_risk_reduction(self, threat: ThreatScenario) -> float:
        """Estimate potential risk reduction from implementing mitigations"""
        # Simplified estimation - in practice would be more sophisticated
        mitigation_count = len(threat.mitigations)
        if mitigation_count >= 4:
            return 0.8  # High reduction
        elif mitigation_count >= 2:
            return 0.6  # Medium reduction
        else:
            return 0.3  # Low reduction
    
    def _assess_implementation_complexity(self, threat: ThreatScenario) -> str:
        """Assess complexity of implementing mitigations"""
        # Simplified assessment based on number and type of mitigations
        mitigation_count = len(threat.mitigations)
        if mitigation_count > 3:
            return "high"
        elif mitigation_count > 1:
            return "medium"
        else:
            return "low"
    
    def _generate_implementation_timeline(self, threats: List[ThreatScenario]) -> Dict[str, List[str]]:
        """Generate implementation timeline for mitigations"""
        timeline = {
            "immediate": [],
            "short_term": [],  # 1-3 months
            "medium_term": [], # 3-6 months
            "long_term": []    # 6+ months
        }
        
        for threat in threats:
            priority = self._determine_mitigation_priority(threat)
            complexity = self._assess_implementation_complexity(threat)
            
            if priority == "immediate":
                timeline["immediate"].append(threat.scenario_id)
            elif complexity == "low":
                timeline["short_term"].append(threat.scenario_id)
            elif complexity == "medium":
                timeline["medium_term"].append(threat.scenario_id)
            else:
                timeline["long_term"].append(threat.scenario_id)
        
        return timeline
    
    def _estimate_mitigation_costs(self, threats: List[ThreatScenario]) -> Dict[str, Any]:
        """Estimate costs for implementing mitigations"""
        # Simplified cost estimation
        total_cost = 0
        cost_breakdown = {}
        
        for threat in threats:
            complexity = self._assess_implementation_complexity(threat)
            
            if complexity == "high":
                cost = 50000  # High complexity
            elif complexity == "medium":
                cost = 25000  # Medium complexity
            else:
                cost = 10000  # Low complexity
            
            cost_breakdown[threat.scenario_id] = cost
            total_cost += cost
        
        return {
            "total_estimated_cost": total_cost,
            "cost_by_threat": cost_breakdown,
            "currency": "USD",
            "estimation_confidence": "low"  # Simplified estimation
        }
    
    def _calculate_total_risk_reduction(self, threats: List[ThreatScenario]) -> Dict[str, Any]:
        """Calculate total risk reduction from implementing all mitigations"""
        if not threats:
            return {}
        
        current_risk = sum(t.risk_score for t in threats)
        
        # Estimate risk after mitigation
        reduced_risk = 0.0
        for threat in threats:
            reduction_factor = self._estimate_risk_reduction(threat)
            reduced_risk += threat.risk_score * (1 - reduction_factor)
        
        risk_reduction_percentage = ((current_risk - reduced_risk) / current_risk) * 100
        
        return {
            "current_total_risk": current_risk,
            "projected_residual_risk": reduced_risk,
            "risk_reduction_percentage": risk_reduction_percentage,
            "high_priority_threats_mitigated": len([t for t in threats if t.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]])
        }
    
    def _assess_threat_coverage(self, threat: ThreatScenario, architecture_components: List[Dict[str, Any]]) -> float:
        """Assess how well architecture covers a specific threat"""
        covered_mitigations = 0
        total_mitigations = len(threat.mitigations)
        
        if total_mitigations == 0:
            return 100.0
        
        for mitigation in threat.mitigations:
            if self._is_mitigation_implemented(mitigation, architecture_components):
                covered_mitigations += 1
        
        return (covered_mitigations / total_mitigations) * 100.0
    
    def _is_mitigation_implemented(self, mitigation: str, architecture_components: List[Dict[str, Any]]) -> bool:
        """Check if a mitigation is implemented in the architecture"""
        # Simplified check - in practice would be more sophisticated
        mitigation_lower = mitigation.lower()
        
        for component in architecture_components:
            component_desc = f"{component.get('name', '')} {component.get('description', '')} {component.get('type', '')}".lower()
            
            # Check for key mitigation concepts
            if any(keyword in component_desc for keyword in ["encryption", "authentication", "validation", "monitoring", "firewall"]):
                if any(keyword in mitigation_lower for keyword in ["encrypt", "auth", "valid", "monitor", "firewall"]):
                    return True
        
        return False
    
    def _identify_architecture_gaps(
        self,
        threat_model: ThreatModel,
        architecture_components: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify gaps in security architecture"""
        gaps = []
        
        # Check for missing security layers
        component_types = set(c.get("type", "").lower() for c in architecture_components)
        
        required_components = ["firewall", "authentication", "encryption", "monitoring", "logging"]
        for required in required_components:
            if not any(required in comp_type for comp_type in component_types):
                gaps.append({
                    "type": "missing_component",
                    "component": required,
                    "severity": "medium",
                    "description": f"Missing {required} component in architecture"
                })
        
        return gaps
    
    def _generate_architecture_recommendations(
        self,
        missing_controls: List[str],
        architecture_gaps: List[Dict[str, Any]],
        overall_coverage: float
    ) -> List[str]:
        """Generate architecture improvement recommendations"""
        recommendations = []
        
        if overall_coverage < 0.7:
            recommendations.append("Overall security coverage is below recommended threshold (70%)")
        
        if missing_controls:
            recommendations.append(f"Implement {len(missing_controls)} missing security controls")
        
        for gap in architecture_gaps:
            if gap["severity"] == "high":
                recommendations.append(f"URGENT: Address {gap['description']}")
            else:
                recommendations.append(f"Consider: {gap['description']}")
        
        return recommendations


# Global instance
threat_modeling_engine = ThreatModelingEngine()