"""Automated Licensing Engine - Core licensing automation system

Handles automatic license generation, negotiation, and distribution
for multi-format content across global platforms.

Project: IA Influencer Agent & Content Protection Platform
Created by: Fahed Mlaiel <mlaiel@live.de>

WARNING - COPYRIGHT PROTECTION:
This code and concept are the exclusive intellectual property of Fahed Mlaiel.
Any unauthorized use, reproduction, or distribution without explicit written 
authorization from Fahed Mlaiel (mlaiel@live.de) is strictly prohibited.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ...core.database import get_db
from ...core.logging import get_logger
from ...models.licensing import (
    LicenseAgreement, 
    LicenseTemplate,
    LicenseTerms,
    RoyaltyDistribution
)
from ...utils.exceptions import LicensingError
from ..ai.contract_intelligence import ContractIntelligenceEngine
from ..blockchain.smart_contracts import SmartContractManager


class LicenseType(Enum):
    """License types for different content usage scenarios"""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    SYNCHRONIZATION = "synchronization"
    MECHANICAL = "mechanical"
    PERFORMANCE = "performance"
    MASTER_RECORDING = "master_recording"
    PUBLISHING = "publishing"
    DERIVATIVE_WORKS = "derivative_works"
    COMMERCIAL_USE = "commercial_use"
    STREAMING = "streaming"


class LicenseStatus(Enum):
    """License agreement status tracking"""    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    EXPIRED = "expired"
    BREACHED = "breached"


@dataclass
class LicenseConfiguration:
    """Configuration for automated license generation"""    license_type: LicenseType
    territory: List[str]
    duration_months: int
    revenue_percentage: Decimal
    minimum_guarantee: Optional[Decimal] = None
    advance_payment: Optional[Decimal] = None
    usage_limits: Dict[str, int] = field(default_factory=dict)
    restrictions: List[str] = field(default_factory=list)
    performance_requirements: Dict[str, Any] = field(default_factory=dict)


class LicenseRequest(BaseModel):
    """License request structure"""    content_id: str = Field(..., description="Content identifier")
    licensee_id: str = Field(..., description="Licensee user ID")
    license_type: LicenseType = Field(..., description="Type of license requested")
    territory: List[str] = Field(..., description="Geographic territories")
    intended_use: str = Field(..., description="Intended use description")
    duration_months: int = Field(12, description="License duration in months")
    budget_range: Optional[Dict[str, Decimal]] = Field(None, description="Budget constraints")
    additional_terms: Optional[Dict[str, Any]] = Field(None, description="Additional terms")


class AutomatedLicensingEngine:
    """    Advanced automated licensing system with AI-driven contract generation,
    intelligent pricing, and blockchain-secured agreements.
    """    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        self.logger = get_logger(__name__)
        self.contract_intelligence = ContractIntelligenceEngine()
        self.smart_contract_manager = SmartContractManager()
        
    async def process_license_request(
        self, 
        request: LicenseRequest,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """        Process incoming license request with automated evaluation and approval
        
        Args:
            request: License request details
            auto_approve: Whether to automatically approve qualifying requests
            
        Returns:
            License processing result with agreement details
        """        try:
            self.logger.info(f"Processing license request for content {request.content_id}")
            
            # Validate content ownership and availability
            content_validation = await self._validate_content_licensing_eligibility(
                request.content_id
            )
            
            if not content_validation["eligible"]:
                raise LicensingError(f"Content not eligible for licensing: {content_validation['reason']}")
            
            # Generate intelligent pricing based on AI analysis
            pricing_analysis = await self._generate_intelligent_pricing(request)
            
            # Create license configuration
            license_config = await self._create_license_configuration(
                request, pricing_analysis
            )
            
            # Generate contract terms using AI
            contract_terms = await self.contract_intelligence.generate_contract_terms(
                license_config, request
            )
            
            # Create license agreement
            license_agreement = await self._create_license_agreement(
                request, license_config, contract_terms
            )
            
            # Initialize blockchain smart contract if applicable
            if license_config.license_type in [LicenseType.EXCLUSIVE, LicenseType.MASTER_RECORDING]:
                smart_contract = await self.smart_contract_manager.deploy_license_contract(
                    license_agreement.id
                )
                license_agreement.blockchain_contract_address = smart_contract["address"]
            
            # Auto-approve if criteria met
            if auto_approve and await self._evaluate_auto_approval_criteria(request, pricing_analysis):
                await self._approve_license_agreement(license_agreement.id)
                status = LicenseStatus.ACTIVE
            else:
                status = LicenseStatus.PENDING_APPROVAL
            
            # Setup automated monitoring and compliance
            await self._setup_license_monitoring(license_agreement.id)
            
            return {
                "success": True,
                "license_id": license_agreement.id,
                "status": status.value,
                "terms": contract_terms,
                "pricing": pricing_analysis,
                "estimated_revenue": pricing_analysis["projected_revenue"],
                "next_steps": await self._generate_next_steps(license_agreement, status)
            }
            
        except Exception as e:
            self.logger.error(f"Error processing license request: {str(e)}")
            raise LicensingError(f"License processing failed: {str(e)}")
    
    async def _validate_content_licensing_eligibility(self, content_id: str) -> Dict[str, Any]:
        """Validate if content is eligible for licensing"""        try:
            # Check content ownership
            content_info = await self._get_content_info(content_id)
            
            if not content_info:
                return {"eligible": False, "reason": "Content not found"}
            
            # Verify ownership rights
            ownership_clear = await self._verify_ownership_rights(content_id)
            if not ownership_clear["clear"]:
                return {"eligible": False, "reason": f"Ownership issues: {ownership_clear['issues']}"}
            
            # Check existing licenses and conflicts
            existing_licenses = await self._get_existing_licenses(content_id)
            conflicts = await self._analyze_license_conflicts(existing_licenses)
            
            if conflicts:
                return {"eligible": False, "reason": f"License conflicts: {conflicts}"}
            
            # Verify content quality and completeness
            quality_check = await self._perform_content_quality_check(content_id)
            if not quality_check["passes"]:
                return {"eligible": False, "reason": f"Quality issues: {quality_check['issues']}"}
            
            return {
                "eligible": True,
                "content_info": content_info,
                "ownership_status": ownership_clear,
                "existing_licenses_count": len(existing_licenses),
                "quality_score": quality_check["score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error validating content eligibility: {str(e)}")
            return {"eligible": False, "reason": f"Validation error: {str(e)}"}
    
    async def _generate_intelligent_pricing(self, request: LicenseRequest) -> Dict[str, Any]:
        """Generate AI-driven pricing analysis"""        try:
            # Analyze market data for similar content
            market_analysis = await self._analyze_market_pricing(
                request.license_type, request.territory
            )
            
            # Content value assessment
            content_value = await self._assess_content_value(request.content_id)
            
            # Territory-specific pricing adjustments
            territory_adjustments = await self._calculate_territory_adjustments(
                request.territory
            )
            
            # Usage type multipliers
            usage_multiplier = await self._get_usage_type_multiplier(
                request.license_type, request.intended_use
            )
            
            # Calculate base pricing
            base_price = (
                market_analysis["median_price"] * 
                content_value["value_multiplier"] *
                territory_adjustments["multiplier"] *
                usage_multiplier
            )
            
            # Revenue sharing calculation
            revenue_percentage = self._calculate_optimal_revenue_share(
                request.license_type, market_analysis
            )
            
            # Minimum guarantee calculation
            minimum_guarantee = base_price * Decimal("0.3")  # 30% of estimated value
            
            # Projected revenue calculation
            projected_revenue = await self._calculate_projected_revenue(
                request, base_price, revenue_percentage
            )
            
            return {
                "base_license_fee": base_price,
                "revenue_percentage": revenue_percentage,
                "minimum_guarantee": minimum_guarantee,
                "projected_revenue": projected_revenue,
                "market_analysis": market_analysis,
                "content_value_score": content_value["score"],
                "territory_factor": territory_adjustments["multiplier"],
                "usage_multiplier": usage_multiplier,
                "recommended_terms": {
                    "advance_payment": base_price * Decimal("0.5"),
                    "milestone_payments": self._generate_milestone_payments(projected_revenue),
                    "performance_bonuses": self._generate_performance_bonuses(projected_revenue)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error generating pricing analysis: {str(e)}")
            raise LicensingError(f"Pricing analysis failed: {str(e)}")
    
    async def _create_license_configuration(
        self, 
        request: LicenseRequest,
        pricing_analysis: Dict[str, Any]
    ) -> LicenseConfiguration:
        """Create comprehensive license configuration"""        
        # Generate usage limits based on license type
        usage_limits = self._generate_usage_limits(request.license_type, request.intended_use)
        
        # Create restrictions based on territory and content type
        restrictions = await self._generate_licensing_restrictions(
            request.territory, request.license_type
        )
        
        # Performance requirements
        performance_requirements = {
            "reporting_frequency": "monthly",
            "minimum_promotion_spend": pricing_analysis["base_license_fee"] * Decimal("0.1"),
            "quality_standards": {
                "audio_bitrate_min": 320,  # kbps for audio
                "video_resolution_min": "1080p",
                "image_resolution_min": "1920x1080"
            },
            "attribution_requirements": {
                "credit_placement": "prominent",
                "copyright_notice": "required",
                "trademark_usage": "approved_only"
            }
        }
        
        return LicenseConfiguration(
            license_type=request.license_type,
            territory=request.territory,
            duration_months=request.duration_months,
            revenue_percentage=pricing_analysis["revenue_percentage"],
            minimum_guarantee=pricing_analysis["minimum_guarantee"],
            advance_payment=pricing_analysis["recommended_terms"]["advance_payment"],
            usage_limits=usage_limits,
            restrictions=restrictions,
            performance_requirements=performance_requirements
        )
    
    async def _create_license_agreement(
        self,
        request: LicenseRequest,
        config: LicenseConfiguration,
        contract_terms: Dict[str, Any]
    ) -> LicenseAgreement:
        """Create comprehensive license agreement"""        
        agreement_id = str(uuid.uuid4())
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=config.duration_months * 30)
        
        # Create license agreement record
        license_agreement = LicenseAgreement(
            id=agreement_id,
            content_id=request.content_id,
            licensee_id=request.licensee_id,
            license_type=config.license_type.value,
            status=LicenseStatus.DRAFT.value,
            territory=config.territory,
            start_date=start_date,
            end_date=end_date,
            revenue_percentage=config.revenue_percentage,
            minimum_guarantee=config.minimum_guarantee,
            advance_payment=config.advance_payment,
            usage_limits=config.usage_limits,
            restrictions=config.restrictions,
            contract_terms=contract_terms,
            performance_requirements=config.performance_requirements,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(license_agreement)
        self.db.commit()
        self.db.refresh(license_agreement)
        
        self.logger.info(f"Created license agreement {agreement_id}")
        return license_agreement
    
    async def _setup_license_monitoring(self, license_id: str) -> None:
        """Setup automated monitoring for license compliance"""        try:
            # Create monitoring tasks
            monitoring_config = {
                "license_id": license_id,
                "monitoring_frequency": "daily",
                "compliance_checks": [
                    "usage_limits_verification",
                    "territory_compliance",
                    "payment_status_check",
                    "performance_requirements_audit",
                    "content_usage_tracking"
                ],
                "alert_thresholds": {
                    "usage_limit_warning": 0.8,  # 80% of limit
                    "payment_delay_days": 30,
                    "performance_below_target": 0.7  # 70% of expected
                },
                "automated_actions": {
                    "suspend_on_breach": True,
                    "escalate_to_legal": True,
                    "generate_performance_reports": True
                }
            }
            
            # Schedule monitoring tasks
            from ...tasks.licensing import setup_license_monitoring_task
            await setup_license_monitoring_task.delay(license_id, monitoring_config)
            
            self.logger.info(f"Setup monitoring for license {license_id}")
            
        except Exception as e:
            self.logger.error(f"Error setting up license monitoring: {str(e)}")
            raise
    
    async def generate_license_report(
        self, 
        license_id: str,
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate comprehensive license performance report"""        try:
            license_agreement = self.db.query(LicenseAgreement).filter(
                LicenseAgreement.id == license_id
            ).first()
            
            if not license_agreement:
                raise LicensingError(f"License agreement {license_id} not found")
            
            # Collect performance data
            usage_data = await self._collect_usage_analytics(license_id)
            revenue_data = await self._collect_revenue_data(license_id)
            compliance_status = await self._check_compliance_status(license_id)
            
            report = {
                "license_id": license_id,
                "report_date": datetime.utcnow().isoformat(),
                "report_type": report_type,
                "license_details": {
                    "type": license_agreement.license_type,
                    "status": license_agreement.status,
                    "territory": license_agreement.territory,
                    "duration": f"{license_agreement.duration_months} months",
                    "start_date": license_agreement.start_date.isoformat(),
                    "end_date": license_agreement.end_date.isoformat()
                },
                "financial_summary": {
                    "total_revenue_generated": revenue_data["total_revenue"],
                    "advance_payment_received": license_agreement.advance_payment,
                    "minimum_guarantee_met": revenue_data["minimum_guarantee_met"],
                    "outstanding_payments": revenue_data["outstanding_amount"],
                    "next_payment_due": revenue_data["next_payment_date"]
                },
                "usage_analytics": usage_data,
                "compliance_status": compliance_status,
                "performance_metrics": await self._calculate_performance_metrics(license_id),
                "recommendations": await self._generate_optimization_recommendations(license_id)
            }
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating license report: {str(e)}")
            raise LicensingError(f"Report generation failed: {str(e)}")
    
    # Helper methods for internal operations
    async def _get_content_info(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve content information"""        # Implementation for content info retrieval
        pass
    
    async def _verify_ownership_rights(self, content_id: str) -> Dict[str, Any]:
        """Verify content ownership rights"""        # Implementation for ownership verification
        pass
    
    async def _analyze_market_pricing(self, license_type: LicenseType, territory: List[str]) -> Dict[str, Any]:
        """Analyze market pricing data"""        # Implementation for market analysis
        pass
    
    async def _calculate_projected_revenue(
        self, 
        request: LicenseRequest, 
        base_price: Decimal, 
        revenue_percentage: Decimal
    ) -> Dict[str, Decimal]:
        """Calculate projected revenue streams"""        # Implementation for revenue projection
        pass
    
    def _generate_usage_limits(self, license_type: LicenseType, intended_use: str) -> Dict[str, int]:
        """Generate appropriate usage limits"""        base_limits = {
            "daily_streams": 10000,
            "monthly_downloads": 1000,
            "broadcast_hours": 24,
            "sync_placements": 5
        }
        
        # Adjust based on license type
        if license_type == LicenseType.EXCLUSIVE:
            return {k: v * 10 for k, v in base_limits.items()}  # 10x limits for exclusive
        elif license_type == LicenseType.STREAMING:
            base_limits["daily_streams"] *= 5
            
        return base_limits
    
    def _calculate_optimal_revenue_share(
        self, 
        license_type: LicenseType, 
        market_analysis: Dict[str, Any]
    ) -> Decimal:
        """Calculate optimal revenue sharing percentage"""        base_percentages = {
            LicenseType.EXCLUSIVE: Decimal("0.15"),  # 15%
            LicenseType.NON_EXCLUSIVE: Decimal("0.25"),  # 25%
            LicenseType.SYNCHRONIZATION: Decimal("0.20"),  # 20%
            LicenseType.STREAMING: Decimal("0.30"),  # 30%
            LicenseType.COMMERCIAL_USE: Decimal("0.18")  # 18%
        }
        
        base_percentage = base_percentages.get(license_type, Decimal("0.25"))
        
        # Adjust based on market conditions
        if market_analysis.get("demand_high"):
            base_percentage *= Decimal("0.85")  # Lower percentage when demand is high
        
        return base_percentage
