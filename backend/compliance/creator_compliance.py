"""
Creator Compliance - Content Creator Compliance Management

Comprehensive creator compliance system for influencers, content creators,
and digital talent compliance requirements, contracts, and performance monitoring.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: All rights reserved - Proprietary software
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import aioredis
from sqlalchemy import Column, String, DateTime, JSON, Boolean, Float, Integer, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class CreatorType(Enum):
    """Types of content creators"""
    INFLUENCER = "influencer"
    MUSICIAN = "musician"
    ARTIST = "artist"
    BLOGGER = "blogger"
    PHOTOGRAPHER = "photographer"
    VIDEOGRAPHER = "videographer"
    PODCASTER = "podcaster"
    STREAMER = "streamer"
    GAMER = "gamer"
    EDUCATOR = "educator"
    CHEF = "chef"
    FITNESS_TRAINER = "fitness_trainer"
    BEAUTY_CREATOR = "beauty_creator"
    TECH_REVIEWER = "tech_reviewer"
    LIFESTYLE_CREATOR = "lifestyle_creator"


class CreatorTier(Enum):
    """Creator tier levels"""
    NANO = "nano"          # 1K-10K followers
    MICRO = "micro"        # 10K-100K followers
    MACRO = "macro"        # 100K-1M followers
    MEGA = "mega"          # 1M+ followers
    CELEBRITY = "celebrity" # Public figures


class ContractType(Enum):
    """Types of creator contracts"""
    BRAND_PARTNERSHIP = "brand_partnership"
    SPONSORSHIP = "sponsorship"
    AMBASSADOR = "ambassador"
    AFFILIATE = "affiliate"
    LICENSING = "licensing"
    EXCLUSIVE_DEAL = "exclusive_deal"
    REVENUE_SHARE = "revenue_share"
    COLLABORATION = "collaboration"
    ENDORSEMENT = "endorsement"
    CONTENT_LICENSING = "content_licensing"


class ComplianceArea(Enum):
    """Creator compliance areas"""
    FTC_DISCLOSURE = "ftc_disclosure"
    SPONSORED_CONTENT = "sponsored_content"
    AFFILIATE_MARKETING = "affiliate_marketing"
    COPYRIGHT_USAGE = "copyright_usage"
    TRADEMARK_COMPLIANCE = "trademark_compliance"
    PRIVACY_RIGHTS = "privacy_rights"
    TAX_OBLIGATIONS = "tax_obligations"
    PLATFORM_POLICIES = "platform_policies"
    BRAND_GUIDELINES = "brand_guidelines"
    CONTENT_STANDARDS = "content_standards"
    AUDIENCE_PROTECTION = "audience_protection"
    DATA_PROTECTION = "data_protection"


class ViolationType(Enum):
    """Types of compliance violations"""
    MISSING_DISCLOSURE = "missing_disclosure"
    INADEQUATE_DISCLOSURE = "inadequate_disclosure"
    COPYRIGHT_INFRINGEMENT = "copyright_infringement"
    TRADEMARK_VIOLATION = "trademark_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    MISLEADING_CLAIMS = "misleading_claims"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    PLATFORM_POLICY_BREACH = "platform_policy_breach"
    CONTRACT_VIOLATION = "contract_violation"
    TAX_NON_COMPLIANCE = "tax_non_compliance"
    BRAND_GUIDELINE_VIOLATION = "brand_guideline_violation"


class ComplianceStatus(Enum):
    """Compliance status levels"""
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    UNDER_REVIEW = "under_review"
    PENDING_APPROVAL = "pending_approval"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class DisclosureType(Enum):
    """Types of required disclosures"""
    SPONSORED = "sponsored"
    PAID_PARTNERSHIP = "paid_partnership"
    GIFTED = "gifted"
    AFFILIATE_LINK = "affiliate_link"
    BRAND_AMBASSADOR = "brand_ambassador"
    FREE_PRODUCT = "free_product"
    FAMILY_FRIEND_DISCOUNT = "family_friend_discount"
    EQUITY_PARTNERSHIP = "equity_partnership"


@dataclass
class CreatorProfile:
    """Content creator profile and compliance information"""
    creator_id: str
    creator_name: str
    creator_type: CreatorType
    creator_tier: CreatorTier
    platforms: List[str]
    follower_counts: Dict[str, int]
    engagement_rates: Dict[str, float]
    primary_categories: List[str]
    target_demographics: Dict[str, Any]
    compliance_status: ComplianceStatus
    compliance_score: float
    active_contracts: List[str]
    violation_history: List[str]
    certification_status: Dict[str, bool]
    last_compliance_review: datetime
    next_review_date: datetime
    profile_created: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreatorContract:
    """Creator contract details"""
    contract_id: str
    creator_id: str
    brand_id: str
    contract_type: ContractType
    contract_title: str
    start_date: datetime
    end_date: datetime
    compensation_amount: float
    compensation_type: str
    deliverables: List[Dict[str, Any]]
    compliance_requirements: List[str]
    disclosure_requirements: List[DisclosureType]
    content_guidelines: Dict[str, Any]
    exclusivity_clauses: List[str]
    performance_metrics: Dict[str, Any]
    approval_process: Dict[str, Any]
    contract_status: str
    signed_date: Optional[datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComplianceViolation:
    """Creator compliance violation record"""
    violation_id: str
    creator_id: str
    content_id: str
    violation_type: ViolationType
    compliance_area: ComplianceArea
    severity: str
    description: str
    detection_method: str
    detection_date: datetime
    platform: str
    brand_involved: Optional[str]
    contract_id: Optional[str]
    evidence: List[str]
    action_taken: str
    remediation_required: List[str]
    deadline: Optional[datetime]
    resolution_status: str
    resolution_date: Optional[datetime]
    repeat_offense: bool
    impact_assessment: Dict[str, Any]


@dataclass
class DisclosureAssessment:
    """Assessment of disclosure compliance"""
    assessment_id: str
    creator_id: str
    content_id: str
    platform: str
    required_disclosures: List[DisclosureType]
    actual_disclosures: List[str]
    disclosure_compliance: bool
    disclosure_quality_score: float
    missing_disclosures: List[DisclosureType]
    inadequate_disclosures: List[str]
    recommendations: List[str]
    assessment_date: datetime
    reviewer: str


@dataclass
class CreatorCertification:
    """Creator compliance certification"""
    certification_id: str
    creator_id: str
    certification_type: str
    certification_body: str
    issue_date: datetime
    expiry_date: datetime
    requirements_met: List[str]
    test_scores: Dict[str, float]
    certification_status: str
    renewal_required: bool
    continuing_education_hours: int
    specializations: List[str]


class CreatorProfileRecord(Base):
    """Database model for creator profiles"""
    __tablename__ = "creator_profiles"
    
    creator_id = Column(String, primary_key=True)
    creator_name = Column(String, nullable=False)
    creator_type = Column(String, nullable=False)
    creator_tier = Column(String, nullable=False)
    platforms = Column(JSON, default=[])
    follower_counts = Column(JSON, default={})
    engagement_rates = Column(JSON, default={})
    primary_categories = Column(JSON, default=[])
    target_demographics = Column(JSON, default={})
    compliance_status = Column(String, nullable=False)
    compliance_score = Column(Float, default=0.0)
    active_contracts = Column(JSON, default=[])
    violation_history = Column(JSON, default=[])
    certification_status = Column(JSON, default={})
    last_compliance_review = Column(DateTime)
    next_review_date = Column(DateTime)
    profile_created = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreatorContractRecord(Base):
    """Database model for creator contracts"""
    __tablename__ = "creator_contracts"
    
    contract_id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False)
    brand_id = Column(String, nullable=False)
    contract_type = Column(String, nullable=False)
    contract_title = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    compensation_amount = Column(Float, default=0.0)
    compensation_type = Column(String)
    deliverables = Column(JSON, default=[])
    compliance_requirements = Column(JSON, default=[])
    disclosure_requirements = Column(JSON, default=[])
    content_guidelines = Column(JSON, default={})
    exclusivity_clauses = Column(JSON, default=[])
    performance_metrics = Column(JSON, default={})
    approval_process = Column(JSON, default={})
    contract_status = Column(String, nullable=False)
    signed_date = Column(DateTime)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ComplianceViolationRecord(Base):
    """Database model for compliance violations"""
    __tablename__ = "creator_compliance_violations"
    
    violation_id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False)
    content_id = Column(String, nullable=False)
    violation_type = Column(String, nullable=False)
    compliance_area = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    detection_method = Column(String, nullable=False)
    detection_date = Column(DateTime, nullable=False)
    platform = Column(String, nullable=False)
    brand_involved = Column(String)
    contract_id = Column(String)
    evidence = Column(JSON, default=[])
    action_taken = Column(String)
    remediation_required = Column(JSON, default=[])
    deadline = Column(DateTime)
    resolution_status = Column(String)
    resolution_date = Column(DateTime)
    repeat_offense = Column(Boolean, default=False)
    impact_assessment = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DisclosureAssessmentRecord(Base):
    """Database model for disclosure assessments"""
    __tablename__ = "disclosure_assessments"
    
    assessment_id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False)
    content_id = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    required_disclosures = Column(JSON, default=[])
    actual_disclosures = Column(JSON, default=[])
    disclosure_compliance = Column(Boolean, default=False)
    disclosure_quality_score = Column(Float, default=0.0)
    missing_disclosures = Column(JSON, default=[])
    inadequate_disclosures = Column(JSON, default=[])
    recommendations = Column(JSON, default=[])
    assessment_date = Column(DateTime, default=datetime.utcnow)
    reviewer = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class CreatorCertificationRecord(Base):
    """Database model for creator certifications"""
    __tablename__ = "creator_certifications"
    
    certification_id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False)
    certification_type = Column(String, nullable=False)
    certification_body = Column(String, nullable=False)
    issue_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    requirements_met = Column(JSON, default=[])
    test_scores = Column(JSON, default={})
    certification_status = Column(String, nullable=False)
    renewal_required = Column(Boolean, default=False)
    continuing_education_hours = Column(Integer, default=0)
    specializations = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CreatorProfileManager:
    """Manages creator profiles and compliance tracking"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def create_creator_profile(self, creator_data: Dict[str, Any]) -> CreatorProfile:
        """Create new creator profile with compliance assessment"""
        try:
            creator_id = str(uuid.uuid4())
            
            # Perform initial compliance assessment
            initial_compliance = await self._assess_initial_compliance(creator_data)
            
            # Determine creator tier based on followers
            creator_tier = await self._determine_creator_tier(creator_data.get("follower_counts", {}))
            
            # Calculate next review date
            next_review = datetime.utcnow() + timedelta(days=90)  # Quarterly reviews
            
            profile = CreatorProfile(
                creator_id=creator_id,
                creator_name=creator_data["creator_name"],
                creator_type=CreatorType(creator_data["creator_type"]),
                creator_tier=creator_tier,
                platforms=creator_data.get("platforms", []),
                follower_counts=creator_data.get("follower_counts", {}),
                engagement_rates=creator_data.get("engagement_rates", {}),
                primary_categories=creator_data.get("primary_categories", []),
                target_demographics=creator_data.get("target_demographics", {}),
                compliance_status=initial_compliance["status"],
                compliance_score=initial_compliance["score"],
                active_contracts=[],
                violation_history=[],
                certification_status={},
                last_compliance_review=datetime.utcnow(),
                next_review_date=next_review,
                profile_created=datetime.utcnow(),
                metadata=creator_data.get("metadata", {})
            )
            
            # Store profile
            await self._store_creator_profile(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create creator profile: {str(e)}")
            raise
    
    async def _assess_initial_compliance(self, creator_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess initial compliance status for new creator"""
        compliance_score = 100.0  # Start with perfect score
        status = ComplianceStatus.COMPLIANT
        
        # Check basic profile completeness
        required_fields = ["creator_name", "creator_type", "platforms", "primary_categories"]
        missing_fields = [field for field in required_fields if not creator_data.get(field)]
        
        if missing_fields:
            compliance_score -= len(missing_fields) * 10
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        
        # Check platform verification status
        platforms = creator_data.get("platforms", [])
        verified_platforms = creator_data.get("verified_platforms", [])
        
        verification_rate = len(verified_platforms) / len(platforms) if platforms else 0
        if verification_rate < 0.5:
            compliance_score -= 20
            status = ComplianceStatus.PARTIALLY_COMPLIANT
        
        # Check for previous violations (if transferring from another system)
        previous_violations = creator_data.get("violation_history", [])
        if previous_violations:
            violation_penalty = min(len(previous_violations) * 5, 30)
            compliance_score -= violation_penalty
            if len(previous_violations) > 5:
                status = ComplianceStatus.NON_COMPLIANT
        
        # Ensure minimum score
        compliance_score = max(compliance_score, 0.0)
        
        return {
            "status": status,
            "score": compliance_score,
            "missing_fields": missing_fields,
            "verification_rate": verification_rate
        }
    
    async def _determine_creator_tier(self, follower_counts: Dict[str, int]) -> CreatorTier:
        """Determine creator tier based on follower counts"""
        if not follower_counts:
            return CreatorTier.NANO
        
        # Use the highest follower count across platforms
        max_followers = max(follower_counts.values())
        
        if max_followers >= 1_000_000:
            return CreatorTier.MEGA
        elif max_followers >= 100_000:
            return CreatorTier.MACRO
        elif max_followers >= 10_000:
            return CreatorTier.MICRO
        else:
            return CreatorTier.NANO
    
    async def _store_creator_profile(self, profile: CreatorProfile) -> None:
        """Store creator profile in database"""
        try:
            record = CreatorProfileRecord(
                creator_id=profile.creator_id,
                creator_name=profile.creator_name,
                creator_type=profile.creator_type.value,
                creator_tier=profile.creator_tier.value,
                platforms=profile.platforms,
                follower_counts=profile.follower_counts,
                engagement_rates=profile.engagement_rates,
                primary_categories=profile.primary_categories,
                target_demographics=profile.target_demographics,
                compliance_status=profile.compliance_status.value,
                compliance_score=profile.compliance_score,
                active_contracts=profile.active_contracts,
                violation_history=profile.violation_history,
                certification_status=profile.certification_status,
                last_compliance_review=profile.last_compliance_review,
                next_review_date=profile.next_review_date,
                profile_created=profile.profile_created,
                metadata=profile.metadata
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store creator profile: {str(e)}")
            raise


class DisclosureComplianceManager:
    """Manages FTC disclosure and sponsored content compliance"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def assess_disclosure_compliance(self, 
                                         creator_id: str,
                                         content_id: str,
                                         platform: str,
                                         content_data: Dict[str, Any],
                                         contract_requirements: Optional[List[DisclosureType]] = None) -> DisclosureAssessment:
        """Assess disclosure compliance for specific content"""
        try:
            assessment_id = str(uuid.uuid4())
            
            # Determine required disclosures
            required_disclosures = await self._determine_required_disclosures(
                content_data, contract_requirements
            )
            
            # Extract actual disclosures from content
            actual_disclosures = await self._extract_disclosures(content_data, platform)
            
            # Check compliance
            compliance_check = await self._check_disclosure_compliance(
                required_disclosures, actual_disclosures, platform
            )
            
            # Calculate quality score
            quality_score = await self._calculate_disclosure_quality_score(
                actual_disclosures, platform
            )
            
            # Generate recommendations
            recommendations = await self._generate_disclosure_recommendations(
                required_disclosures, actual_disclosures, platform, compliance_check
            )
            
            assessment = DisclosureAssessment(
                assessment_id=assessment_id,
                creator_id=creator_id,
                content_id=content_id,
                platform=platform,
                required_disclosures=required_disclosures,
                actual_disclosures=actual_disclosures,
                disclosure_compliance=compliance_check["compliant"],
                disclosure_quality_score=quality_score,
                missing_disclosures=compliance_check["missing"],
                inadequate_disclosures=compliance_check["inadequate"],
                recommendations=recommendations,
                assessment_date=datetime.utcnow(),
                reviewer="automated_system"
            )
            
            # Store assessment
            await self._store_disclosure_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Disclosure compliance assessment failed: {str(e)}")
            raise
    
    async def _determine_required_disclosures(self, 
                                            content_data: Dict[str, Any],
                                            contract_requirements: Optional[List[DisclosureType]]) -> List[DisclosureType]:
        """Determine what disclosures are required"""
        required = []
        
        # Contract-based requirements
        if contract_requirements:
            required.extend(contract_requirements)
        
        # Content-based requirements
        content_type = content_data.get("content_type", "").lower()
        
        # Check for sponsored content indicators
        if content_data.get("is_sponsored", False):
            required.append(DisclosureType.SPONSORED)
        
        if content_data.get("brand_partnership", False):
            required.append(DisclosureType.PAID_PARTNERSHIP)
        
        if content_data.get("affiliate_links", []):
            required.append(DisclosureType.AFFILIATE_LINK)
        
        if content_data.get("gifted_products", []):
            required.append(DisclosureType.GIFTED)
        
        if content_data.get("brand_ambassador", False):
            required.append(DisclosureType.BRAND_AMBASSADOR)
        
        # Remove duplicates
        return list(set(required))
    
    async def _extract_disclosures(self, content_data: Dict[str, Any], platform: str) -> List[str]:
        """Extract disclosure statements from content"""
        disclosures = []
        
        # Common disclosure patterns
        disclosure_patterns = [
            r'#sponsored', r'#ad', r'#advertisement', r'#paidpartnership',
            r'#affiliate', r'#gifted', r'#brandambassador', r'#collab',
            r'sponsored by', r'paid partnership', r'affiliate link',
            r'gifted by', r'brand ambassador', r'collaboration with'
        ]
        
        # Check text content
        text_fields = ["caption", "description", "title", "content"]
        for field in text_fields:
            if field in content_data:
                text = content_data[field].lower()
                for pattern in disclosure_patterns:
                    if pattern.replace('r\'', '').replace('\'', '') in text:
                        disclosures.append(pattern)
        
        # Check hashtags
        hashtags = content_data.get("hashtags", [])
        for hashtag in hashtags:
            hashtag_lower = hashtag.lower()
            for pattern in disclosure_patterns:
                if pattern.replace('#', '').replace('r\'', '').replace('\'', '') in hashtag_lower:
                    disclosures.append(hashtag)
        
        # Platform-specific disclosure locations
        if platform.lower() == "instagram":
            # Check story stickers, branded content tags
            if content_data.get("branded_content_tag"):
                disclosures.append("branded_content_tag")
            if content_data.get("paid_partnership_label"):
                disclosures.append("paid_partnership_label")
        
        elif platform.lower() == "youtube":
            # Check video description, cards, end screens
            if content_data.get("includes_paid_promotion"):
                disclosures.append("youtube_paid_promotion")
        
        elif platform.lower() == "tiktok":
            # Check branded content toggle
            if content_data.get("branded_content_toggle"):
                disclosures.append("branded_content_toggle")
        
        return list(set(disclosures))
    
    async def _check_disclosure_compliance(self, 
                                         required: List[DisclosureType],
                                         actual: List[str],
                                         platform: str) -> Dict[str, Any]:
        """Check if disclosures meet requirements"""
        compliant = True
        missing = []
        inadequate = []
        
        # Map actual disclosures to disclosure types
        actual_types = await self._map_disclosures_to_types(actual)
        
        # Check each required disclosure
        for req_type in required:
            if req_type not in actual_types:
                missing.append(req_type)
                compliant = False
            else:
                # Check quality of disclosure
                disclosure_quality = await self._assess_disclosure_quality(
                    req_type, actual, platform
                )
                if not disclosure_quality["adequate"]:
                    inadequate.append(disclosure_quality["issue"])
                    compliant = False
        
        return {
            "compliant": compliant,
            "missing": missing,
            "inadequate": inadequate
        }
    
    async def _map_disclosures_to_types(self, actual_disclosures: List[str]) -> List[DisclosureType]:
        """Map actual disclosure text to disclosure types"""
        mapped_types = []
        
        disclosure_mapping = {
            "sponsored": DisclosureType.SPONSORED,
            "ad": DisclosureType.SPONSORED,
            "advertisement": DisclosureType.SPONSORED,
            "paidpartnership": DisclosureType.PAID_PARTNERSHIP,
            "affiliate": DisclosureType.AFFILIATE_LINK,
            "gifted": DisclosureType.GIFTED,
            "brandambassador": DisclosureType.BRAND_AMBASSADOR,
            "branded_content_tag": DisclosureType.PAID_PARTNERSHIP,
            "paid_partnership_label": DisclosureType.PAID_PARTNERSHIP,
            "youtube_paid_promotion": DisclosureType.SPONSORED,
            "branded_content_toggle": DisclosureType.SPONSORED
        }
        
        for disclosure in actual_disclosures:
            disclosure_clean = disclosure.lower().replace('#', '').replace('r\'', '').replace('\'', '')
            if disclosure_clean in disclosure_mapping:
                mapped_types.append(disclosure_mapping[disclosure_clean])
        
        return list(set(mapped_types))
    
    async def _assess_disclosure_quality(self, 
                                       disclosure_type: DisclosureType,
                                       actual_disclosures: List[str],
                                       platform: str) -> Dict[str, Any]:
        """Assess quality of specific disclosure"""
        # Platform-specific quality requirements
        quality_requirements = {
            "instagram": {
                "prominence": "top_3_hashtags_or_caption_start",
                "clarity": "clear_language",
                "visibility": "not_buried_in_hashtags"
            },
            "youtube": {
                "prominence": "description_top_or_verbal",
                "clarity": "clear_statement",
                "visibility": "easily_visible"
            },
            "tiktok": {
                "prominence": "caption_start_or_overlay",
                "clarity": "clear_hashtag_or_text",
                "visibility": "visible_during_video"
            }
        }
        
        platform_reqs = quality_requirements.get(platform.lower(), {})
        
        # Check prominence (simplified implementation)
        prominent = any(
            disclosure.startswith('#ad') or disclosure.startswith('#sponsored')
            for disclosure in actual_disclosures[:3]  # Top 3 items
        )
        
        # Check clarity
        clear = any(
            len(disclosure) > 3 and not disclosure.isdigit()
            for disclosure in actual_disclosures
        )
        
        # Overall adequacy
        adequate = prominent and clear
        
        issues = []
        if not prominent:
            issues.append("disclosure_not_prominent")
        if not clear:
            issues.append("disclosure_unclear")
        
        return {
            "adequate": adequate,
            "prominent": prominent,
            "clear": clear,
            "issue": issues[0] if issues else None
        }
    
    async def _calculate_disclosure_quality_score(self, 
                                                actual_disclosures: List[str],
                                                platform: str) -> float:
        """Calculate overall disclosure quality score"""
        if not actual_disclosures:
            return 0.0
        
        score = 0.0
        max_score = 100.0
        
        # Presence score (40 points)
        if actual_disclosures:
            score += 40.0
        
        # Prominence score (30 points)
        prominent_disclosures = [
            d for d in actual_disclosures[:3]
            if any(keyword in d.lower() for keyword in ['ad', 'sponsored', 'paid'])
        ]
        if prominent_disclosures:
            score += 30.0
        
        # Clarity score (20 points)
        clear_disclosures = [
            d for d in actual_disclosures
            if len(d) > 5 and any(keyword in d.lower() for keyword in ['sponsored', 'partnership', 'affiliate'])
        ]
        if clear_disclosures:
            score += 20.0
        
        # Platform compliance score (10 points)
        platform_specific = await self._check_platform_specific_compliance(actual_disclosures, platform)
        if platform_specific:
            score += 10.0
        
        return min(score, max_score)
    
    async def _check_platform_specific_compliance(self, 
                                                disclosures: List[str],
                                                platform: str) -> bool:
        """Check platform-specific disclosure compliance"""
        platform_requirements = {
            "instagram": ["branded_content_tag", "paid_partnership_label"],
            "youtube": ["youtube_paid_promotion"],
            "tiktok": ["branded_content_toggle"],
            "facebook": ["branded_content_tag"]
        }
        
        required_indicators = platform_requirements.get(platform.lower(), [])
        
        if not required_indicators:
            return True  # No specific requirements
        
        return any(indicator in disclosures for indicator in required_indicators)
    
    async def _generate_disclosure_recommendations(self, 
                                                 required: List[DisclosureType],
                                                 actual: List[str],
                                                 platform: str,
                                                 compliance_check: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving disclosure compliance"""
        recommendations = []
        
        # Missing disclosures
        if compliance_check["missing"]:
            recommendations.append("Add required disclosure statements for missing types")
            for missing_type in compliance_check["missing"]:
                recommendations.append(f"Add {missing_type.value} disclosure")
        
        # Inadequate disclosures
        if compliance_check["inadequate"]:
            recommendations.append("Improve visibility and clarity of existing disclosures")
        
        # Platform-specific recommendations
        if platform.lower() == "instagram":
            recommendations.extend([
                "Use Instagram's branded content tools",
                "Place disclosures at the beginning of captions",
                "Use clear hashtags like #ad or #sponsored"
            ])
        
        elif platform.lower() == "youtube":
            recommendations.extend([
                "Include disclosure in video description",
                "Use YouTube's paid promotion disclosure",
                "Mention sponsorship verbally in video"
            ])
        
        elif platform.lower() == "tiktok":
            recommendations.extend([
                "Use TikTok's branded content toggle",
                "Include disclosure in video overlay",
                "Add clear hashtags in caption"
            ])
        
        # General best practices
        recommendations.extend([
            "Ensure disclosures are prominent and easily visible",
            "Use clear, unambiguous language",
            "Don't bury disclosures in long lists of hashtags",
            "Review FTC guidelines regularly"
        ])
        
        return list(set(recommendations))  # Remove duplicates
    
    async def _store_disclosure_assessment(self, assessment: DisclosureAssessment) -> None:
        """Store disclosure assessment in database"""
        try:
            record = DisclosureAssessmentRecord(
                assessment_id=assessment.assessment_id,
                creator_id=assessment.creator_id,
                content_id=assessment.content_id,
                platform=assessment.platform,
                required_disclosures=[dt.value for dt in assessment.required_disclosures],
                actual_disclosures=assessment.actual_disclosures,
                disclosure_compliance=assessment.disclosure_compliance,
                disclosure_quality_score=assessment.disclosure_quality_score,
                missing_disclosures=[dt.value for dt in assessment.missing_disclosures],
                inadequate_disclosures=assessment.inadequate_disclosures,
                recommendations=assessment.recommendations,
                assessment_date=assessment.assessment_date,
                reviewer=assessment.reviewer
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store disclosure assessment: {str(e)}")
            raise


class ContractComplianceManager:
    """Manages creator contract compliance and monitoring"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
    async def create_creator_contract(self, contract_data: Dict[str, Any]) -> CreatorContract:
        """Create new creator contract with compliance requirements"""
        try:
            contract_id = str(uuid.uuid4())
            
            # Parse contract requirements
            compliance_requirements = await self._parse_compliance_requirements(contract_data)
            
            # Determine disclosure requirements
            disclosure_requirements = await self._determine_disclosure_requirements(contract_data)
            
            contract = CreatorContract(
                contract_id=contract_id,
                creator_id=contract_data["creator_id"],
                brand_id=contract_data["brand_id"],
                contract_type=ContractType(contract_data["contract_type"]),
                contract_title=contract_data["contract_title"],
                start_date=datetime.fromisoformat(contract_data["start_date"]),
                end_date=datetime.fromisoformat(contract_data["end_date"]),
                compensation_amount=contract_data.get("compensation_amount", 0.0),
                compensation_type=contract_data.get("compensation_type", "fixed"),
                deliverables=contract_data.get("deliverables", []),
                compliance_requirements=compliance_requirements,
                disclosure_requirements=disclosure_requirements,
                content_guidelines=contract_data.get("content_guidelines", {}),
                exclusivity_clauses=contract_data.get("exclusivity_clauses", []),
                performance_metrics=contract_data.get("performance_metrics", {}),
                approval_process=contract_data.get("approval_process", {}),
                contract_status="draft",
                signed_date=None,
                metadata=contract_data.get("metadata", {})
            )
            
            # Store contract
            await self._store_creator_contract(contract)
            
            return contract
            
        except Exception as e:
            logger.error(f"Failed to create creator contract: {str(e)}")
            raise
    
    async def _parse_compliance_requirements(self, contract_data: Dict[str, Any]) -> List[str]:
        """Parse compliance requirements from contract data"""
        requirements = []
        
        contract_type = contract_data.get("contract_type")
        
        # Base requirements for all contracts
        requirements.extend([
            "ftc_disclosure_compliance",
            "brand_guideline_adherence",
            "content_approval_process",
            "performance_metric_tracking"
        ])
        
        # Type-specific requirements
        if contract_type == "brand_partnership":
            requirements.extend([
                "sponsored_content_disclosure",
                "brand_mention_requirements",
                "exclusivity_compliance"
            ])
        
        elif contract_type == "affiliate":
            requirements.extend([
                "affiliate_link_disclosure",
                "commission_tracking",
                "promotional_guideline_compliance"
            ])
        
        elif contract_type == "ambassador":
            requirements.extend([
                "brand_representation_standards",
                "ongoing_engagement_requirements",
                "exclusive_partnership_compliance"
            ])
        
        # Platform-specific requirements
        platforms = contract_data.get("target_platforms", [])
        for platform in platforms:
            requirements.append(f"{platform.lower()}_platform_compliance")
        
        return list(set(requirements))
    
    async def _determine_disclosure_requirements(self, contract_data: Dict[str, Any]) -> List[DisclosureType]:
        """Determine required disclosures based on contract type"""
        disclosures = []
        
        contract_type = contract_data.get("contract_type")
        compensation = contract_data.get("compensation_amount", 0)
        
        # Paid partnerships require sponsored content disclosure
        if compensation > 0 or contract_type in ["brand_partnership", "sponsorship"]:
            disclosures.extend([DisclosureType.SPONSORED, DisclosureType.PAID_PARTNERSHIP])
        
        # Affiliate contracts require affiliate disclosure
        if contract_type == "affiliate":
            disclosures.append(DisclosureType.AFFILIATE_LINK)
        
        # Gifted products require gifted disclosure
        if contract_data.get("includes_gifted_products", False):
            disclosures.append(DisclosureType.GIFTED)
        
        # Ambassador programs require ambassador disclosure
        if contract_type == "ambassador":
            disclosures.append(DisclosureType.BRAND_AMBASSADOR)
        
        return list(set(disclosures))
    
    async def _store_creator_contract(self, contract: CreatorContract) -> None:
        """Store creator contract in database"""
        try:
            record = CreatorContractRecord(
                contract_id=contract.contract_id,
                creator_id=contract.creator_id,
                brand_id=contract.brand_id,
                contract_type=contract.contract_type.value,
                contract_title=contract.contract_title,
                start_date=contract.start_date,
                end_date=contract.end_date,
                compensation_amount=contract.compensation_amount,
                compensation_type=contract.compensation_type,
                deliverables=contract.deliverables,
                compliance_requirements=contract.compliance_requirements,
                disclosure_requirements=[dr.value for dr in contract.disclosure_requirements],
                content_guidelines=contract.content_guidelines,
                exclusivity_clauses=contract.exclusivity_clauses,
                performance_metrics=contract.performance_metrics,
                approval_process=contract.approval_process,
                contract_status=contract.contract_status,
                signed_date=contract.signed_date,
                metadata=contract.metadata
            )
            
            self.db.add(record)
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Failed to store creator contract: {str(e)}")
            raise


# Main Creator Compliance Engine
class CreatorCompliance:
    """Main creator compliance management engine"""
    
    def __init__(self, db_session -> None: AsyncSession, redis_client -> None: aioredis.Redis) -> None:
        self.db = db_session
        self.redis = redis_client
        
        # Initialize components
        self.profile_manager = CreatorProfileManager(db_session, redis_client)
        self.disclosure_manager = DisclosureComplianceManager(db_session, redis_client)
        self.contract_manager = ContractComplianceManager(db_session, redis_client)
        
    async def conduct_comprehensive_creator_compliance_audit(self, 
                                                           creator_id: str,
                                                           audit_scope: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive compliance audit for creator"""
        try:
            audit_id = str(uuid.uuid4())
            
            # Get creator profile
            creator_profile = await self._get_creator_profile(creator_id)
            
            # Audit components
            audit_results = {}
            
            # 1. Profile compliance audit
            profile_audit = await self._audit_profile_compliance(creator_profile)
            audit_results["profile_compliance"] = profile_audit
            
            # 2. Disclosure compliance audit
            disclosure_audit = await self._audit_disclosure_compliance(
                creator_id, audit_scope.get("content_sample", [])
            )
            audit_results["disclosure_compliance"] = disclosure_audit
            
            # 3. Contract compliance audit
            contract_audit = await self._audit_contract_compliance(creator_id)
            audit_results["contract_compliance"] = contract_audit
            
            # 4. Platform compliance audit
            platform_audit = await self._audit_platform_compliance(
                creator_id, creator_profile.platforms
            )
            audit_results["platform_compliance"] = platform_audit
            
            # 5. Content compliance audit
            content_audit = await self._audit_content_compliance(
                creator_id, audit_scope.get("content_sample", [])
            )
            audit_results["content_compliance"] = content_audit
            
            # Calculate overall compliance score
            overall_score = await self._calculate_overall_compliance_score(audit_results)
            
            # Generate compliance recommendations
            recommendations = await self._generate_compliance_recommendations(audit_results)
            
            # Identify compliance risks
            risk_assessment = await self._assess_compliance_risks(audit_results, creator_profile)
            
            # Generate action plan
            action_plan = await self._generate_compliance_action_plan(audit_results, recommendations)
            
            comprehensive_audit = {
                "audit_id": audit_id,
                "creator_id": creator_id,
                "audit_scope": audit_scope,
                "audit_results": audit_results,
                "overall_compliance_score": overall_score,
                "recommendations": recommendations,
                "risk_assessment": risk_assessment,
                "action_plan": action_plan,
                "audit_date": datetime.utcnow().isoformat(),
                "next_audit_date": (datetime.utcnow() + timedelta(days=90)).isoformat(),
                "auditor": "automated_compliance_system"
            }
            
            # Cache audit results
            await self.redis.setex(f"creator_compliance_audit:{audit_id}", 3600 * 24 * 30,
                                  json.dumps(comprehensive_audit, default=str))
            
            return comprehensive_audit
            
        except Exception as e:
            logger.error(f"Creator compliance audit failed: {str(e)}")
            raise
    
    async def _get_creator_profile(self, creator_id: str) -> Optional[CreatorProfile]:
        """Get creator profile from database"""
        # Implementation would query database
        # For now, return mock profile
        return CreatorProfile(
            creator_id=creator_id,
            creator_name="Mock Creator",
            creator_type=CreatorType.INFLUENCER,
            creator_tier=CreatorTier.MICRO,
            platforms=["instagram", "youtube", "tiktok"],
            follower_counts={"instagram": 50000, "youtube": 25000, "tiktok": 30000},
            engagement_rates={"instagram": 0.035, "youtube": 0.028, "tiktok": 0.045},
            primary_categories=["lifestyle", "fashion", "beauty"],
            target_demographics={"age_range": "18-34", "gender": "female_majority"},
            compliance_status=ComplianceStatus.COMPLIANT,
            compliance_score=85.0,
            active_contracts=["contract_1", "contract_2"],
            violation_history=[],
            certification_status={"ftc_training": True, "platform_certification": False},
            last_compliance_review=datetime.utcnow() - timedelta(days=60),
            next_review_date=datetime.utcnow() + timedelta(days=30),
            profile_created=datetime.utcnow() - timedelta(days=365),
            metadata={}
        )
    
    async def _audit_profile_compliance(self, profile: CreatorProfile) -> Dict[str, Any]:
        """Audit creator profile compliance"""
        audit = {
            "profile_completeness": 0.0,
            "verification_status": {},
            "compliance_certifications": {},
            "issues": [],
            "score": 0.0
        }
        
        # Check profile completeness
        required_fields = ["creator_name", "creator_type", "platforms", "primary_categories"]
        completed_fields = sum(1 for field in required_fields if getattr(profile, field, None))
        audit["profile_completeness"] = completed_fields / len(required_fields)
        
        # Check verification status
        for platform in profile.platforms:
            audit["verification_status"][platform] = profile.metadata.get(f"{platform}_verified", False)
        
        # Check compliance certifications
        audit["compliance_certifications"] = profile.certification_status
        
        # Identify issues
        if audit["profile_completeness"] < 1.0:
            audit["issues"].append("incomplete_profile")
        
        if not any(audit["verification_status"].values()):
            audit["issues"].append("no_platform_verification")
        
        if not audit["compliance_certifications"].get("ftc_training"):
            audit["issues"].append("missing_ftc_training")
        
        # Calculate score
        base_score = audit["profile_completeness"] * 40
        verification_score = len([v for v in audit["verification_status"].values() if v]) / len(profile.platforms) * 30
        certification_score = len([c for c in audit["compliance_certifications"].values() if c]) * 15
        
        audit["score"] = base_score + verification_score + certification_score
        
        return audit
    
    async def _audit_disclosure_compliance(self, 
                                         creator_id: str,
                                         content_sample: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit disclosure compliance across content sample"""
        audit = {
            "total_content_reviewed": len(content_sample),
            "compliant_content": 0,
            "disclosure_rate": 0.0,
            "common_violations": [],
            "score": 0.0
        }
        
        if not content_sample:
            return audit
        
        compliant_count = 0
        violation_types = defaultdict(int)
        
        for content in content_sample:
            # Perform disclosure assessment
            assessment = await self.disclosure_manager.assess_disclosure_compliance(
                creator_id=creator_id,
                content_id=content.get("content_id", str(uuid.uuid4())),
                platform=content.get("platform", "unknown"),
                content_data=content,
                contract_requirements=None
            )
            
            if assessment.disclosure_compliance:
                compliant_count += 1
            else:
                for violation in assessment.inadequate_disclosures:
                    violation_types[violation] += 1
        
        audit["compliant_content"] = compliant_count
        audit["disclosure_rate"] = compliant_count / len(content_sample)
        audit["common_violations"] = [
            {"violation": violation, "count": count}
            for violation, count in violation_types.most_common(5)
        ]
        audit["score"] = audit["disclosure_rate"] * 100
        
        return audit
    
    async def _audit_contract_compliance(self, creator_id: str) -> Dict[str, Any]:
        """Audit contract compliance"""
        audit = {
            "active_contracts": 0,
            "compliant_contracts": 0,
            "compliance_rate": 0.0,
            "common_issues": [],
            "score": 0.0
        }
        
        # Mock contract compliance audit
        # In real implementation, would query contract database
        audit["active_contracts"] = 3
        audit["compliant_contracts"] = 2
        audit["compliance_rate"] = 2/3
        audit["common_issues"] = ["missing_performance_metrics", "unclear_deliverables"]
        audit["score"] = audit["compliance_rate"] * 100
        
        return audit
    
    async def _audit_platform_compliance(self, 
                                       creator_id: str,
                                       platforms: List[str]) -> Dict[str, Any]:
        """Audit platform-specific compliance"""
        audit = {
            "platforms_reviewed": platforms,
            "platform_scores": {},
            "average_score": 0.0,
            "common_issues": []
        }
        
        total_score = 0.0
        all_issues = []
        
        for platform in platforms:
            # Mock platform compliance check
            platform_score = 85.0  # Would be calculated based on platform-specific rules
            platform_issues = ["missing_business_account", "incomplete_bio"]
            
            audit["platform_scores"][platform] = {
                "score": platform_score,
                "issues": platform_issues
            }
            
            total_score += platform_score
            all_issues.extend(platform_issues)
        
        audit["average_score"] = total_score / len(platforms) if platforms else 0.0
        audit["common_issues"] = list(set(all_issues))
        
        return audit
    
    async def _audit_content_compliance(self, 
                                      creator_id: str,
                                      content_sample: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit content compliance"""
        audit = {
            "content_reviewed": len(content_sample),
            "compliant_content": 0,
            "compliance_rate": 0.0,
            "content_violations": [],
            "score": 0.0
        }
        
        if not content_sample:
            return audit
        
        compliant_count = 0
        violations = []
        
        for content in content_sample:
            # Mock content compliance check
            is_compliant = True
            content_violations = []
            
            # Check for inappropriate content
            text_content = f"{content.get('title', '')} {content.get('description', '')}"
            if any(word in text_content.lower() for word in ["inappropriate", "violation"]):
                is_compliant = False
                content_violations.append("inappropriate_content")
            
            # Check copyright compliance
            if not content.get("copyright_cleared", True):
                is_compliant = False
                content_violations.append("copyright_issue")
            
            if is_compliant:
                compliant_count += 1
            else:
                violations.extend(content_violations)
        
        audit["compliant_content"] = compliant_count
        audit["compliance_rate"] = compliant_count / len(content_sample)
        audit["content_violations"] = list(set(violations))
        audit["score"] = audit["compliance_rate"] * 100
        
        return audit
    
    async def _calculate_overall_compliance_score(self, audit_results: Dict[str, Any]) -> float:
        """Calculate overall compliance score from audit results"""
        scores = []
        weights = {
            "profile_compliance": 0.2,
            "disclosure_compliance": 0.3,
            "contract_compliance": 0.2,
            "platform_compliance": 0.15,
            "content_compliance": 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for area, weight in weights.items():
            if area in audit_results and "score" in audit_results[area]:
                weighted_score += audit_results[area]["score"] * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    async def _generate_compliance_recommendations(self, audit_results: Dict[str, Any]) -> List[str]:
        """Generate compliance recommendations based on audit results"""
        recommendations = []
        
        # Profile recommendations
        if audit_results.get("profile_compliance", {}).get("score", 100) < 80:
            recommendations.append("Complete creator profile with all required information")
            recommendations.append("Obtain platform verification where possible")
            recommendations.append("Complete FTC compliance training")
        
        # Disclosure recommendations
        if audit_results.get("disclosure_compliance", {}).get("score", 100) < 80:
            recommendations.append("Improve disclosure compliance across all sponsored content")
            recommendations.append("Use platform-specific disclosure tools")
            recommendations.append("Review FTC guidelines for proper disclosure practices")
        
        # Contract recommendations
        if audit_results.get("contract_compliance", {}).get("score", 100) < 80:
            recommendations.append("Review active contracts for compliance requirements")
            recommendations.append("Establish clear performance tracking systems")
            recommendations.append("Ensure all deliverables are clearly defined")
        
        # General recommendations
        recommendations.extend([
            "Implement regular compliance self-audits",
            "Stay updated on platform policy changes",
            "Maintain detailed records of all sponsored content",
            "Consider professional compliance consultation"
        ])
        
        return recommendations
    
    async def _assess_compliance_risks(self, 
                                     audit_results: Dict[str, Any],
                                     creator_profile: CreatorProfile) -> Dict[str, Any]:
        """Assess compliance risks"""
        risk_assessment = {
            "overall_risk_level": "low",
            "risk_factors": [],
            "risk_score": 0.0,
            "mitigation_strategies": []
        }
        
        risk_score = 0.0
        
        # Calculate risk based on audit results
        for area, results in audit_results.items():
            if results.get("score", 100) < 60:
                risk_score += 20
                risk_assessment["risk_factors"].append(f"low_{area}_score")
        
        # Additional risk factors
        if creator_profile.violation_history:
            risk_score += len(creator_profile.violation_history) * 10
            risk_assessment["risk_factors"].append("violation_history")
        
        if creator_profile.creator_tier in [CreatorTier.MEGA, CreatorTier.CELEBRITY]:
            risk_score += 15  # Higher visibility = higher risk
            risk_assessment["risk_factors"].append("high_visibility")
        
        # Determine risk level
        if risk_score >= 60:
            risk_assessment["overall_risk_level"] = "high"
        elif risk_score >= 30:
            risk_assessment["overall_risk_level"] = "medium"
        else:
            risk_assessment["overall_risk_level"] = "low"
        
        risk_assessment["risk_score"] = min(risk_score, 100.0)
        
        # Generate mitigation strategies
        if risk_score > 30:
            risk_assessment["mitigation_strategies"] = [
                "Implement enhanced compliance monitoring",
                "Provide additional compliance training",
                "Establish more frequent review cycles",
                "Consider professional compliance support"
            ]
        
        return risk_assessment
    
    async def _generate_compliance_action_plan(self, 
                                             audit_results: Dict[str, Any],
                                             recommendations: List[str]) -> Dict[str, Any]:
        """Generate compliance action plan"""
        action_plan = {
            "immediate_actions": [],
            "short_term_goals": [],
            "long_term_objectives": [],
            "timeline": {
                "immediate": "1-2 weeks",
                "short_term": "1-3 months",
                "long_term": "3-12 months"
            }
        }
        
        # Immediate actions (critical issues)
        for area, results in audit_results.items():
            if results.get("score", 100) < 50:
                action_plan["immediate_actions"].append(f"Address critical {area} issues")
        
        # Short-term goals
        action_plan["short_term_goals"] = [
            "Achieve 90%+ disclosure compliance rate",
            "Complete all required compliance certifications",
            "Implement systematic compliance review process"
        ]
        
        # Long-term objectives
        action_plan["long_term_objectives"] = [
            "Maintain sustained compliance excellence",
            "Develop compliance best practices documentation",
            "Mentor other creators on compliance practices"
        ]
        
        return action_plan


# Export main classes
__all__ = [
    "CreatorCompliance",
    "CreatorProfileManager",
    "DisclosureComplianceManager",
    "ContractComplianceManager",
    "CreatorType",
    "CreatorTier",
    "ContractType",
    "ComplianceArea",
    "ViolationType",
    "ComplianceStatus",
    "DisclosureType",
    "CreatorProfile",
    "CreatorContract",
    "ComplianceViolation",
    "DisclosureAssessment",
    "CreatorCertification"
]
