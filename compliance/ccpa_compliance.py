"""
CCPA (California Consumer Privacy Act) Compliance Manager
Implements CCPA compliance for consumer rights and privacy protection

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved - Unauthorized use prohibited
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
from dataclasses import dataclass, field
import uuid


class CCPAConsumerRight(str, Enum):
    """CCPA Consumer Rights"""
    RIGHT_TO_KNOW = "right_to_know"
    RIGHT_TO_DELETE = "right_to_delete"
    RIGHT_TO_OPT_OUT = "right_to_opt_out"
    RIGHT_TO_NON_DISCRIMINATION = "right_to_non_discrimination"


class CCPAPersonalInfoCategory(str, Enum):
    """CCPA Personal Information Categories"""
    IDENTIFIERS = "identifiers"
    PERSONAL_INFO = "personal_info"
    PROTECTED_CHARACTERISTICS = "protected_characteristics"
    COMMERCIAL_INFO = "commercial_info"
    BIOMETRIC_INFO = "biometric_info"
    INTERNET_ACTIVITY = "internet_activity"
    GEOLOCATION = "geolocation"
    SENSORY_DATA = "sensory_data"
    PROFESSIONAL_INFO = "professional_info"
    EDUCATION_INFO = "education_info"
    INFERENCES = "inferences"


class CCPABusinessPurpose(str, Enum):
    """CCPA Business/Commercial Purposes"""
    AUDIT_SECURITY = "audit_security"
    FRAUD_PREVENTION = "fraud_prevention"
    DEBUGGING = "debugging"
    SHORT_TERM_USE = "short_term_use"
    SERVICE_PERFORMANCE = "service_performance"
    INTERNAL_RESEARCH = "internal_research"
    QUALITY_VERIFICATION = "quality_verification"


@dataclass
class CCPAPersonalInfo:
    """CCPA Personal Information Record"""
    category: CCPAPersonalInfoCategory
    data_elements: List[str]
    collection_purpose: str
    business_purpose: CCPABusinessPurpose
    sources: List[str] = field(default_factory=list)
    third_parties_shared: List[str] = field(default_factory=list)
    retention_period: int = 365  # days
    sold_to_third_parties: bool = False
    disclosed_for_business: bool = False


@dataclass
class CCPAConsumerRequest:
    """CCPA Consumer Request Record"""
    request_id: str
    consumer_id: int
    request_type: CCPAConsumerRight
    request_date: datetime
    verification_method: str
    verification_status: str = "pending"
    fulfillment_date: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    status: str = "received"
    notes: str = ""


@dataclass
class CCPADisclosure:
    """CCPA Disclosure Information"""
    disclosure_id: str
    collection_notice: str
    privacy_policy_url: str
    categories_collected: List[CCPAPersonalInfoCategory] = field(default_factory=list)
    purposes_collection: List[str] = field(default_factory=list)
    sources_personal_info: List[str] = field(default_factory=list)
    categories_disclosed: List[CCPAPersonalInfoCategory] = field(default_factory=list)
    categories_sold: List[CCPAPersonalInfoCategory] = field(default_factory=list)
    third_party_recipients: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)


class CCPAComplianceManager:
    """
    CCPA Compliance Manager
    
    Implements California Consumer Privacy Act compliance including:
    - Consumer rights management (know, delete, opt-out, non-discrimination)
    - Personal information inventory and categorization
    - Privacy policy and disclosure management
    - Consumer request processing and verification
    - Third-party data sharing tracking
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger("compliance.ccpa")
        
        # CCPA compliance settings
        self.verification_required = self.config.get("verification_required", True)
        self.response_deadline_days = self.config.get("response_deadline_days", 45)
        self.opt_out_immediate = self.config.get("opt_out_immediate", True)
        
        # Business information
        self.business_info = self.config.get("business_info", {
            "name": "Ainflue Platform",
            "address": "",
            "phone": "",
            "email": "privacy@ainflue.com"
        })
        
        # Personal information inventory
        self.personal_info_inventory = self._initialize_personal_info_inventory()
        
        self.logger.info("CCPA Compliance Manager initialized successfully")
    
    def _initialize_personal_info_inventory(self) -> List[CCPAPersonalInfo]:
        """Initialize CCPA personal information inventory"""
        return [
            CCPAPersonalInfo(
                category=CCPAPersonalInfoCategory.IDENTIFIERS,
                data_elements=[
                    "real name", "alias", "email address", "account name",
                    "IP address", "unique personal identifier"
                ],
                collection_purpose="Account creation and management",
                business_purpose=CCPABusinessPurpose.SERVICE_PERFORMANCE,
                sources=["directly from consumer", "automatically collected"],
                third_parties_shared=["service providers", "analytics providers"],
                retention_period=2555,  # 7 years
                disclosed_for_business=True
            ),
            CCPAPersonalInfo(
                category=CCPAPersonalInfoCategory.COMMERCIAL_INFO,
                data_elements=[
                    "purchase history", "subscription records", "payment information",
                    "billing details", "revenue data"
                ],
                collection_purpose="Payment processing and monetization",
                business_purpose=CCPABusinessPurpose.SERVICE_PERFORMANCE,
                sources=["directly from consumer", "payment processors"],
                third_parties_shared=["payment processors", "financial institutions"],
                retention_period=2555,  # 7 years (legal requirement)
                disclosed_for_business=True
            ),
            CCPAPersonalInfo(
                category=CCPAPersonalInfoCategory.INTERNET_ACTIVITY,
                data_elements=[
                    "browsing history", "search history", "interaction with website",
                    "content uploads", "usage patterns"
                ],
                collection_purpose="Service improvement and analytics",
                business_purpose=CCPABusinessPurpose.INTERNAL_RESEARCH,
                sources=["automatically collected"],
                third_parties_shared=["analytics providers"],
                retention_period=730,  # 2 years
                disclosed_for_business=True
            ),
            CCPAPersonalInfo(
                category=CCPAPersonalInfoCategory.SENSORY_DATA,
                data_elements=[
                    "audio recordings", "video content", "images",
                    "audio fingerprints", "content metadata"
                ],
                collection_purpose="Content protection and monetization",
                business_purpose=CCPABusinessPurpose.SERVICE_PERFORMANCE,
                sources=["directly from consumer"],
                third_parties_shared=["content platforms", "protection services"],
                retention_period=1825,  # 5 years
                disclosed_for_business=True
            ),
            CCPAPersonalInfo(
                category=CCPAPersonalInfoCategory.INFERENCES,
                data_elements=[
                    "content preferences", "usage patterns", "audience insights",
                    "monetization potential", "collaboration matches"
                ],
                collection_purpose="Personalization and recommendations",
                business_purpose=CCPABusinessPurpose.INTERNAL_RESEARCH,
                sources=["derived from other personal information"],
                third_parties_shared=["analytics providers"],
                retention_period=730,  # 2 years
                disclosed_for_business=True
            )
        ]
    
    async def check_compliance(self, user_id: int) -> Dict[str, Any]:
        """Check CCPA compliance status for a user"""
        try:
            self.logger.info(f"Checking CCPA compliance for user {user_id}")
            
            compliance_result = {
                "user_id": user_id,
                "regulation": "ccpa",
                "compliance_score": 100.0,
                "status": "compliant",
                "last_checked": datetime.utcnow(),
                "issues": [],
                "recommendations": []
            }
            
            # Check consumer rights implementation
            rights_score = await self._check_consumer_rights_implementation(user_id)
            compliance_result["consumer_rights_score"] = rights_score
            
            # Check disclosure compliance
            disclosure_score = await self._check_disclosure_compliance(user_id)
            compliance_result["disclosure_score"] = disclosure_score
            
            # Check data sharing compliance
            sharing_score = await self._check_data_sharing_compliance(user_id)
            compliance_result["data_sharing_score"] = sharing_score
            
            # Calculate overall score
            overall_score = (rights_score + disclosure_score + sharing_score) / 3
            compliance_result["compliance_score"] = overall_score
            
            # Determine status
            if overall_score >= 90.0:
                compliance_result["status"] = "compliant"
            elif overall_score >= 70.0:
                compliance_result["status"] = "partial_compliance"
            else:
                compliance_result["status"] = "non_compliant"
            
            # Add specific issues and recommendations
            if overall_score < 100.0:
                compliance_result["issues"] = [
                    "Some CCPA compliance requirements not fully met"
                ]
                compliance_result["recommendations"] = [
                    "Review and update privacy policy disclosures",
                    "Implement consumer request processing automation",
                    "Audit third-party data sharing agreements"
                ]
            
            self.logger.info(
                f"CCPA compliance check completed for user {user_id}: "
                f"{overall_score:.1f}%"
            )
            
            return compliance_result
            
        except Exception as e:
            self.logger.error(f"Error checking CCPA compliance: {e}")
            return {
                "user_id": user_id,
                "regulation": "ccpa",
                "compliance_score": 0.0,
                "status": "error",
                "error": str(e)
            }
    
    async def _check_consumer_rights_implementation(self, user_id: int) -> float:
        """Check implementation of CCPA consumer rights"""
        score = 100.0
        
        # Check if all consumer rights are implemented
        required_rights = [
            CCPAConsumerRight.RIGHT_TO_KNOW,
            CCPAConsumerRight.RIGHT_TO_DELETE,
            CCPAConsumerRight.RIGHT_TO_OPT_OUT,
            CCPAConsumerRight.RIGHT_TO_NON_DISCRIMINATION
        ]
        
        # This would typically check database for implemented features
        # For now, assume all rights are implemented
        implemented_rights = len(required_rights)  # Placeholder
        
        if implemented_rights < len(required_rights):
            score -= (len(required_rights) - implemented_rights) * 25.0
        
        return max(0.0, score)
    
    async def _check_disclosure_compliance(self, user_id: int) -> float:
        """Check CCPA disclosure compliance"""
        score = 100.0
        
        # Check if all required disclosures are present
        # This would typically check for privacy policy, collection notices, etc.
        # For now, assume basic compliance
        
        return score
    
    async def _check_data_sharing_compliance(self, user_id: int) -> float:
        """Check CCPA data sharing compliance"""
        score = 100.0
        
        # Check third-party data sharing compliance
        # This would typically audit actual data sharing activities
        # For now, assume compliance
        
        return score
    
    async def process_consumer_request(
        self,
        consumer_id: int,
        request_type: CCPAConsumerRight,
        verification_data: Dict[str, Any] = None
    ) -> str:
        """
        Process CCPA consumer request
        
        Args:
            consumer_id: Consumer making the request
            request_type: Type of consumer right request
            verification_data: Data for consumer verification
            
        Returns:
            Request ID for tracking
        """
        try:
            request_id = f"ccpa_{uuid.uuid4().hex[:12]}"
            
            self.logger.info(
                f"Processing CCPA consumer request: {request_id} "
                f"({request_type.value}) for consumer {consumer_id}"
            )
            
            # Create consumer request record
            consumer_request = CCPAConsumerRequest(
                request_id=request_id,
                consumer_id=consumer_id,
                request_type=request_type,
                request_date=datetime.utcnow(),
                verification_method="email_verification",  # Default method
                verification_status="pending" if self.verification_required else "verified"
            )
            
            # Store request (in actual implementation, this would go to database)
            await self._store_consumer_request(consumer_request)
            
            # Process based on request type
            if request_type == CCPAConsumerRight.RIGHT_TO_KNOW:
                await self._process_right_to_know(consumer_request)
            elif request_type == CCPAConsumerRight.RIGHT_TO_DELETE:
                await self._process_right_to_delete(consumer_request)
            elif request_type == CCPAConsumerRight.RIGHT_TO_OPT_OUT:
                await self._process_right_to_opt_out(consumer_request)
            elif request_type == CCPAConsumerRight.RIGHT_TO_NON_DISCRIMINATION:
                await self._process_right_to_non_discrimination(consumer_request)
            
            self.logger.info(f"CCPA consumer request processed: {request_id}")
            
            return request_id
            
        except Exception as e:
            self.logger.error(f"Error processing CCPA consumer request: {e}")
            raise
    
    async def _process_right_to_know(self, request: CCPAConsumerRequest) -> None:
        """Process Right to Know request"""
        try:
            # Collect personal information for consumer
            personal_info = await self._collect_consumer_personal_info(request.consumer_id)
            
            # Generate disclosure report
            disclosure_report = {
                "categories_collected": [info.category.value for info in self.personal_info_inventory],
                "purposes_collection": [info.collection_purpose for info in self.personal_info_inventory],
                "sources": ["directly from consumer", "automatically collected", "third parties"],
                "categories_disclosed": [info.category.value for info in self.personal_info_inventory if info.disclosed_for_business],
                "categories_sold": [info.category.value for info in self.personal_info_inventory if info.sold_to_third_parties],
                "specific_personal_info": personal_info,
                "third_party_recipients": ["service providers", "analytics providers", "payment processors"]
            }
            
            # Update request with response data
            request.response_data = disclosure_report
            request.fulfillment_date = datetime.utcnow()
            request.status = "fulfilled"
            
            # Send disclosure to consumer (in actual implementation)
            await self._send_disclosure_to_consumer(request)
            
        except Exception as e:
            self.logger.error(f"Error processing right to know request: {e}")
            raise
    
    async def _process_right_to_delete(self, request: CCPAConsumerRequest) -> None:
        """Process Right to Delete request"""
        try:
            # Check if deletion is permissible
            can_delete = await self._check_deletion_eligibility(request.consumer_id)
            
            if can_delete:
                # Perform data deletion
                await self._perform_consumer_data_deletion(request.consumer_id)
                
                request.response_data = {"deletion_performed": True, "deletion_date": datetime.utcnow()}
                request.status = "fulfilled"
            else:
                request.response_data = {
                    "deletion_performed": False,
                    "reason": "Data required for legal obligations or legitimate business purposes"
                }
                request.status = "denied"
            
            request.fulfillment_date = datetime.utcnow()
            
            # Notify consumer of deletion result
            await self._notify_consumer_deletion_result(request)
            
        except Exception as e:
            self.logger.error(f"Error processing right to delete request: {e}")
            raise
    
    async def _process_right_to_opt_out(self, request: CCPAConsumerRequest) -> None:
        """Process Right to Opt-Out request"""
        try:
            # Implement opt-out of sale of personal information
            await self._implement_opt_out(request.consumer_id)
            
            request.response_data = {
                "opt_out_status": "active",
                "opt_out_date": datetime.utcnow(),
                "effective_immediately": self.opt_out_immediate
            }
            request.fulfillment_date = datetime.utcnow()
            request.status = "fulfilled"
            
            # Notify consumer of opt-out confirmation
            await self._notify_consumer_opt_out_confirmation(request)
            
        except Exception as e:
            self.logger.error(f"Error processing right to opt-out request: {e}")
            raise
    
    async def _process_right_to_non_discrimination(self, request: CCPAConsumerRequest) -> None:
        """Process Right to Non-Discrimination request"""
        try:
            # Document non-discrimination policy compliance
            request.response_data = {
                "non_discrimination_policy": "Consumer rights requests do not affect service quality or pricing",
                "policy_url": "https://ainflue.com/privacy-policy#non-discrimination",
                "complaint_process": "Contact privacy@ainflue.com for discrimination concerns"
            }
            request.fulfillment_date = datetime.utcnow()
            request.status = "fulfilled"
            
            # Send non-discrimination policy information
            await self._send_non_discrimination_info(request)
            
        except Exception as e:
            self.logger.error(f"Error processing right to non-discrimination request: {e}")
            raise
    
    async def process_data_subject_request(
        self, user_id: int, request_type, details: Dict[str, Any]
    ) -> str:
        """Process data subject request (interface compatibility with global compliance)"""
        # Map global request types to CCPA consumer rights
        ccpa_right_mapping = {
            "access": CCPAConsumerRight.RIGHT_TO_KNOW,
            "erasure": CCPAConsumerRight.RIGHT_TO_DELETE,
            "opt_out": CCPAConsumerRight.RIGHT_TO_OPT_OUT
        }
        
        ccpa_right = ccpa_right_mapping.get(request_type.value if hasattr(request_type, 'value') else request_type)
        
        if ccpa_right:
            return await self.process_consumer_request(user_id, ccpa_right, details)
        else:
            raise ValueError(f"Unsupported request type for CCPA: {request_type}")
    
    async def generate_compliance_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate CCPA compliance report"""
        try:
            report = {
                "regulation": "ccpa",
                "reporting_period": f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
                "generated_at": datetime.utcnow(),
                "consumer_requests": {
                    "total_requests": 0,
                    "right_to_know": 0,
                    "right_to_delete": 0,
                    "right_to_opt_out": 0,
                    "requests_fulfilled": 0,
                    "average_response_time_days": 0.0
                },
                "compliance_metrics": {
                    "compliance_rate": 95.0,  # Placeholder
                    "disclosure_accuracy": 98.0,
                    "response_timeliness": 100.0,
                    "verification_success_rate": 95.0
                },
                "data_sharing": {
                    "categories_sold": [],
                    "third_party_recipients": len(set(
                        recipient for info in self.personal_info_inventory 
                        for recipient in info.third_parties_shared
                    )),
                    "opt_out_rate": 15.0  # Placeholder
                },
                "violations": 0,
                "enforcement_actions": 0
            }
            
            # In actual implementation, this would query database for real metrics
            # For now, return placeholder report
            
            self.logger.info("CCPA compliance report generated")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating CCPA compliance report: {e}")
            raise
    
    async def _store_consumer_request(self, request: CCPAConsumerRequest) -> None:
        """Store consumer request (placeholder for database operation)"""
        # In actual implementation, this would store to database
        self.logger.info(f"Stored CCPA consumer request: {request.request_id}")
    
    async def _collect_consumer_personal_info(self, consumer_id: int) -> Dict[str, Any]:
        """Collect personal information for consumer (placeholder)"""
        # In actual implementation, this would collect from database
        return {
            "identifiers": ["email@example.com", "username123"],
            "commercial_info": ["subscription_premium", "payment_methods"],
            "internet_activity": ["login_history", "content_uploads"],
            "sensory_data": ["audio_files", "video_content"],
            "inferences": ["content_preferences", "usage_patterns"]
        }
    
    async def _check_deletion_eligibility(self, consumer_id: int) -> bool:
        """Check if consumer data can be deleted"""
        # In actual implementation, this would check legal obligations
        return True  # Placeholder
    
    async def _perform_consumer_data_deletion(self, consumer_id: int) -> None:
        """Perform consumer data deletion (placeholder)"""
        # In actual implementation, this would delete from database
        self.logger.info(f"Performed data deletion for consumer {consumer_id}")
    
    async def _implement_opt_out(self, consumer_id: int) -> None:
        """Implement opt-out of sale (placeholder)"""
        # In actual implementation, this would update opt-out status
        self.logger.info(f"Implemented opt-out for consumer {consumer_id}")
    
    async def _send_disclosure_to_consumer(self, request: CCPAConsumerRequest) -> None:
        """Send disclosure information to consumer (placeholder)"""
        self.logger.info(f"Sent disclosure to consumer for request {request.request_id}")
    
    async def _notify_consumer_deletion_result(self, request: CCPAConsumerRequest) -> None:
        """Notify consumer of deletion result (placeholder)"""
        self.logger.info(f"Notified consumer of deletion result for request {request.request_id}")
    
    async def _notify_consumer_opt_out_confirmation(self, request: CCPAConsumerRequest) -> None:
        """Notify consumer of opt-out confirmation (placeholder)"""
        self.logger.info(f"Sent opt-out confirmation for request {request.request_id}")
    
    async def _send_non_discrimination_info(self, request: CCPAConsumerRequest) -> None:
        """Send non-discrimination policy information (placeholder)"""
        self.logger.info(f"Sent non-discrimination info for request {request.request_id}")


# Export for use in other modules
__all__ = [
    "CCPAComplianceManager",
    "CCPAConsumerRight",
    "CCPAPersonalInfoCategory",
    "CCPABusinessPurpose"
]