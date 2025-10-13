"""
⚖️ Creator Compliance Service
Advanced creator compliance and regulatory management

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class ComplianceStatus(Enum):
    """Compliance status types"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"
    UNDER_INVESTIGATION = "under_investigation"


class ComplianceRuleType(Enum):
    """Types of compliance rules"""
    CONTENT_GUIDELINES = "content_guidelines"
    DISCLOSURE_REQUIREMENTS = "disclosure_requirements"
    DATA_PROTECTION = "data_protection"
    ADVERTISING_STANDARDS = "advertising_standards"
    PLATFORM_POLICIES = "platform_policies"
    LEGAL_REQUIREMENTS = "legal_requirements"


class ViolationSeverity(Enum):
    """Violation severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CreatorComplianceService:
    """Advanced creator compliance and regulatory management service"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_rules: Dict[str, Dict[str, Any]] = {}
        self.creator_profiles: Dict[str, Dict[str, Any]] = {}
        self.violations: List[Dict[str, Any]] = []
        self.compliance_checks: List[Dict[str, Any]] = []
        self.disclosure_templates: Dict[str, Dict[str, Any]] = {}
        
        self._initialize_compliance_rules()
        self._initialize_disclosure_templates()
        self.logger.info("✅ CreatorComplianceService initialized")
    
    def _initialize_compliance_rules(self):
        """Initialize compliance rules database"""
        self.compliance_rules = {
            "sponsored_disclosure": {
                "rule_id": "sponsored_disclosure",
                "name": "Divulgation de contenu sponsorisé",
                "type": ComplianceRuleType.DISCLOSURE_REQUIREMENTS,
                "description": "Les créateurs doivent divulguer clairement tout contenu sponsorisé",
                "requirements": [
                    "Utiliser #pub, #sponsorisé ou #partenariat",
                    "Mention claire et visible",
                    "Divulgation au début du contenu"
                ],
                "applicable_platforms": ["instagram", "youtube", "tiktok", "facebook"],
                "mandatory": True,
                "penalties": ["warning", "content_removal", "account_suspension"]
            },
            "data_collection_consent": {
                "rule_id": "data_collection_consent",
                "name": "Consentement collecte de données",
                "type": ComplianceRuleType.DATA_PROTECTION,
                "description": "Obtenir le consentement avant la collecte de données RGPD",
                "requirements": [
                    "Consentement explicite requis",
                    "Information claire sur l'utilisation",
                    "Option de retrait disponible"
                ],
                "applicable_platforms": ["all"],
                "mandatory": True,
                "penalties": ["fine", "data_deletion", "legal_action"]
            },
            "minors_protection": {
                "rule_id": "minors_protection",
                "name": "Protection des mineurs",
                "type": ComplianceRuleType.CONTENT_GUIDELINES,
                "description": "Contenu approprié pour les audiences mineures",
                "requirements": [
                    "Pas de contenu explicite",
                    "Langage approprié",
                    "Pas de promotion de substances"
                ],
                "applicable_platforms": ["youtube", "tiktok"],
                "mandatory": True,
                "penalties": ["demonetization", "age_restriction", "channel_termination"]
            },
            "advertising_transparency": {
                "rule_id": "advertising_transparency",
                "name": "Transparence publicitaire",
                "type": ComplianceRuleType.ADVERTISING_STANDARDS,
                "description": "Respect des standards publicitaires",
                "requirements": [
                    "Publicité clairement identifiée",
                    "Pas de claims mensongers",
                    "Respect des régulations sectorielles"
                ],
                "applicable_platforms": ["all"],
                "mandatory": True,
                "penalties": ["ad_removal", "account_restriction", "legal_compliance"]
            }
        }
    
    def _initialize_disclosure_templates(self):
        """Initialize disclosure templates"""
        self.disclosure_templates = {
            "sponsored_post": {
                "template_id": "sponsored_post",
                "name": "Post sponsorisé",
                "platforms": ["instagram", "facebook"],
                "templates": {
                    "fr": "#Pub - Ce contenu est sponsorisé par {brand_name}. Merci de soutenir les marques qui me permettent de créer du contenu !",
                    "en": "#Ad - This content is sponsored by {brand_name}. Thank you for supporting the brands that make my content possible!"
                },
                "placement": "beginning",
                "visibility": "prominent"
            },
            "affiliate_link": {
                "template_id": "affiliate_link",
                "name": "Lien d'affiliation",
                "platforms": ["youtube", "blog"],
                "templates": {
                    "fr": "⚠️ Liens d'affiliation : J'utilise des liens d'affiliation dans cette description. Je peux recevoir une commission si vous effectuez un achat via ces liens.",
                    "en": "⚠️ Affiliate Links: I use affiliate links in this description. I may receive a commission if you make a purchase through these links."
                },
                "placement": "description",
                "visibility": "clear"
            },
            "gifted_product": {
                "template_id": "gifted_product",
                "name": "Produit offert",
                "platforms": ["instagram", "tiktok"],
                "templates": {
                    "fr": "#Cadeau - Ce produit m'a été offert par {brand_name}. Mon avis reste authentique et personnel.",
                    "en": "#Gifted - This product was gifted to me by {brand_name}. My opinion remains authentic and personal."
                },
                "placement": "beginning",
                "visibility": "hashtag"
            }
        }
    
    async def check_creator_compliance(self, creator_id: str) -> Dict[str, Any]:
        """Perform comprehensive compliance check for creator"""
        try:
            check_id = str(uuid.uuid4())
            
            # Get creator profile
            creator_profile = self.creator_profiles.get(creator_id, {
                "creator_id": creator_id,
                "compliance_score": 85,
                "last_review": datetime.utcnow().isoformat(),
                "platforms": ["instagram", "youtube"],
                "content_categories": ["lifestyle", "technology"],
                "audience_demographics": {"minors_percentage": 15}
            })
            
            # Perform compliance checks
            compliance_results = []
            overall_status = ComplianceStatus.COMPLIANT
            
            for rule_id, rule in self.compliance_rules.items():
                rule_result = await self._check_compliance_rule(creator_profile, rule)
                compliance_results.append(rule_result)
                
                if rule_result["status"] != ComplianceStatus.COMPLIANT.value:
                    if rule["mandatory"]:
                        overall_status = ComplianceStatus.NON_COMPLIANT
                    elif overall_status == ComplianceStatus.COMPLIANT:
                        overall_status = ComplianceStatus.REQUIRES_ACTION
            
            # Calculate compliance score
            compliant_rules = sum(1 for result in compliance_results 
                                if result["status"] == ComplianceStatus.COMPLIANT.value)
            compliance_score = (compliant_rules / len(compliance_results)) * 100
            
            check_result = {
                "check_id": check_id,
                "creator_id": creator_id,
                "overall_status": overall_status.value,
                "compliance_score": compliance_score,
                "rule_checks": compliance_results,
                "recommendations": self._generate_compliance_recommendations(compliance_results),
                "next_review_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.compliance_checks.append(check_result)
            
            return {
                "success": True,
                "compliance_check": check_result
            }
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {str(e)}")
            return {
                "success": False,
                "error": "Vérification de conformité échouée",
                "message": str(e)
            }
    
    async def _check_compliance_rule(
        self, 
        creator_profile: Dict[str, Any], 
        rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check specific compliance rule for creator"""
        
        # Simulate rule checking logic
        import random
        
        # Check if rule applies to creator's platforms
        creator_platforms = creator_profile.get("platforms", [])
        rule_platforms = rule.get("applicable_platforms", [])
        
        if "all" not in rule_platforms:
            if not any(platform in rule_platforms for platform in creator_platforms):
                return {
                    "rule_id": rule["rule_id"],
                    "rule_name": rule["name"],
                    "status": ComplianceStatus.COMPLIANT.value,
                    "reason": "Règle non applicable aux plateformes du créateur",
                    "applicable": False
                }
        
        # Simulate compliance status based on rule type
        compliance_probability = 0.8  # 80% compliance rate
        
        if rule["type"] == ComplianceRuleType.DISCLOSURE_REQUIREMENTS:
            # Check disclosure compliance
            is_compliant = random.random() < compliance_probability
        elif rule["type"] == ComplianceRuleType.DATA_PROTECTION:
            # Check GDPR compliance
            is_compliant = random.random() < 0.9  # Higher compliance for GDPR
        elif rule["type"] == ComplianceRuleType.CONTENT_GUIDELINES:
            # Check content guidelines
            minors_percentage = creator_profile.get("audience_demographics", {}).get("minors_percentage", 0)
            if minors_percentage > 20:
                is_compliant = random.random() < 0.95  # Stricter for minor audiences
            else:
                is_compliant = random.random() < compliance_probability
        else:
            is_compliant = random.random() < compliance_probability
        
        if is_compliant:
            status = ComplianceStatus.COMPLIANT
            reason = "Conforme aux exigences"
        else:
            if rule["mandatory"]:
                status = ComplianceStatus.NON_COMPLIANT
                reason = "Non conforme - Action requise"
            else:
                status = ComplianceStatus.REQUIRES_ACTION
                reason = "Amélioration recommandée"
        
        return {
            "rule_id": rule["rule_id"],
            "rule_name": rule["name"],
            "status": status.value,
            "reason": reason,
            "applicable": True,
            "requirements": rule["requirements"],
            "penalties": rule.get("penalties", [])
        }
    
    def _generate_compliance_recommendations(
        self, 
        compliance_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate compliance improvement recommendations"""
        
        recommendations = []
        
        for result in compliance_results:
            if result["status"] != ComplianceStatus.COMPLIANT.value and result["applicable"]:
                rule_id = result["rule_id"]
                
                if rule_id == "sponsored_disclosure":
                    recommendations.append({
                        "priority": "high",
                        "action": "Améliorer les divulgations sponsorisées",
                        "description": "Ajouter des mentions #pub claires et visibles",
                        "template_id": "sponsored_post"
                    })
                elif rule_id == "data_collection_consent":
                    recommendations.append({
                        "priority": "critical",
                        "action": "Mettre en conformité RGPD",
                        "description": "Implémenter un système de consentement valide",
                        "template_id": None
                    })
                elif rule_id == "minors_protection":
                    recommendations.append({
                        "priority": "high",
                        "action": "Adapter le contenu à l'audience",
                        "description": "Réviser le contenu pour respecter les guidelines mineurs",
                        "template_id": None
                    })
        
        return recommendations
    
    async def report_violation(
        self, 
        creator_id: str, 
        rule_id: str,
        severity: ViolationSeverity,
        description: str,
        evidence: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Report compliance violation"""
        try:
            violation_id = str(uuid.uuid4())
            
            violation = {
                "violation_id": violation_id,
                "creator_id": creator_id,
                "rule_id": rule_id,
                "severity": severity.value,
                "description": description,
                "evidence": evidence or {},
                "status": "open",
                "reported_at": datetime.utcnow().isoformat(),
                "reporter": "system",
                "resolution": None
            }
            
            self.violations.append(violation)
            
            return {
                "success": True,
                "violation": violation,
                "message": "Violation signalée avec succès"
            }
            
        except Exception as e:
            self.logger.error(f"Violation reporting failed: {str(e)}")
            return {
                "success": False,
                "error": "Signalement de violation échoué",
                "message": str(e)
            }
    
    async def get_disclosure_template(
        self, 
        template_id: str, 
        language: str = "fr",
        brand_name: str = None
    ) -> Dict[str, Any]:
        """Get disclosure template for content"""
        try:
            if template_id not in self.disclosure_templates:
                return {
                    "success": False,
                    "error": "Template introuvable"
                }
            
            template_data = self.disclosure_templates[template_id]
            template_text = template_data["templates"].get(language, 
                                                         template_data["templates"].get("fr"))
            
            # Replace placeholders
            if brand_name and "{brand_name}" in template_text:
                template_text = template_text.replace("{brand_name}", brand_name)
            
            return {
                "success": True,
                "template_id": template_id,
                "template_text": template_text,
                "placement": template_data["placement"],
                "visibility": template_data["visibility"],
                "platforms": template_data["platforms"]
            }
            
        except Exception as e:
            self.logger.error(f"Getting disclosure template failed: {str(e)}")
            return {
                "success": False,
                "error": "Récupération du template échouée",
                "message": str(e)
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get service health status"""
        return {
            "service": "CreatorComplianceService",
            "status": "healthy",
            "compliance_rules": len(self.compliance_rules),
            "tracked_creators": len(self.creator_profiles),
            "total_violations": len(self.violations),
            "compliance_checks": len(self.compliance_checks),
            "disclosure_templates": len(self.disclosure_templates),
            "timestamp": datetime.utcnow().isoformat()
        }


__all__ = ['CreatorComplianceService', 'ComplianceStatus', 'ComplianceRuleType', 'ViolationSeverity']