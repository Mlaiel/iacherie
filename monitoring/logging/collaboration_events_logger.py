"""🤝 Collaboration Events Logger - Creator-Brand Partnership Intelligence
==================================================================
Experts: Backend Senior + Business Intelligence + ML Engineer + DBA + Microservices
Technologies: Event Sourcing + Apache Kafka + CQRS + Real-time Matching + Analytics
Business Logic: Collaboration & Networking → Matching créateur-marque → Success tracking → ROI analytics
==================================================================

© 2025 Fahed Mlaiel <mlaiel@live.de>
TOUS DROITS RÉSERVÉS

🚨 PROTECTION INTELLECTUELLE:
- Code propriétaire de Fahed Mlaiel
- Utilisation commerciale INTERDITE sans autorisation écrite
- Reverse engineering STRICTEMENT INTERDIT
- Distribution INTERDITE sans licence explicite
- Violation = Poursuites judiciaires automatiques

🏢 USAGE ENTREPRISE:
- Licence entreprise disponible sur demande
- Support technique inclus avec licence
- Maintenance et mises à jour assurées
- Formation équipe technique fournie
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import threading
import uuid
import statistics

# Configure logging
logger = logging.getLogger(__name__)

# ==================== ENUMS & CONSTANTS ====================

class CollaborationType(Enum):
    """Types de collaboration Creator Economy"""
    # Brand Partnerships
    SPONSORED_CONTENT = "sponsored_content"
    BRAND_AMBASSADOR = "brand_ambassador"
    PRODUCT_PLACEMENT = "product_placement"
    AFFILIATE_PARTNERSHIP = "affiliate_partnership"
    
    # Creator Collaborations
    CREATOR_COLLABORATION = "creator_collaboration"
    CROSS_PROMOTION = "cross_promotion"
    JOINT_CONTENT = "joint_content"
    GUEST_APPEARANCE = "guest_appearance"
    
    # Platform Partnerships
    EXCLUSIVE_DEAL = "exclusive_deal"
    REVENUE_SHARE = "revenue_share"
    LICENSING_DEAL = "licensing_deal"
    DISTRIBUTION_PARTNERSHIP = "distribution_partnership"
    
    # Event-based
    CAMPAIGN_PARTICIPATION = "campaign_participation"
    CONTEST_COLLABORATION = "contest_collaboration"
    LIVE_EVENT = "live_event"
    VIRTUAL_EVENT = "virtual_event"

class CollaborationStatus(Enum):
    """Statuts de collaboration"""
    # Initial stages
    OPPORTUNITY_IDENTIFIED = "opportunity_identified"
    INTEREST_EXPRESSED = "interest_expressed"
    PROPOSAL_SENT = "proposal_sent"
    PROPOSAL_RECEIVED = "proposal_received"
    
    # Negotiation
    UNDER_NEGOTIATION = "under_negotiation"
    TERMS_AGREED = "terms_agreed"
    CONTRACT_DRAFT = "contract_draft"
    LEGAL_REVIEW = "legal_review"
    
    # Active
    SIGNED = "signed"
    IN_PROGRESS = "in_progress"
    CONTENT_CREATED = "content_created"
    CONTENT_PUBLISHED = "content_published"
    
    # Completion
    COMPLETED = "completed"
    DELIVERED = "delivered"
    PAYMENT_PROCESSED = "payment_processed"
    
    # Termination
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    DISPUTE = "dispute"

class ParticipantRole(Enum):
    """Rôles des participants"""
    CREATOR = "creator"
    BRAND = "brand"
    AGENCY = "agency"
    PLATFORM = "platform"
    INFLUENCER = "influencer"
    MANAGER = "manager"
    LEGAL_ADVISOR = "legal_advisor"

class EventType(Enum):
    """Types d'événements de collaboration"""
    # Matching & Discovery
    MATCH_SUGGESTED = "match_suggested"
    PROFILE_VIEWED = "profile_viewed"
    INTEREST_SHOWN = "interest_shown"
    CONTACT_INITIATED = "contact_initiated"
    
    # Proposal & Negotiation
    PROPOSAL_CREATED = "proposal_created"
    PROPOSAL_SENT = "proposal_sent"
    PROPOSAL_VIEWED = "proposal_viewed"
    PROPOSAL_ACCEPTED = "proposal_accepted"
    PROPOSAL_REJECTED = "proposal_rejected"
    PROPOSAL_MODIFIED = "proposal_modified"
    
    # Contract & Legal
    CONTRACT_GENERATED = "contract_generated"
    CONTRACT_SIGNED = "contract_signed"
    TERMS_MODIFIED = "terms_modified"
    LEGAL_REVIEW_STARTED = "legal_review_started"
    LEGAL_APPROVAL = "legal_approval"
    
    # Execution
    COLLABORATION_STARTED = "collaboration_started"
    MILESTONE_REACHED = "milestone_reached"
    CONTENT_SUBMITTED = "content_submitted"
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    REVISION_REQUESTED = "revision_requested"
    
    # Completion & Payment
    DELIVERABLE_COMPLETED = "deliverable_completed"
    COLLABORATION_COMPLETED = "collaboration_completed"
    PAYMENT_REQUESTED = "payment_requested"
    PAYMENT_PROCESSED = "payment_processed"
    
    # Communication
    MESSAGE_SENT = "message_sent"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_COMPLETED = "meeting_completed"
    FEEDBACK_PROVIDED = "feedback_provided"
    
    # Analytics
    PERFORMANCE_TRACKED = "performance_tracked"
    RESULTS_ANALYZED = "results_analyzed"
    ROI_CALCULATED = "roi_calculated"
    REPORT_GENERATED = "report_generated"

class SuccessMetric(Enum):
    """Métriques de succès collaboration"""
    REACH = "reach"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    REVENUE = "revenue"
    BRAND_AWARENESS = "brand_awareness"
    SENTIMENT = "sentiment"
    COMPLETION_TIME = "completion_time"
    QUALITY_SCORE = "quality_score"

# ==================== DATA MODELS ====================

@dataclass
class CollaborationParticipant:
    """Participant à une collaboration"""
    id: str
    role: ParticipantRole
    name: str
    email: Optional[str] = None
    organization: Optional[str] = None
    
    # Creator-specific
    creator_tier: Optional[str] = None
    follower_count: int = 0
    engagement_rate: float = 0.0
    content_categories: List[str] = field(default_factory=list)
    
    # Brand-specific
    industry: Optional[str] = None
    brand_category: Optional[str] = None
    marketing_budget: Optional[float] = None
    
    # Contact info
    phone: Optional[str] = None
    social_handles: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'role': self.role.value,
            'name': self.name,
            'email': self.email,
            'organization': self.organization,
            'creator_tier': self.creator_tier,
            'follower_count': self.follower_count,
            'engagement_rate': self.engagement_rate,
            'content_categories': self.content_categories,
            'industry': self.industry,
            'brand_category': self.brand_category,
            'marketing_budget': self.marketing_budget,
            'phone': self.phone,
            'social_handles': self.social_handles
        }

@dataclass
class CollaborationTerms:
    """Termes de collaboration"""
    compensation_amount: float = 0.0
    compensation_currency: str = "USD"
    compensation_type: str = "fixed"  # fixed, percentage, performance_based
    
    deliverables: List[str] = field(default_factory=list)
    timeline: Dict[str, str] = field(default_factory=dict)  # milestone -> date
    
    content_requirements: Dict[str, Any] = field(default_factory=dict)
    usage_rights: List[str] = field(default_factory=list)
    exclusivity_terms: List[str] = field(default_factory=list)
    
    performance_metrics: List[SuccessMetric] = field(default_factory=list)
    success_criteria: Dict[str, Any] = field(default_factory=dict)
    
    additional_terms: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationEvent:
    """Événement de collaboration complet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Event identification
    event_type: EventType = EventType.MATCH_SUGGESTED
    collaboration_id: str = ""
    
    # Participants
    participants: List[CollaborationParticipant] = field(default_factory=list)
    initiator_id: Optional[str] = None
    target_id: Optional[str] = None
    
    # Collaboration details
    collaboration_type: Optional[CollaborationType] = None
    collaboration_status: Optional[CollaborationStatus] = None
    terms: Optional[CollaborationTerms] = None
    
    # Event context
    description: str = ""
    event_data: Dict[str, Any] = field(default_factory=dict)
    previous_event_id: Optional[str] = None
    
    # Performance metrics
    success_metrics: Dict[SuccessMetric, float] = field(default_factory=dict)
    roi_calculation: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Communication
    message_content: Optional[str] = None
    attachments: List[str] = field(default_factory=list)
    communication_channel: Optional[str] = None
    
    # Platform context
    platform_location: str = "ainflue"
    integration_source: Optional[str] = None
    automation_triggered: bool = False
    
    # Business context
    campaign_id: Optional[str] = None
    budget_allocated: Optional[float] = None
    expected_deliverables: List[str] = field(default_factory=list)
    
    # Timeline
    deadline: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    
    # Analytics
    conversion_value: float = 0.0
    engagement_metrics: Dict[str, float] = field(default_factory=dict)
    reach_metrics: Dict[str, int] = field(default_factory=dict)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def add_participant(self, participant: CollaborationParticipant):
        """Ajoute un participant"""
        if participant not in self.participants:
            self.participants.append(participant)
    
    def get_creators(self) -> List[CollaborationParticipant]:
        """Récupère les créateurs participants"""
        return [p for p in self.participants if p.role == ParticipantRole.CREATOR]
    
    def get_brands(self) -> List[CollaborationParticipant]:
        """Récupère les marques participantes"""
        return [p for p in self.participants if p.role == ParticipantRole.BRAND]
    
    def calculate_collaboration_score(self) -> float:
        """Calcule un score de qualité de collaboration"""
        score = 0.0
        
        # Score basé sur les métriques de succès
        if self.success_metrics:
            metric_scores = []
            for metric, value in self.success_metrics.items():
                if metric == SuccessMetric.ENGAGEMENT and value > 5.0:
                    metric_scores.append(8.0)
                elif metric == SuccessMetric.REACH and value > 10000:
                    metric_scores.append(7.0)
                elif metric == SuccessMetric.CONVERSION and value > 2.0:
                    metric_scores.append(9.0)
                elif metric == SuccessMetric.REVENUE and value > 1000:
                    metric_scores.append(8.5)
                else:
                    metric_scores.append(5.0)
            
            if metric_scores:
                score = statistics.mean(metric_scores)
        
        # Ajustements basés sur le contexte
        if self.collaboration_status == CollaborationStatus.COMPLETED:
            score += 1.0
        if self.roi_calculation and self.roi_calculation > 1.0:
            score += 1.5
        if self.quality_score:
            score = (score + self.quality_score) / 2
        
        return min(score, 10.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Conversion en dictionnaire pour stockage"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type.value,
            'collaboration_id': self.collaboration_id,
            'participants': [p.to_dict() for p in self.participants],
            'initiator_id': self.initiator_id,
            'target_id': self.target_id,
            'collaboration_type': self.collaboration_type.value if self.collaboration_type else None,
            'collaboration_status': self.collaboration_status.value if self.collaboration_status else None,
            'terms': {
                'compensation_amount': self.terms.compensation_amount,
                'compensation_currency': self.terms.compensation_currency,
                'compensation_type': self.terms.compensation_type,
                'deliverables': self.terms.deliverables,
                'timeline': self.terms.timeline,
                'content_requirements': self.terms.content_requirements,
                'usage_rights': self.terms.usage_rights,
                'exclusivity_terms': self.terms.exclusivity_terms,
                'performance_metrics': [m.value for m in self.terms.performance_metrics],
                'success_criteria': self.terms.success_criteria,
                'additional_terms': self.terms.additional_terms
            } if self.terms else None,
            'description': self.description,
            'event_data': self.event_data,
            'previous_event_id': self.previous_event_id,
            'success_metrics': {k.value: v for k, v in self.success_metrics.items()},
            'roi_calculation': self.roi_calculation,
            'quality_score': self.quality_score,
            'message_content': self.message_content,
            'attachments': self.attachments,
            'communication_channel': self.communication_channel,
            'platform_location': self.platform_location,
            'integration_source': self.integration_source,
            'automation_triggered': self.automation_triggered,
            'campaign_id': self.campaign_id,
            'budget_allocated': self.budget_allocated,
            'expected_deliverables': self.expected_deliverables,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None,
            'actual_completion': self.actual_completion.isoformat() if self.actual_completion else None,
            'conversion_value': self.conversion_value,
            'engagement_metrics': self.engagement_metrics,
            'reach_metrics': self.reach_metrics,
            'tags': self.tags,
            'notes': self.notes
        }

@dataclass
class CollaborationPipeline:
    """Pipeline de collaboration complète"""
    collaboration_id: str
    created_at: datetime
    events: List[CollaborationEvent] = field(default_factory=list)
    
    # Status tracking
    current_status: CollaborationStatus = CollaborationStatus.OPPORTUNITY_IDENTIFIED
    completion_percentage: float = 0.0
    
    # Participants tracking
    all_participants: List[CollaborationParticipant] = field(default_factory=list)
    active_participants: List[str] = field(default_factory=list)
    
    # Performance tracking
    total_budget: float = 0.0
    spent_budget: float = 0.0
    projected_roi: float = 0.0
    actual_roi: float = 0.0
    
    # Timeline tracking
    milestones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    delays: List[Dict[str, Any]] = field(default_factory=list)
    
    def add_event(self, event: CollaborationEvent):
        """Ajoute un événement au pipeline"""
        self.events.append(event)
        
        # Update status
        if event.collaboration_status:
            self.current_status = event.collaboration_status
        
        # Update participants
        for participant in event.participants:
            if participant not in self.all_participants:
                self.all_participants.append(participant)
                self.active_participants.append(participant.id)
        
        # Update budget tracking
        if event.budget_allocated:
            self.total_budget += event.budget_allocated
        
        if event.terms and event.terms.compensation_amount:
            self.spent_budget += event.terms.compensation_amount
        
        # Calculate completion percentage
        self._calculate_completion_percentage()
    
    def _calculate_completion_percentage(self):
        """Calcule le pourcentage de completion"""
        status_weights = {
            CollaborationStatus.OPPORTUNITY_IDENTIFIED: 5,
            CollaborationStatus.INTEREST_EXPRESSED: 10,
            CollaborationStatus.PROPOSAL_SENT: 20,
            CollaborationStatus.UNDER_NEGOTIATION: 35,
            CollaborationStatus.TERMS_AGREED: 50,
            CollaborationStatus.SIGNED: 60,
            CollaborationStatus.IN_PROGRESS: 75,
            CollaborationStatus.CONTENT_CREATED: 85,
            CollaborationStatus.CONTENT_PUBLISHED: 95,
            CollaborationStatus.COMPLETED: 100,
            CollaborationStatus.PAYMENT_PROCESSED: 100
        }
        
        self.completion_percentage = status_weights.get(self.current_status, 0)

# ==================== ANALYTICS ENGINE ====================

class CollaborationAnalyticsEngine:
    """Moteur d'analytics pour collaborations Creator Economy"""
    
    def __init__(self):
        self.collaboration_pipelines: Dict[str, CollaborationPipeline] = {}
        self.participant_analytics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.matching_intelligence: Dict[str, List[str]] = defaultdict(list)
        self.success_patterns: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.lock = threading.RLock()
        
        # Real-time metrics
        self.realtime_metrics = {
            'active_collaborations': 0,
            'successful_matches_today': 0,
            'total_collaboration_value': 0.0,
            'average_completion_time': 0.0,
            'success_rate': 0.0,
            'top_performing_creators': [],
            'top_spending_brands': []
        }
        
        # Industry benchmarks
        self.benchmarks = {
            'average_engagement_rate': 3.5,
            'average_conversion_rate': 2.1,
            'average_roi': 4.2,
            'typical_completion_time': 30  # days
        }
    
    def analyze_collaboration_event(self, event: CollaborationEvent):
        """Analyse un événement de collaboration"""
        with self.lock:
            collaboration_id = event.collaboration_id
            
            # Initialize or update pipeline
            if collaboration_id not in self.collaboration_pipelines:
                self.collaboration_pipelines[collaboration_id] = CollaborationPipeline(
                    collaboration_id=collaboration_id,
                    created_at=event.timestamp
                )
            
            pipeline = self.collaboration_pipelines[collaboration_id]
            pipeline.add_event(event)
            
            # Analyze participants
            self._analyze_participants(event)
            
            # Update matching intelligence
            self._update_matching_intelligence(event)
            
            # Track success patterns
            self._track_success_patterns(event)
            
            # Update real-time metrics
            self._update_realtime_metrics()
            
            # Generate insights
            self._generate_collaboration_insights(pipeline)
    
    def _analyze_participants(self, event: CollaborationEvent):
        """Analyse les participants"""
        for participant in event.participants:
            participant_id = participant.id
            
            if participant_id not in self.participant_analytics:
                self.participant_analytics[participant_id] = {
                    'total_collaborations': 0,
                    'successful_collaborations': 0,
                    'total_earnings': 0.0,
                    'average_project_value': 0.0,
                    'preferred_collaboration_types': defaultdict(int),
                    'success_rate': 0.0,
                    'average_completion_time': 0.0,
                    'partner_ratings': [],
                    'collaboration_history': []
                }
            
            analytics = self.participant_analytics[participant_id]
            analytics['total_collaborations'] += 1
            analytics['collaboration_history'].append(event.collaboration_id)
            
            # Track collaboration types
            if event.collaboration_type:
                analytics['preferred_collaboration_types'][event.collaboration_type.value] += 1
            
            # Track earnings for creators
            if (participant.role == ParticipantRole.CREATOR and 
                event.terms and event.terms.compensation_amount):
                analytics['total_earnings'] += event.terms.compensation_amount
                analytics['average_project_value'] = (
                    analytics['total_earnings'] / analytics['total_collaborations']
                )
            
            # Track success
            if event.collaboration_status == CollaborationStatus.COMPLETED:
                analytics['successful_collaborations'] += 1
                analytics['success_rate'] = (
                    analytics['successful_collaborations'] / analytics['total_collaborations']
                )
    
    def _update_matching_intelligence(self, event: CollaborationEvent):
        """Met à jour l'intelligence de matching"""
        if event.event_type in [EventType.MATCH_SUGGESTED, EventType.INTEREST_SHOWN]:
            creators = event.get_creators()
            brands = event.get_brands()
            
            for creator in creators:
                for brand in brands:
                    # Track successful matches for future recommendations
                    match_key = f"{creator.id}_{brand.id}"
                    
                    if event.collaboration_status in [
                        CollaborationStatus.SIGNED,
                        CollaborationStatus.COMPLETED
                    ]:
                        self.matching_intelligence[creator.id].append(brand.id)
                        self.matching_intelligence[brand.id].append(creator.id)
    
    def _track_success_patterns(self, event: CollaborationEvent):
        """Tracking des patterns de succès"""
        if event.collaboration_status == CollaborationStatus.COMPLETED:
            success_pattern = {
                'collaboration_type': event.collaboration_type.value if event.collaboration_type else None,
                'participant_count': len(event.participants),
                'completion_time': None,
                'success_metrics': event.success_metrics,
                'roi': event.roi_calculation,
                'creator_tiers': [p.creator_tier for p in event.get_creators()],
                'brand_industries': [p.industry for p in event.get_brands()]
            }
            
            # Calculate completion time
            pipeline = self.collaboration_pipelines.get(event.collaboration_id)
            if pipeline and pipeline.events:
                start_event = pipeline.events[0]
                completion_time = (event.timestamp - start_event.timestamp).days
                success_pattern['completion_time'] = completion_time
            
            pattern_key = f"{event.collaboration_type.value if event.collaboration_type else 'unknown'}"
            self.success_patterns[pattern_key].append(success_pattern)
    
    def _update_realtime_metrics(self):
        """Met à jour les métriques temps réel"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        
        # Active collaborations
        active_count = 0
        total_value = 0.0
        completion_times = []
        successful_today = 0
        
        for pipeline in self.collaboration_pipelines.values():
            # Active collaborations
            if pipeline.current_status in [
                CollaborationStatus.SIGNED,
                CollaborationStatus.IN_PROGRESS,
                CollaborationStatus.CONTENT_CREATED
            ]:
                active_count += 1
            
            # Total value
            total_value += pipeline.total_budget
            
            # Completion times
            if pipeline.current_status == CollaborationStatus.COMPLETED:
                for event in pipeline.events:
                    if event.actual_completion:
                        completion_time = (event.actual_completion - pipeline.created_at).days
                        completion_times.append(completion_time)
                        
                        # Count successful matches today
                        if event.actual_completion.strftime('%Y-%m-%d') == today:
                            successful_today += 1
        
        self.realtime_metrics['active_collaborations'] = active_count
        self.realtime_metrics['total_collaboration_value'] = total_value
        self.realtime_metrics['successful_matches_today'] = successful_today
        
        if completion_times:
            self.realtime_metrics['average_completion_time'] = statistics.mean(completion_times)
        
        # Success rate
        total_collaborations = len(self.collaboration_pipelines)
        completed_collaborations = len([
            p for p in self.collaboration_pipelines.values()
            if p.current_status == CollaborationStatus.COMPLETED
        ])
        
        if total_collaborations > 0:
            self.realtime_metrics['success_rate'] = completed_collaborations / total_collaborations * 100
        
        # Top performers
        self._calculate_top_performers()
    
    def _calculate_top_performers(self):
        """Calcule les top performers"""
        # Top creators by earnings
        creator_earnings = []
        brand_spending = []
        
        for participant_id, analytics in self.participant_analytics.items():
            # Find participant details
            participant_role = None
            for pipeline in self.collaboration_pipelines.values():
                for event in pipeline.events:
                    for participant in event.participants:
                        if participant.id == participant_id:
                            participant_role = participant.role
                            break
            
            if participant_role == ParticipantRole.CREATOR:
                creator_earnings.append({
                    'id': participant_id,
                    'earnings': analytics['total_earnings']
                })
            elif participant_role == ParticipantRole.BRAND:
                # Calculate brand spending
                total_spending = sum(
                    event.terms.compensation_amount for pipeline in self.collaboration_pipelines.values()
                    for event in pipeline.events
                    if event.terms and event.terms.compensation_amount and
                    any(p.id == participant_id for p in event.participants)
                )
                brand_spending.append({
                    'id': participant_id,
                    'spending': total_spending
                })
        
        self.realtime_metrics['top_performing_creators'] = sorted(
            creator_earnings, key=lambda x: x['earnings'], reverse=True
        )[:5]
        
        self.realtime_metrics['top_spending_brands'] = sorted(
            brand_spending, key=lambda x: x['spending'], reverse=True
        )[:5]
    
    def _generate_collaboration_insights(self, pipeline: CollaborationPipeline):
        """Génère des insights pour une collaboration"""
        # Predict success probability based on patterns
        if len(pipeline.events) > 0:
            last_event = pipeline.events[-1]
            
            # Compare with successful patterns
            similar_patterns = []
            if last_event.collaboration_type:
                pattern_key = last_event.collaboration_type.value
                similar_patterns = self.success_patterns.get(pattern_key, [])
            
            if similar_patterns:
                # Calculate success probability
                successful_similar = len([p for p in similar_patterns if p.get('roi', 0) > 1.0])
                success_probability = successful_similar / len(similar_patterns) if similar_patterns else 0
                
                # Add insight to pipeline
                pipeline.projected_roi = statistics.mean([
                    p.get('roi', 0) for p in similar_patterns if p.get('roi', 0) > 0
                ]) if similar_patterns else 0
    
    def get_collaboration_analytics(self, collaboration_id: str) -> Dict[str, Any]:
        """Analytics pour une collaboration spécifique"""
        if collaboration_id not in self.collaboration_pipelines:
            return {'collaboration_id': collaboration_id, 'status': 'not_found'}
        
        pipeline = self.collaboration_pipelines[collaboration_id]
        
        # Calculate timeline analytics
        timeline_events = []
        for event in pipeline.events:
            timeline_events.append({
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type.value,
                'status': event.collaboration_status.value if event.collaboration_status else None
            })
        
        # Performance metrics
        performance_summary = {}
        if pipeline.events:
            latest_event = pipeline.events[-1]
            if latest_event.success_metrics:
                performance_summary = {
                    metric.value: value for metric, value in latest_event.success_metrics.items()
                }
        
        return {
            'collaboration_id': collaboration_id,
            'created_at': pipeline.created_at.isoformat(),
            'current_status': pipeline.current_status.value,
            'completion_percentage': pipeline.completion_percentage,
            'participants': [p.to_dict() for p in pipeline.all_participants],
            'budget_tracking': {
                'total_budget': pipeline.total_budget,
                'spent_budget': pipeline.spent_budget,
                'remaining_budget': pipeline.total_budget - pipeline.spent_budget
            },
            'roi_analysis': {
                'projected_roi': pipeline.projected_roi,
                'actual_roi': pipeline.actual_roi
            },
            'timeline': timeline_events,
            'performance_metrics': performance_summary,
            'event_count': len(pipeline.events),
            'milestones': pipeline.milestones,
            'delays': pipeline.delays
        }
    
    def get_participant_analytics(self, participant_id: str) -> Dict[str, Any]:
        """Analytics pour un participant spécifique"""
        if participant_id not in self.participant_analytics:
            return {'participant_id': participant_id, 'status': 'not_found'}
        
        analytics = self.participant_analytics[participant_id]
        
        # Calculate additional metrics
        recent_collaborations = analytics['collaboration_history'][-5:]  # Last 5
        
        return {
            'participant_id': participant_id,
            'collaboration_summary': {
                'total_collaborations': analytics['total_collaborations'],
                'successful_collaborations': analytics['successful_collaborations'],
                'success_rate': analytics['success_rate'],
                'average_completion_time': analytics['average_completion_time']
            },
            'financial_summary': {
                'total_earnings': analytics['total_earnings'],
                'average_project_value': analytics['average_project_value']
            },
            'preferences': {
                'preferred_collaboration_types': dict(analytics['preferred_collaboration_types'])
            },
            'recent_collaborations': recent_collaborations,
            'partner_ratings': analytics['partner_ratings']
        }
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        total_collaborations = len(self.collaboration_pipelines)
        total_participants = len(self.participant_analytics)
        
        # Industry performance comparison
        industry_comparison = {}
        for metric, benchmark in self.benchmarks.items():
            if metric == 'average_engagement_rate':
                # Calculate platform average
                engagement_rates = []
                for pipeline in self.collaboration_pipelines.values():
                    for event in pipeline.events:
                        if 'engagement_rate' in event.engagement_metrics:
                            engagement_rates.append(event.engagement_metrics['engagement_rate'])
                
                platform_avg = statistics.mean(engagement_rates) if engagement_rates else 0
                industry_comparison[metric] = {
                    'platform_average': platform_avg,
                    'industry_benchmark': benchmark,
                    'performance': 'above' if platform_avg > benchmark else 'below'
                }
        
        return {
            'platform_overview': {
                'total_collaborations': total_collaborations,
                'total_participants': total_participants,
                'active_collaborations': self.realtime_metrics['active_collaborations'],
                'total_collaboration_value': self.realtime_metrics['total_collaboration_value']
            },
            'realtime_metrics': self.realtime_metrics,
            'success_patterns': {
                pattern_type: len(patterns) for pattern_type, patterns in self.success_patterns.items()
            },
            'industry_comparison': industry_comparison,
            'matching_intelligence_size': len(self.matching_intelligence)
        }
    
    def get_matching_recommendations(self, participant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommandations de matching pour un participant"""
        if participant_id not in self.matching_intelligence:
            return []
        
        # Get historical successful matches
        successful_partners = self.matching_intelligence[participant_id]
        
        # Score potential matches
        recommendations = []
        for partner_id in successful_partners[:limit]:
            partner_analytics = self.participant_analytics.get(partner_id, {})
            
            score = 0.0
            if partner_analytics:
                # Score based on success rate
                score += partner_analytics.get('success_rate', 0) * 40
                
                # Score based on collaboration count (experience)
                score += min(partner_analytics.get('total_collaborations', 0) * 2, 30)
                
                # Score based on earnings/spending (activity level)
                score += min(partner_analytics.get('total_earnings', 0) / 1000, 30)
            
            recommendations.append({
                'partner_id': partner_id,
                'match_score': min(score, 100),
                'success_rate': partner_analytics.get('success_rate', 0),
                'collaboration_count': partner_analytics.get('total_collaborations', 0)
            })
        
        return sorted(recommendations, key=lambda x: x['match_score'], reverse=True)

# ==================== MAIN LOGGER CLASS ====================

class CollaborationEventsLogger:
    """Logger principal pour événements de collaboration Creator Economy"""
    
    def __init__(self, buffer_size: int = 5000, auto_flush_interval: int = 60):
        self.buffer_size = buffer_size
        self.auto_flush_interval = auto_flush_interval
        
        # Storage
        self.event_buffer = deque(maxlen=buffer_size)
        self.analytics_engine = CollaborationAnalyticsEngine()
        
        # Threading
        self.lock = threading.RLock()
        self.is_running = False
        self.flush_thread = None
        
        # Statistics
        self.total_logged = 0
        self.dropped_events = 0
        
        logger.info("🤝 Collaboration Events Logger initialized")
    
    def start(self):
        """Démarre le logger"""
        if self.is_running:
            return
            
        self.is_running = True
        self.flush_thread = threading.Thread(
            target=self._auto_flush_loop,
            daemon=True,
            name="CollaborationLogger-AutoFlush"
        )
        self.flush_thread.start()
        
        logger.info("🚀 Collaboration Events Logger started")
    
    def stop(self):
        """Arrête le logger"""
        if not self.is_running:
            return
            
        self.is_running = False
        if self.flush_thread:
            self.flush_thread.join(timeout=5.0)
            
        # Flush final
        self._flush_buffer()
        
        logger.info("🛑 Collaboration Events Logger stopped")
    
    def _auto_flush_loop(self):
        """Boucle de flush automatique"""
        while self.is_running:
            time.sleep(self.auto_flush_interval)
            if self.is_running:
                self._flush_buffer()
    
    def _flush_buffer(self):
        """Vide le buffer et traite les événements"""
        with self.lock:
            events_to_process = list(self.event_buffer)
            self.event_buffer.clear()
        
        for event in events_to_process:
            try:
                self.analytics_engine.analyze_collaboration_event(event)
                logger.debug(f"Processed collaboration event: {event.event_type.value}")
            except Exception as e:
                logger.error(f"Error processing collaboration event {event.id}: {e}")
    
    def log_collaboration_event(self, 
                               event_type: EventType,
                               collaboration_id: str,
                               participants: List[CollaborationParticipant] = None,
                               **kwargs) -> str:
        """Log un événement de collaboration"""
        
        event = CollaborationEvent(
            event_type=event_type,
            collaboration_id=collaboration_id,
            participants=participants or [],
            **kwargs
        )
        
        with self.lock:
            if len(self.event_buffer) >= self.buffer_size:
                self.dropped_events += 1
                logger.warning(f"Collaboration event buffer full, dropping event {event.id}")
                return ""
            
            self.event_buffer.append(event)
            self.total_logged += 1
        
        logger.info(f"Logged collaboration event: {event_type.value} for {collaboration_id}")
        return event.id
    
    # ==================== SPECIALIZED LOG METHODS ====================
    
    def log_match_suggestion(self, creator_id: str, brand_id: str, 
                           collaboration_type: CollaborationType, **kwargs) -> str:
        """Log suggestion de match"""
        collaboration_id = f"collab_{uuid.uuid4().hex[:8]}"
        
        creator = CollaborationParticipant(
            id=creator_id,
            role=ParticipantRole.CREATOR,
            name=f"Creator {creator_id}"
        )
        
        brand = CollaborationParticipant(
            id=brand_id,
            role=ParticipantRole.BRAND,
            name=f"Brand {brand_id}"
        )
        
        return self.log_collaboration_event(
            event_type=EventType.MATCH_SUGGESTED,
            collaboration_id=collaboration_id,
            participants=[creator, brand],
            collaboration_type=collaboration_type,
            collaboration_status=CollaborationStatus.OPPORTUNITY_IDENTIFIED,
            description=f"Match suggested between {creator_id} and {brand_id}",
            **kwargs
        )
    
    def log_proposal_sent(self, collaboration_id: str, sender_id: str, 
                         receiver_id: str, terms: CollaborationTerms, **kwargs) -> str:
        """Log envoi de proposition"""
        return self.log_collaboration_event(
            event_type=EventType.PROPOSAL_SENT,
            collaboration_id=collaboration_id,
            initiator_id=sender_id,
            target_id=receiver_id,
            terms=terms,
            collaboration_status=CollaborationStatus.PROPOSAL_SENT,
            description=f"Proposal sent from {sender_id} to {receiver_id}",
            **kwargs
        )
    
    def log_contract_signed(self, collaboration_id: str, participants: List[CollaborationParticipant],
                           terms: CollaborationTerms, **kwargs) -> str:
        """Log signature de contrat"""
        return self.log_collaboration_event(
            event_type=EventType.CONTRACT_SIGNED,
            collaboration_id=collaboration_id,
            participants=participants,
            terms=terms,
            collaboration_status=CollaborationStatus.SIGNED,
            description=f"Contract signed for collaboration {collaboration_id}",
            **kwargs
        )
    
    def log_content_submission(self, collaboration_id: str, creator_id: str,
                             content_details: Dict[str, Any], **kwargs) -> str:
        """Log soumission de contenu"""
        return self.log_collaboration_event(
            event_type=EventType.CONTENT_SUBMITTED,
            collaboration_id=collaboration_id,
            initiator_id=creator_id,
            collaboration_status=CollaborationStatus.CONTENT_CREATED,
            event_data=content_details,
            description=f"Content submitted by {creator_id}",
            **kwargs
        )
    
    def log_collaboration_completion(self, collaboration_id: str, 
                                   success_metrics: Dict[SuccessMetric, float],
                                   roi_calculation: float, **kwargs) -> str:
        """Log completion de collaboration"""
        return self.log_collaboration_event(
            event_type=EventType.COLLABORATION_COMPLETED,
            collaboration_id=collaboration_id,
            collaboration_status=CollaborationStatus.COMPLETED,
            success_metrics=success_metrics,
            roi_calculation=roi_calculation,
            actual_completion=datetime.utcnow(),
            description=f"Collaboration {collaboration_id} completed successfully",
            **kwargs
        )
    
    def log_payment_processed(self, collaboration_id: str, amount: float,
                            currency: str = "USD", recipient_id: str = "", **kwargs) -> str:
        """Log traitement de paiement"""
        return self.log_collaboration_event(
            event_type=EventType.PAYMENT_PROCESSED,
            collaboration_id=collaboration_id,
            collaboration_status=CollaborationStatus.PAYMENT_PROCESSED,
            target_id=recipient_id,
            conversion_value=amount,
            event_data={"amount": amount, "currency": currency},
            description=f"Payment of {amount} {currency} processed for {collaboration_id}",
            **kwargs
        )
    
    def log_communication_event(self, collaboration_id: str, sender_id: str,
                               message_content: str, channel: str = "platform", **kwargs) -> str:
        """Log événement de communication"""
        return self.log_collaboration_event(
            event_type=EventType.MESSAGE_SENT,
            collaboration_id=collaboration_id,
            initiator_id=sender_id,
            message_content=message_content,
            communication_channel=channel,
            description=f"Message sent in collaboration {collaboration_id}",
            **kwargs
        )
    
    # ==================== ANALYTICS METHODS ====================
    
    def get_collaboration_analytics(self, collaboration_id: str) -> Dict[str, Any]:
        """Analytics pour une collaboration spécifique"""
        return self.analytics_engine.get_collaboration_analytics(collaboration_id)
    
    def get_participant_analytics(self, participant_id: str) -> Dict[str, Any]:
        """Analytics pour un participant spécifique"""
        return self.analytics_engine.get_participant_analytics(participant_id)
    
    def get_platform_analytics(self) -> Dict[str, Any]:
        """Analytics globales de la plateforme"""
        return self.analytics_engine.get_platform_analytics()
    
    def get_matching_recommendations(self, participant_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommandations de matching"""
        return self.analytics_engine.get_matching_recommendations(participant_id, limit)
    
    def get_success_insights(self) -> Dict[str, Any]:
        """Insights sur les patterns de succès"""
        return {
            'success_patterns': dict(self.analytics_engine.success_patterns),
            'benchmarks': self.analytics_engine.benchmarks,
            'realtime_metrics': self.analytics_engine.realtime_metrics
        }
    
    def get_logger_stats(self) -> Dict[str, Any]:
        """Statistiques du logger"""
        with self.lock:
            buffer_size = len(self.event_buffer)
            
        return {
            'total_logged': self.total_logged,
            'dropped_events': self.dropped_events,
            'current_buffer_size': buffer_size,
            'max_buffer_size': self.buffer_size,
            'buffer_utilization': buffer_size / self.buffer_size,
            'is_running': self.is_running,
            'active_collaborations': len(self.analytics_engine.collaboration_pipelines),
            'tracked_participants': len(self.analytics_engine.participant_analytics)
        }

# ==================== HELPER FUNCTIONS ====================

# Instance globale
_collaboration_logger_instance: Optional[CollaborationEventsLogger] = None

def get_collaboration_logger() -> CollaborationEventsLogger:
    """Récupère l'instance singleton du logger"""
    global _collaboration_logger_instance
    
    if _collaboration_logger_instance is None:
        _collaboration_logger_instance = CollaborationEventsLogger()
        _collaboration_logger_instance.start()
        
    return _collaboration_logger_instance

def log_creator_brand_match(creator_id: str, brand_id: str, collaboration_type: str = "sponsored_content", **kwargs):
    """Helper: Log match créateur-marque"""
    logger_instance = get_collaboration_logger()
    collab_type = CollaborationType(collaboration_type) if collaboration_type in [c.value for c in CollaborationType] else CollaborationType.SPONSORED_CONTENT
    return logger_instance.log_match_suggestion(creator_id, brand_id, collab_type, **kwargs)

def log_collaboration_proposal(collaboration_id: str, sender_id: str, receiver_id: str, amount: float, **kwargs):
    """Helper: Log proposition de collaboration"""
    logger_instance = get_collaboration_logger()
    terms = CollaborationTerms(compensation_amount=amount)
    return logger_instance.log_proposal_sent(collaboration_id, sender_id, receiver_id, terms, **kwargs)

def log_collaboration_success(collaboration_id: str, roi: float, metrics: Dict[str, float] = None, **kwargs):
    """Helper: Log succès de collaboration"""
    logger_instance = get_collaboration_logger()
    success_metrics = {}
    if metrics:
        for key, value in metrics.items():
            if key in [m.value for m in SuccessMetric]:
                success_metrics[SuccessMetric(key)] = value
    return logger_instance.log_collaboration_completion(collaboration_id, success_metrics, roi, **kwargs)

# ==================== DEMO ====================

if __name__ == "__main__":
    # Configuration et démonstration
    collab_logger = CollaborationEventsLogger(buffer_size=1000, auto_flush_interval=10)
    collab_logger.start()
    
    try:
        # Simulation d'événements de collaboration
        creators = ["creator_1", "creator_2", "creator_3"]
        brands = ["brand_1", "brand_2", "brand_3"]
        
        for i, (creator_id, brand_id) in enumerate(zip(creators, brands)):
            # Match suggestion
            collab_logger.log_match_suggestion(
                creator_id=creator_id,
                brand_id=brand_id,
                collaboration_type=CollaborationType.SPONSORED_CONTENT
            )
            
            # Proposal
            terms = CollaborationTerms(
                compensation_amount=1000.0 + i*500,
                compensation_currency="USD",
                deliverables=[f"Video content", f"Social media posts"],
                performance_metrics=[SuccessMetric.REACH, SuccessMetric.ENGAGEMENT]
            )
            
            collaboration_id = f"collab_{i+1}"
            collab_logger.log_proposal_sent(
                collaboration_id=collaboration_id,
                sender_id=brand_id,
                receiver_id=creator_id,
                terms=terms
            )
            
            # Contract signing
            creator_participant = CollaborationParticipant(
                id=creator_id,
                role=ParticipantRole.CREATOR,
                name=f"Creator {i+1}",
                follower_count=10000 + i*5000,
                engagement_rate=3.5 + i*0.5
            )
            
            brand_participant = CollaborationParticipant(
                id=brand_id,
                role=ParticipantRole.BRAND,
                name=f"Brand {i+1}",
                industry="Technology",
                marketing_budget=50000.0
            )
            
            collab_logger.log_contract_signed(
                collaboration_id=collaboration_id,
                participants=[creator_participant, brand_participant],
                terms=terms
            )
            
            # Content submission
            collab_logger.log_content_submission(
                collaboration_id=collaboration_id,
                creator_id=creator_id,
                content_details={
                    "content_type": "video",
                    "duration": 60,
                    "platforms": ["youtube", "instagram"]
                }
            )
            
            # Completion
            success_metrics = {
                SuccessMetric.REACH: 50000.0 + i*20000,
                SuccessMetric.ENGAGEMENT: 4.0 + i*0.5,
                SuccessMetric.CONVERSION: 2.5 + i*0.3
            }
            
            collab_logger.log_collaboration_completion(
                collaboration_id=collaboration_id,
                success_metrics=success_metrics,
                roi_calculation=3.5 + i*0.5
            )
            
            # Payment
            collab_logger.log_payment_processed(
                collaboration_id=collaboration_id,
                amount=terms.compensation_amount,
                recipient_id=creator_id
            )
        
        # Attendre le traitement
        time.sleep(2)
        
        # Afficher les résultats
        print("🤝 Collaboration Events Logger Demo Results:")
        print("\n🔧 Logger Stats:")
        print(json.dumps(collab_logger.get_logger_stats(), indent=2))
        
        print("\n🎯 Platform Analytics:")
        platform_analytics = collab_logger.get_platform_analytics()
        print(json.dumps(platform_analytics, indent=2, default=str))
        
        print("\n👤 Creator Analytics (creator_1):")
        creator_analytics = collab_logger.get_participant_analytics("creator_1")
        print(json.dumps(creator_analytics, indent=2, default=str))
        
        print("\n📊 Collaboration Analytics (collab_1):")
        collaboration_analytics = collab_logger.get_collaboration_analytics("collab_1")
        print(json.dumps(collaboration_analytics, indent=2, default=str))
        
        print("\n🎯 Matching Recommendations (creator_1):")
        recommendations = collab_logger.get_matching_recommendations("creator_1")
        print(json.dumps(recommendations, indent=2, default=str))
        
    finally:
        collab_logger.stop()