"""
Collaboration Licensing System - IA Influencer Agent + Content Protection Platform

Advanced collaboration licensing for multi-format creators enabling seamless
creator-to-creator licensing, collaboration rights management, and revenue sharing.

Business Logic: Creator → Collaboration Matching → License Agreement → Revenue Sharing → Distribution

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use prohibited.
"""

from typing import Dict, List, Any, Optional, Union, Tuple, Set
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
from dataclasses import dataclass, asdict
import uuid
import json

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of creative collaborations."""
    MUSIC_FEATURING = "music_featuring"
    REMIX_COLLABORATION = "remix_collaboration"
    PODCAST_GUEST = "podcast_guest"
    PHOTO_SHOOT = "photo_shoot"
    CONTENT_CREATION = "content_creation"
    CROSS_PROMOTION = "cross_promotion"
    LIVE_PERFORMANCE = "live_performance"
    JOINT_VENTURE = "joint_venture"


class LicenseScope(Enum):
    """Scope of collaboration license."""
    SINGLE_PROJECT = "single_project"
    SERIES_PROJECT = "series_project"
    ONGOING_PARTNERSHIP = "ongoing_partnership"
    EXCLUSIVE_COLLABORATION = "exclusive_collaboration"
    NON_EXCLUSIVE = "non_exclusive"


class RevenueModel(Enum):
    """Revenue sharing models."""
    EQUAL_SPLIT = "equal_split"
    WEIGHTED_SPLIT = "weighted_split"
    LEAD_CREATOR_MAJORITY = "lead_creator_majority"
    PERFORMANCE_BASED = "performance_based"
    FLAT_FEE = "flat_fee"
    ROYALTY_ONLY = "royalty_only"


class CollaborationStatus(Enum):
    """Status of collaboration."""
    PROPOSED = "proposed"
    NEGOTIATING = "negotiating"
    AGREED = "agreed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


@dataclass
class CollaborationProposal:
    """Collaboration proposal structure."""
    proposal_id: str
    proposer_id: str
    proposer_type: str  # CreatorType
    target_creator_id: str
    target_creator_type: str
    collaboration_type: CollaborationType
    project_description: str
    proposed_terms: Dict[str, Any]
    revenue_model: RevenueModel
    license_scope: LicenseScope
    duration: Optional[timedelta]
    territory: str
    status: CollaborationStatus
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]


@dataclass
class CollaborationAgreement:
    """Executed collaboration agreement."""
    agreement_id: str
    proposal_id: str
    collaborators: List[Dict[str, Any]]  # [{creator_id, creator_type, role, contribution_weight}]
    collaboration_type: CollaborationType
    license_terms: Dict[str, Any]
    revenue_sharing: Dict[str, float]  # creator_id -> percentage
    intellectual_property_terms: Dict[str, Any]
    deliverables: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    status: CollaborationStatus
    signed_at: datetime
    effective_date: datetime
    expiration_date: Optional[datetime]
    automated_tracking: bool


@dataclass
class CollaborationRevenue:
    """Revenue tracking for collaborations."""
    revenue_id: str
    agreement_id: str
    content_id: str
    platform: str
    revenue_amount: float
    currency: str
    revenue_date: datetime
    distribution_calculated: bool
    payouts_processed: bool
    metadata: Dict[str, Any]


@dataclass
class CreatorProfile:
    """Creator profile for collaboration matching."""
    creator_id: str
    creator_type: str
    specialties: List[str]
    portfolio_stats: Dict[str, Any]
    collaboration_history: List[str]
    preferred_collaboration_types: List[CollaborationType]
    availability: Dict[str, Any]
    rate_card: Dict[str, float]
    reputation_score: float
    verification_level: str


class CollaborationLicensingManager:
    """
    Advanced collaboration licensing system.
    
    Manages creator-to-creator collaborations, licensing agreements,
    and automated revenue sharing in the IA Influencer ecosystem.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the Collaboration Licensing Manager."""
        self.config = config
        self.db_config = config.get("database", {})
        self.collaboration_config = config.get("collaboration", {})
        
        # Core registries
        self.proposals: Dict[str, CollaborationProposal] = {}
        self.agreements: Dict[str, CollaborationAgreement] = {}
        self.revenue_records: Dict[str, List[CollaborationRevenue]] = {}
        self.creator_profiles: Dict[str, CreatorProfile] = {}
        
        # Collaboration networks
        self.collaboration_networks: Dict[str, Set[str]] = {}  # creator_id -> connected_creators
        self.active_collaborations: Dict[str, List[str]] = {}  # creator_id -> agreement_ids
        
        # AI matching settings
        self.enable_ai_matching = self.collaboration_config.get("enable_ai_matching", True)
        self.matching_threshold = self.collaboration_config.get("matching_threshold", 0.75)
        self.auto_agreements = self.collaboration_config.get("auto_agreements", False)
        
        logger.info("Collaboration Licensing Manager initialized successfully")
    
    async def create_collaboration_proposal(
        self,
        proposer_id: str,
        proposer_type: str,
        target_creator_id: str,
        collaboration_type: CollaborationType,
        project_description: str,
        proposed_terms: Dict[str, Any],
        revenue_model: RevenueModel = RevenueModel.EQUAL_SPLIT,
        duration_days: Optional[int] = None
    ) -> CollaborationProposal:
        """
        Create a new collaboration proposal.
        
        Args:
            proposer_id: ID of creator making the proposal
            proposer_type: Type of proposing creator
            target_creator_id: ID of target creator
            collaboration_type: Type of collaboration
            project_description: Description of the collaboration project
            proposed_terms: Detailed terms and conditions
            revenue_model: Revenue sharing model
            duration_days: Duration in days (optional)
        """
        try:
            # Validate creators exist and are compatible
            await self._validate_collaboration_compatibility(
                proposer_id, target_creator_id, collaboration_type
            )
            
            # Get target creator type
            target_profile = self.creator_profiles.get(target_creator_id)
            target_creator_type = target_profile.creator_type if target_profile else "unknown"
            
            proposal = CollaborationProposal(
                proposal_id=str(uuid.uuid4()),
                proposer_id=proposer_id,
                proposer_type=proposer_type,
                target_creator_id=target_creator_id,
                target_creator_type=target_creator_type,
                collaboration_type=collaboration_type,
                project_description=project_description,
                proposed_terms=proposed_terms,
                revenue_model=revenue_model,
                license_scope=LicenseScope.SINGLE_PROJECT,
                duration=timedelta(days=duration_days) if duration_days else None,
                territory="GLOBAL",
                status=CollaborationStatus.PROPOSED,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=30),  # 30-day expiration
                metadata={}
            )
            
            # Store proposal
            self.proposals[proposal.proposal_id] = proposal
            
            # Update collaboration networks
            if proposer_id not in self.collaboration_networks:
                self.collaboration_networks[proposer_id] = set()
            self.collaboration_networks[proposer_id].add(target_creator_id)
            
            logger.info(f"Collaboration proposal created: {proposal.proposal_id}")
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to create collaboration proposal: {e}")
            raise
    
    async def _validate_collaboration_compatibility(
        self,
        proposer_id: str,
        target_creator_id: str,
        collaboration_type: CollaborationType
    ) -> bool:
        """Validate that creators are compatible for collaboration."""
        # Check if creators exist
        proposer_profile = self.creator_profiles.get(proposer_id)
        target_profile = self.creator_profiles.get(target_creator_id)
        
        if not proposer_profile or not target_profile:
            raise ValueError("Creator profiles not found")
        
        # Check if target creator accepts this collaboration type
        if collaboration_type not in target_profile.preferred_collaboration_types:
            logger.warning(f"Target creator {target_creator_id} doesn't prefer {collaboration_type.value}")
        
        # Check availability
        if not target_profile.availability.get("accepting_collaborations", True):
            raise ValueError("Target creator is not accepting collaborations")
        
        # Check reputation scores
        min_reputation = 0.7
        if (proposer_profile.reputation_score < min_reputation or 
            target_profile.reputation_score < min_reputation):
            logger.warning("Low reputation score detected for collaboration")
        
        return True
    
    async def respond_to_proposal(
        self,
        proposal_id: str,
        responder_id: str,
        response: str,  # "accept", "reject", "counter"
        counter_terms: Optional[Dict[str, Any]] = None
    ) -> CollaborationProposal:
        """Respond to a collaboration proposal."""
        try:
            proposal = self.proposals.get(proposal_id)
            if not proposal:
                raise ValueError(f"Proposal {proposal_id} not found")
            
            if proposal.target_creator_id != responder_id:
                raise ValueError("Only target creator can respond to proposal")
            
            if response == "accept":
                proposal.status = CollaborationStatus.AGREED
                # Automatically create agreement
                await self._create_collaboration_agreement(proposal)
                
            elif response == "reject":
                proposal.status = CollaborationStatus.CANCELLED
                
            elif response == "counter":
                proposal.status = CollaborationStatus.NEGOTIATING
                if counter_terms:
                    proposal.proposed_terms.update(counter_terms)
                    proposal.metadata["counter_offer"] = {
                        "terms": counter_terms,
                        "timestamp": datetime.utcnow().isoformat()
                    }
            
            logger.info(f"Proposal {proposal_id} responded with: {response}")
            return proposal
            
        except Exception as e:
            logger.error(f"Failed to respond to proposal {proposal_id}: {e}")
            raise
    
    async def _create_collaboration_agreement(
        self,
        proposal: CollaborationProposal
    ) -> CollaborationAgreement:
        """Create a binding collaboration agreement from an accepted proposal."""
        try:
            # Build collaborators list
            collaborators = [
                {
                    "creator_id": proposal.proposer_id,
                    "creator_type": proposal.proposer_type,
                    "role": "lead_creator",
                    "contribution_weight": 0.6
                },
                {
                    "creator_id": proposal.target_creator_id,
                    "creator_type": proposal.target_creator_type,
                    "role": "collaborator",
                    "contribution_weight": 0.4
                }
            ]
            
            # Calculate revenue sharing based on model
            revenue_sharing = await self._calculate_revenue_sharing(
                proposal.revenue_model, collaborators
            )
            
            # Generate license terms
            license_terms = await self._generate_license_terms(
                proposal.collaboration_type, proposal.proposed_terms
            )
            
            agreement = CollaborationAgreement(
                agreement_id=str(uuid.uuid4()),
                proposal_id=proposal.proposal_id,
                collaborators=collaborators,
                collaboration_type=proposal.collaboration_type,
                license_terms=license_terms,
                revenue_sharing=revenue_sharing,
                intellectual_property_terms=await self._generate_ip_terms(proposal),
                deliverables=proposal.proposed_terms.get("deliverables", []),
                milestones=proposal.proposed_terms.get("milestones", []),
                status=CollaborationStatus.ACTIVE,
                signed_at=datetime.utcnow(),
                effective_date=datetime.utcnow(),
                expiration_date=datetime.utcnow() + proposal.duration if proposal.duration else None,
                automated_tracking=True
            )
            
            # Store agreement
            self.agreements[agreement.agreement_id] = agreement
            
            # Update active collaborations tracking
            for collaborator in collaborators:
                creator_id = collaborator["creator_id"]
                if creator_id not in self.active_collaborations:
                    self.active_collaborations[creator_id] = []
                self.active_collaborations[creator_id].append(agreement.agreement_id)
            
            logger.info(f"Collaboration agreement created: {agreement.agreement_id}")
            return agreement
            
        except Exception as e:
            logger.error(f"Failed to create collaboration agreement: {e}")
            raise
    
    async def _calculate_revenue_sharing(
        self,
        revenue_model: RevenueModel,
        collaborators: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate revenue sharing percentages based on model."""
        sharing = {}
        
        if revenue_model == RevenueModel.EQUAL_SPLIT:
            percentage = 1.0 / len(collaborators)
            for collaborator in collaborators:
                sharing[collaborator["creator_id"]] = percentage
                
        elif revenue_model == RevenueModel.WEIGHTED_SPLIT:
            total_weight = sum(c["contribution_weight"] for c in collaborators)
            for collaborator in collaborators:
                sharing[collaborator["creator_id"]] = collaborator["contribution_weight"] / total_weight
                
        elif revenue_model == RevenueModel.LEAD_CREATOR_MAJORITY:
            lead_creator = next(c for c in collaborators if c["role"] == "lead_creator")
            sharing[lead_creator["creator_id"]] = 0.7
            
            remaining = 0.3 / (len(collaborators) - 1)
            for collaborator in collaborators:
                if collaborator["role"] != "lead_creator":
                    sharing[collaborator["creator_id"]] = remaining
        
        return sharing
    
    async def _generate_license_terms(
        self,
        collaboration_type: CollaborationType,
        proposed_terms: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific license terms based on collaboration type."""
        base_terms = {
            "usage_rights": "shared",
            "attribution_required": True,
            "modification_rights": "with_approval",
            "distribution_rights": "shared",
            "territory": "global",
            "exclusivity": False
        }
        
        # Collaboration-specific terms
        if collaboration_type == CollaborationType.MUSIC_FEATURING:
            base_terms.update({
                "performance_rights": "shared",
                "mechanical_rights": "shared",
                "synchronization_rights": "shared",
                "remix_rights": "with_approval"
            })
        elif collaboration_type == CollaborationType.PHOTO_SHOOT:
            base_terms.update({
                "commercial_usage": "shared",
                "editorial_usage": "shared",
                "model_releases_required": True,
                "watermark_removal": "prohibited"
            })
        elif collaboration_type == CollaborationType.CONTENT_CREATION:
            base_terms.update({
                "platform_rights": "shared",
                "monetization_rights": "shared",
                "cross_promotion": "allowed",
                "archive_rights": "shared"
            })
        
        # Override with proposed terms
        base_terms.update(proposed_terms.get("license_terms", {}))
        
        return base_terms
    
    async def _generate_ip_terms(
        self,
        proposal: CollaborationProposal
    ) -> Dict[str, Any]:
        """Generate intellectual property terms for the collaboration."""
        return {
            "joint_ownership": True,
            "individual_contributions_recognized": True,
            "derivative_works_approval": "mutual_consent",
            "third_party_licensing": "shared_approval",
            "termination_rights": {
                "notice_period_days": 30,
                "continued_usage_rights": True,
                "revenue_share_continuation": "until_completion"
            },
            "dispute_resolution": "mediation_then_arbitration",
            "confidentiality": {
                "duration_months": 12,
                "scope": "project_specific"
            }
        }
    
    async def track_collaboration_revenue(
        self,
        agreement_id: str,
        content_id: str,
        platform: str,
        revenue_amount: float,
        currency: str = "EUR"
    ) -> CollaborationRevenue:
        """Track revenue for collaborative content."""
        try:
            agreement = self.agreements.get(agreement_id)
            if not agreement:
                raise ValueError(f"Agreement {agreement_id} not found")
            
            revenue_record = CollaborationRevenue(
                revenue_id=str(uuid.uuid4()),
                agreement_id=agreement_id,
                content_id=content_id,
                platform=platform,
                revenue_amount=revenue_amount,
                currency=currency,
                revenue_date=datetime.utcnow(),
                distribution_calculated=False,
                payouts_processed=False,
                metadata={}
            )
            
            # Store revenue record
            if agreement_id not in self.revenue_records:
                self.revenue_records[agreement_id] = []
            self.revenue_records[agreement_id].append(revenue_record)
            
            # Trigger automatic distribution calculation
            if agreement.automated_tracking:
                await self._calculate_revenue_distribution(revenue_record, agreement)
            
            logger.info(f"Revenue tracked for collaboration: {revenue_amount} {currency}")
            return revenue_record
            
        except Exception as e:
            logger.error(f"Failed to track collaboration revenue: {e}")
            raise
    
    async def _calculate_revenue_distribution(
        self,
        revenue_record: CollaborationRevenue,
        agreement: CollaborationAgreement
    ) -> Dict[str, float]:
        """Calculate revenue distribution based on agreement terms."""
        try:
            distribution = {}
            
            for creator_id, percentage in agreement.revenue_sharing.items():
                amount = revenue_record.revenue_amount * percentage
                distribution[creator_id] = amount
            
            # Mark as calculated
            revenue_record.distribution_calculated = True
            revenue_record.metadata["distribution"] = distribution
            revenue_record.metadata["calculated_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Revenue distribution calculated for {revenue_record.revenue_id}")
            return distribution
            
        except Exception as e:
            logger.error(f"Failed to calculate revenue distribution: {e}")
            raise
    
    async def find_collaboration_matches(
        self,
        creator_id: str,
        collaboration_type: CollaborationType,
        project_requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find potential collaboration matches using AI matching."""
        try:
            if not self.enable_ai_matching:
                return []
            
            creator_profile = self.creator_profiles.get(creator_id)
            if not creator_profile:
                raise ValueError(f"Creator profile not found for {creator_id}")
            
            matches = []
            
            for target_id, target_profile in self.creator_profiles.items():
                if target_id == creator_id:
                    continue
                
                # Check if target accepts this collaboration type
                if collaboration_type not in target_profile.preferred_collaboration_types:
                    continue
                
                # Check availability
                if not target_profile.availability.get("accepting_collaborations", True):
                    continue
                
                # Calculate match score
                match_score = await self._calculate_match_score(
                    creator_profile, target_profile, collaboration_type, project_requirements
                )
                
                if match_score >= self.matching_threshold:
                    matches.append({
                        "creator_id": target_id,
                        "creator_type": target_profile.creator_type,
                        "match_score": match_score,
                        "specialties": target_profile.specialties,
                        "reputation_score": target_profile.reputation_score,
                        "collaboration_history_count": len(target_profile.collaboration_history),
                        "estimated_rate": target_profile.rate_card.get(collaboration_type.value, 0.0)
                    })
            
            # Sort by match score
            matches.sort(key=lambda x: x["match_score"], reverse=True)
            
            logger.info(f"Found {len(matches)} collaboration matches for {creator_id}")
            return matches[:10]  # Return top 10 matches
            
        except Exception as e:
            logger.error(f"Failed to find collaboration matches: {e}")
            raise
    
    async def _calculate_match_score(
        self,
        requester_profile: CreatorProfile,
        candidate_profile: CreatorProfile,
        collaboration_type: CollaborationType,
        project_requirements: Dict[str, Any]
    ) -> float:
        """Calculate AI-based match score between creators."""
        score = 0.0
        
        # Reputation compatibility (20%)
        rep_diff = abs(requester_profile.reputation_score - candidate_profile.reputation_score)
        reputation_score = max(0.0, 1.0 - rep_diff) * 0.2
        score += reputation_score
        
        # Specialty matching (30%)
        required_specialties = project_requirements.get("required_specialties", [])
        specialty_matches = len(set(required_specialties) & set(candidate_profile.specialties))
        specialty_score = (specialty_matches / max(len(required_specialties), 1)) * 0.3
        score += specialty_score
        
        # Collaboration history (20%)
        if candidate_profile.collaboration_history:
            history_score = min(len(candidate_profile.collaboration_history) / 10.0, 1.0) * 0.2
            score += history_score
        
        # Collaboration type preference (20%)
        if collaboration_type in candidate_profile.preferred_collaboration_types:
            score += 0.2
        
        # Portfolio compatibility (10%)
        portfolio_score = self._calculate_portfolio_compatibility(
            requester_profile.portfolio_stats, candidate_profile.portfolio_stats
        ) * 0.1
        score += portfolio_score
        
        return min(score, 1.0)
    
    def _calculate_portfolio_compatibility(
        self,
        requester_stats: Dict[str, Any],
        candidate_stats: Dict[str, Any]
    ) -> float:
        """Calculate portfolio compatibility score."""
        # Simplified compatibility based on similar metrics
        compatible_metrics = 0
        total_metrics = 0
        
        for metric in ["total_content", "avg_engagement", "platform_diversity"]:
            if metric in requester_stats and metric in candidate_stats:
                total_metrics += 1
                req_value = requester_stats[metric]
                cand_value = candidate_stats[metric]
                
                if isinstance(req_value, (int, float)) and isinstance(cand_value, (int, float)):
                    # Calculate similarity (closer values = more compatible)
                    if max(req_value, cand_value) > 0:
                        similarity = min(req_value, cand_value) / max(req_value, cand_value)
                        if similarity >= 0.7:  # 70% similarity threshold
                            compatible_metrics += 1
        
        return compatible_metrics / max(total_metrics, 1)
    
    async def generate_collaboration_report(
        self,
        creator_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive collaboration report for a creator."""
        try:
            period_start = datetime.utcnow() - timedelta(days=period_days)
            
            # Get creator's active collaborations
            active_agreements = [
                self.agreements[agreement_id]
                for agreement_id in self.active_collaborations.get(creator_id, [])
                if self.agreements[agreement_id].status == CollaborationStatus.ACTIVE
            ]
            
            # Calculate revenue from collaborations
            total_collaboration_revenue = 0.0
            for agreement in active_agreements:
                agreement_revenue = self.revenue_records.get(agreement.agreement_id, [])
                creator_share = agreement.revenue_sharing.get(creator_id, 0.0)
                for revenue in agreement_revenue:
                    if revenue.revenue_date >= period_start:
                        total_collaboration_revenue += revenue.revenue_amount * creator_share
            
            # Get collaboration network size
            network_size = len(self.collaboration_networks.get(creator_id, set()))
            
            # Count proposals made and received
            proposals_made = len([
                p for p in self.proposals.values()
                if p.proposer_id == creator_id and p.created_at >= period_start
            ])
            
            proposals_received = len([
                p for p in self.proposals.values()
                if p.target_creator_id == creator_id and p.created_at >= period_start
            ])
            
            report = {
                "creator_id": creator_id,
                "report_period": f"{period_start.date()} to {datetime.utcnow().date()}",
                "collaboration_statistics": {
                    "active_collaborations": len(active_agreements),
                    "total_collaboration_revenue": total_collaboration_revenue,
                    "network_size": network_size,
                    "proposals_made": proposals_made,
                    "proposals_received": proposals_received
                },
                "collaboration_breakdown": await self._get_collaboration_breakdown(active_agreements),
                "top_collaborators": await self._get_top_collaborators(creator_id),
                "revenue_by_platform": await self._get_collaboration_revenue_by_platform(active_agreements, creator_id),
                "recommendations": await self._generate_collaboration_recommendations(creator_id),
                "generated_at": datetime.utcnow()
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate collaboration report for {creator_id}: {e}")
            raise
    
    async def _get_collaboration_breakdown(
        self,
        agreements: List[CollaborationAgreement]
    ) -> Dict[str, int]:
        """Get breakdown of collaborations by type."""
        breakdown = {}
        for agreement in agreements:
            collab_type = agreement.collaboration_type.value
            breakdown[collab_type] = breakdown.get(collab_type, 0) + 1
        return breakdown
    
    async def _get_top_collaborators(
        self,
        creator_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top collaborators by revenue and frequency."""
        collaborator_stats = {}
        
        # Aggregate collaboration data
        for agreement_id in self.active_collaborations.get(creator_id, []):
            agreement = self.agreements[agreement_id]
            revenues = self.revenue_records.get(agreement_id, [])
            
            for collaborator in agreement.collaborators:
                if collaborator["creator_id"] == creator_id:
                    continue
                
                collab_id = collaborator["creator_id"]
                if collab_id not in collaborator_stats:
                    collaborator_stats[collab_id] = {
                        "creator_id": collab_id,
                        "creator_type": collaborator["creator_type"],
                        "collaboration_count": 0,
                        "total_revenue": 0.0
                    }
                
                collaborator_stats[collab_id]["collaboration_count"] += 1
                
                # Add revenue
                creator_share = agreement.revenue_sharing.get(creator_id, 0.0)
                for revenue in revenues:
                    collaborator_stats[collab_id]["total_revenue"] += revenue.revenue_amount * creator_share
        
        # Sort by combined score (revenue + frequency)
        top_collaborators = list(collaborator_stats.values())
        top_collaborators.sort(
            key=lambda x: (x["total_revenue"] * 0.7 + x["collaboration_count"] * 0.3),
            reverse=True
        )
        
        return top_collaborators[:limit]
    
    async def _get_collaboration_revenue_by_platform(
        self,
        agreements: List[CollaborationAgreement],
        creator_id: str
    ) -> Dict[str, float]:
        """Get collaboration revenue breakdown by platform."""
        platform_revenue = {}
        
        for agreement in agreements:
            creator_share = agreement.revenue_sharing.get(creator_id, 0.0)
            revenues = self.revenue_records.get(agreement.agreement_id, [])
            
            for revenue in revenues:
                platform = revenue.platform
                platform_revenue[platform] = platform_revenue.get(platform, 0.0)
                platform_revenue[platform] += revenue.revenue_amount * creator_share
        
        return platform_revenue
    
    async def _generate_collaboration_recommendations(
        self,
        creator_id: str
    ) -> List[str]:
        """Generate personalized collaboration recommendations."""
        recommendations = []
        
        creator_profile = self.creator_profiles.get(creator_id)
        if not creator_profile:
            return recommendations
        
        # Check collaboration frequency
        active_count = len(self.active_collaborations.get(creator_id, []))
        if active_count == 0:
            recommendations.append("Consider starting your first collaboration to expand your network")
        elif active_count < 3:
            recommendations.append("Explore more collaboration opportunities to diversify your content")
        
        # Check network size
        network_size = len(self.collaboration_networks.get(creator_id, set()))
        if network_size < 5:
            recommendations.append("Build your collaboration network by connecting with more creators")
        
        # Check collaboration types
        used_types = set()
        for agreement_id in self.active_collaborations.get(creator_id, []):
            agreement = self.agreements[agreement_id]
            used_types.add(agreement.collaboration_type)
        
        unused_preferred = set(creator_profile.preferred_collaboration_types) - used_types
        if unused_preferred:
            recommendations.append(f"Try new collaboration types: {', '.join([t.value for t in unused_preferred])}")
        
        # Revenue optimization
        total_revenue = sum(
            sum(r.revenue_amount for r in self.revenue_records.get(aid, []))
            for aid in self.active_collaborations.get(creator_id, [])
        )
        
        if total_revenue < 1000:  # Threshold for optimization recommendation
            recommendations.append("Focus on monetized collaborations to increase revenue")
        
        return recommendations[:8]
