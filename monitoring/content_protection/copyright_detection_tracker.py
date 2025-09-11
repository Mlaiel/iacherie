"""
Ainflue Platform - Copyright Detection Tracker
==============================================

Real-time copyright detection and tracking system using AI fingerprinting,
pattern recognition, and automated copyright infringement analysis for
comprehensive content protection.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
import json
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class CopyrightStatus(Enum):
    """Copyright detection status levels."""
    CLEAR = "clear"                    # No copyright issues detected
    POTENTIAL_MATCH = "potential_match" # Possible copyright match
    COPYRIGHT_MATCH = "copyright_match" # Confirmed copyright match
    DISPUTED = "disputed"               # Copyright claim disputed
    LICENSED = "licensed"               # Content properly licensed
    FAIR_USE = "fair_use"              # Fair use determination
    DMCA_CLAIMED = "dmca_claimed"      # DMCA takedown claim received

class DetectionConfidence(Enum):
    """Detection confidence levels."""
    VERY_HIGH = "very_high"    # 95%+ confidence
    HIGH = "high"             # 85-94% confidence
    MEDIUM = "medium"         # 70-84% confidence
    LOW = "low"              # 50-69% confidence
    VERY_LOW = "very_low"    # <50% confidence

class ContentCategory(Enum):
    """Categories of copyrighted content."""
    MUSIC = "music"
    SOUND_EFFECTS = "sound_effects"
    VOICE_RECORDING = "voice_recording"
    AUDIOBOOK = "audiobook"
    PODCAST = "podcast"
    COMMERCIAL = "commercial"
    FILM_AUDIO = "film_audio"
    GAME_AUDIO = "game_audio"
    NEWS = "news"
    EDUCATIONAL = "educational"

@dataclass
class CopyrightOwner:
    """Copyright owner information."""
    owner_id: str
    name: str
    contact_email: str
    rights_organization: Optional[str]
    territories: List[str]
    registration_numbers: List[str]
    verified: bool = False

@dataclass
class CopyrightClaim:
    """Copyright infringement claim."""
    claim_id: str
    content_id: str
    claimant_id: str
    original_content_id: str
    similarity_score: float
    detection_confidence: DetectionConfidence
    copyright_status: CopyrightStatus
    content_category: ContentCategory
    match_duration_seconds: float
    match_start_time: float
    detection_algorithm: str
    evidence_data: Dict[str, Any]
    claim_details: str
    automatic_detection: bool
    manual_review_required: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class CopyrightDatabase:
    """Copyright reference database entry."""
    reference_id: str
    content_fingerprint: str
    owner: CopyrightOwner
    title: str
    artist: str
    album: Optional[str]
    release_date: Optional[datetime]
    isrc: Optional[str]
    content_category: ContentCategory
    duration_seconds: float
    territories_protected: List[str]
    licenses_available: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

class CopyrightDetectionTracker:
    """
    Enterprise copyright detection tracking system.
    
    Features:
    - Real-time copyright infringement detection
    - AI-powered similarity analysis and pattern recognition
    - Comprehensive copyright database management
    - Automated claim generation and validation
    - Territory-specific copyright enforcement
    - Integration with legal and licensing systems
    - Performance analytics and compliance reporting
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.copyright_database: Dict[str, CopyrightDatabase] = {}
        self.copyright_claims: deque = deque(maxlen=100000)
        self.copyright_owners: Dict[str, CopyrightOwner] = {}
        self.detection_thresholds = self._initialize_detection_thresholds()
        self.territory_rules = self._initialize_territory_rules()
        self._initialize_detection_algorithms()
        
        logger.info("Copyright Detection Tracker initialized")
    
    def _initialize_detection_thresholds(self) -> Dict[str, float]:
        """Initialize detection thresholds for different scenarios."""
        return {
            'automatic_claim_threshold': 0.90,
            'manual_review_threshold': 0.75,
            'potential_match_threshold': 0.65,
            'fair_use_max_duration': 30.0,  # seconds
            'commercial_use_threshold': 0.80,
            'educational_use_threshold': 0.85,
            'parody_detection_threshold': 0.70
        }
    
    def _initialize_territory_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize territory-specific copyright rules."""
        return {
            'US': {
                'fair_use_duration': 30,
                'commercial_threshold': 0.85,
                'dmca_applicable': True,
                'safe_harbor_provisions': True
            },
            'EU': {
                'fair_use_duration': 15,
                'commercial_threshold': 0.90,
                'gdpr_compliance': True,
                'copyright_directive_applicable': True
            },
            'UK': {
                'fair_use_duration': 20,
                'commercial_threshold': 0.88,
                'fair_dealing_provisions': True
            },
            'DE': {
                'fair_use_duration': 12,
                'commercial_threshold': 0.92,
                'gema_licensing': True,
                'strict_copyright_enforcement': True
            },
            'GLOBAL': {
                'fair_use_duration': 10,
                'commercial_threshold': 0.95,
                'default_rules': True
            }
        }
    
    def _initialize_detection_algorithms(self):
        """Initialize copyright detection algorithms."""
        self.detection_algorithms = {
            'spectral_fingerprint': {
                'accuracy': 0.94,
                'processing_speed': 'fast',
                'best_for': ['music', 'audio_effects']
            },
            'neural_audio_match': {
                'accuracy': 0.96,
                'processing_speed': 'medium',
                'best_for': ['voice', 'complex_audio']
            },
            'perceptual_hash': {
                'accuracy': 0.88,
                'processing_speed': 'very_fast',
                'best_for': ['simple_audio', 'repetitive_content']
            },
            'deep_content_analysis': {
                'accuracy': 0.98,
                'processing_speed': 'slow',
                'best_for': ['comprehensive_analysis', 'disputed_claims']
            }
        }
    
    async def register_copyrighted_content(self, content_fingerprint: str,
                                         owner: CopyrightOwner,
                                         title: str, artist: str,
                                         content_category: ContentCategory,
                                         duration_seconds: float,
                                         territories_protected: List[str],
                                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """Register copyrighted content in the protection database."""
        reference_id = str(uuid.uuid4())
        
        copyright_entry = CopyrightDatabase(
            reference_id=reference_id,
            content_fingerprint=content_fingerprint,
            owner=owner,
            title=title,
            artist=artist,
            content_category=content_category,
            duration_seconds=duration_seconds,
            territories_protected=territories_protected,
            licenses_available=[],
            metadata=metadata or {}
        )
        
        self.copyright_database[reference_id] = copyright_entry
        
        # Register owner if not exists
        if owner.owner_id not in self.copyright_owners:
            self.copyright_owners[owner.owner_id] = owner
        
        logger.info(f"Copyrighted content registered: {reference_id} - {title} by {artist}")
        return reference_id
    
    async def detect_copyright_infringement(self, content_id: str,
                                          content_fingerprint: str,
                                          territory: str = "GLOBAL",
                                          content_metadata: Optional[Dict[str, Any]] = None) -> List[CopyrightClaim]:
        """Detect potential copyright infringement for uploaded content."""
        claims = []
        detection_start = datetime.utcnow()
        
        # Search through copyright database for matches
        for ref_id, copyright_entry in self.copyright_database.items():
            if territory not in copyright_entry.territories_protected and "GLOBAL" not in copyright_entry.territories_protected:
                continue
            
            # Calculate similarity using AI algorithms
            similarity_score = await self._calculate_content_similarity(
                content_fingerprint, copyright_entry.content_fingerprint,
                copyright_entry.content_category
            )
            
            # Determine if similarity warrants a claim
            if similarity_score >= self.detection_thresholds['potential_match_threshold']:
                claim = await self._create_copyright_claim(
                    content_id, ref_id, similarity_score, territory,
                    copyright_entry, content_metadata or {}
                )
                claims.append(claim)
        
        detection_time = (datetime.utcnow() - detection_start).total_seconds() * 1000
        
        # Sort claims by similarity score
        claims.sort(key=lambda c: c.similarity_score, reverse=True)
        
        logger.info(f"Copyright detection completed: {len(claims)} potential matches found "
                   f"in {detection_time:.1f}ms for content {content_id}")
        
        return claims
    
    async def _calculate_content_similarity(self, content_fp: str, reference_fp: str,
                                          content_category: ContentCategory) -> float:
        """Calculate similarity between content and reference fingerprints."""
        # Simulate AI-powered similarity calculation
        await asyncio.sleep(0.002)  # Simulate processing time
        
        # Choose best algorithm for content category
        algorithm = self._select_best_algorithm(content_category)
        algorithm_accuracy = self.detection_algorithms[algorithm]['accuracy']
        
        # Simulate fingerprint comparison
        # In production, this would use actual fingerprint matching algorithms
        base_similarity = 0.3 + (hash(content_fp + reference_fp) % 70) / 100
        
        # Adjust based on algorithm accuracy
        adjusted_similarity = base_similarity * algorithm_accuracy
        
        return min(1.0, max(0.0, adjusted_similarity))
    
    def _select_best_algorithm(self, content_category: ContentCategory) -> str:
        """Select the best detection algorithm for content category."""
        category_algorithm_map = {
            ContentCategory.MUSIC: 'spectral_fingerprint',
            ContentCategory.VOICE_RECORDING: 'neural_audio_match',
            ContentCategory.SOUND_EFFECTS: 'perceptual_hash',
            ContentCategory.PODCAST: 'neural_audio_match',
            ContentCategory.AUDIOBOOK: 'neural_audio_match',
            ContentCategory.COMMERCIAL: 'deep_content_analysis'
        }
        
        return category_algorithm_map.get(content_category, 'spectral_fingerprint')
    
    async def _create_copyright_claim(self, content_id: str, reference_id: str,
                                    similarity_score: float, territory: str,
                                    copyright_entry: CopyrightDatabase,
                                    content_metadata: Dict[str, Any]) -> CopyrightClaim:
        """Create a copyright claim based on detection results."""
        claim_id = str(uuid.uuid4())
        
        # Determine detection confidence
        confidence = self._calculate_detection_confidence(similarity_score)
        
        # Determine copyright status
        copyright_status = self._determine_copyright_status(
            similarity_score, territory, copyright_entry, content_metadata
        )
        
        # Determine if manual review is required
        manual_review_required = (
            confidence in [DetectionConfidence.LOW, DetectionConfidence.MEDIUM] or
            similarity_score < self.detection_thresholds['automatic_claim_threshold']
        )
        
        # Calculate match duration and timing
        match_duration = min(
            content_metadata.get('duration_seconds', 0),
            copyright_entry.duration_seconds
        )
        
        # Create evidence data
        evidence_data = {
            'similarity_algorithm': self._select_best_algorithm(copyright_entry.content_category),
            'fingerprint_match_points': int(similarity_score * 100),
            'reference_metadata': {
                'title': copyright_entry.title,
                'artist': copyright_entry.artist,
                'isrc': copyright_entry.isrc
            },
            'territory_rules_applied': self.territory_rules.get(territory, {}),
            'detection_timestamp': datetime.utcnow().isoformat()
        }
        
        claim = CopyrightClaim(
            claim_id=claim_id,
            content_id=content_id,
            claimant_id=copyright_entry.owner.owner_id,
            original_content_id=reference_id,
            similarity_score=similarity_score,
            detection_confidence=confidence,
            copyright_status=copyright_status,
            content_category=copyright_entry.content_category,
            match_duration_seconds=match_duration,
            match_start_time=0.0,  # Assume full match for now
            detection_algorithm=self._select_best_algorithm(copyright_entry.content_category),
            evidence_data=evidence_data,
            claim_details=f"Potential copyright infringement detected with {similarity_score:.1%} similarity",
            automatic_detection=True,
            manual_review_required=manual_review_required
        )
        
        self.copyright_claims.append(claim)
        
        # Log claim based on severity
        if copyright_status == CopyrightStatus.COPYRIGHT_MATCH:
            logger.warning(f"Copyright infringement detected: {claim_id} "
                          f"(similarity={similarity_score:.3f})")
        else:
            logger.info(f"Potential copyright match: {claim_id} "
                       f"(similarity={similarity_score:.3f})")
        
        return claim
    
    def _calculate_detection_confidence(self, similarity_score: float) -> DetectionConfidence:
        """Calculate detection confidence based on similarity score."""
        if similarity_score >= 0.95:
            return DetectionConfidence.VERY_HIGH
        elif similarity_score >= 0.85:
            return DetectionConfidence.HIGH
        elif similarity_score >= 0.70:
            return DetectionConfidence.MEDIUM
        elif similarity_score >= 0.50:
            return DetectionConfidence.LOW
        else:
            return DetectionConfidence.VERY_LOW
    
    def _determine_copyright_status(self, similarity_score: float, territory: str,
                                  copyright_entry: CopyrightDatabase,
                                  content_metadata: Dict[str, Any]) -> CopyrightStatus:
        """Determine copyright status based on various factors."""
        territory_rules = self.territory_rules.get(territory, self.territory_rules['GLOBAL'])
        
        # Check for automatic copyright match
        if similarity_score >= self.detection_thresholds['automatic_claim_threshold']:
            return CopyrightStatus.COPYRIGHT_MATCH
        
        # Check for potential fair use
        content_duration = content_metadata.get('duration_seconds', 0)
        if content_duration <= territory_rules.get('fair_use_duration', 10):
            if similarity_score < territory_rules.get('commercial_threshold', 0.90):
                return CopyrightStatus.FAIR_USE
        
        # Check for licensed content
        if content_metadata.get('has_license', False):
            return CopyrightStatus.LICENSED
        
        # Default to potential match for manual review
        if similarity_score >= self.detection_thresholds['manual_review_threshold']:
            return CopyrightStatus.POTENTIAL_MATCH
        
        return CopyrightStatus.CLEAR
    
    def get_claim_by_id(self, claim_id: str) -> Optional[CopyrightClaim]:
        """Get copyright claim by ID."""
        for claim in self.copyright_claims:
            if claim.claim_id == claim_id:
                return claim
        return None
    
    def get_claims_for_content(self, content_id: str) -> List[CopyrightClaim]:
        """Get all copyright claims for specific content."""
        return [claim for claim in self.copyright_claims if claim.content_id == content_id]
    
    def get_claims_by_owner(self, owner_id: str) -> List[CopyrightClaim]:
        """Get all copyright claims by specific owner."""
        return [claim for claim in self.copyright_claims if claim.claimant_id == owner_id]
    
    async def update_claim_status(self, claim_id: str, new_status: CopyrightStatus,
                                review_notes: Optional[str] = None) -> bool:
        """Update copyright claim status (manual review result)."""
        claim = self.get_claim_by_id(claim_id)
        if not claim:
            return False
        
        old_status = claim.copyright_status
        claim.copyright_status = new_status
        claim.manual_review_required = False
        
        if review_notes:
            claim.evidence_data['review_notes'] = review_notes
            claim.evidence_data['review_timestamp'] = datetime.utcnow().isoformat()
        
        logger.info(f"Claim status updated: {claim_id} ({old_status.value} → {new_status.value})")
        return True
    
    def get_copyright_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get comprehensive copyright detection statistics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_claims = [
            claim for claim in self.copyright_claims
            if claim.timestamp >= cutoff_time
        ]
        
        if not recent_claims:
            return {"message": f"No copyright detection activity in last {hours} hours"}
        
        # Status distribution
        status_counts = {}
        for status in CopyrightStatus:
            status_counts[status.value] = len([c for c in recent_claims if c.copyright_status == status])
        
        # Confidence distribution
        confidence_counts = {}
        for confidence in DetectionConfidence:
            confidence_counts[confidence.value] = len([c for c in recent_claims if c.detection_confidence == confidence])
        
        # Category analysis
        category_stats = {}
        for category in ContentCategory:
            category_claims = [c for c in recent_claims if c.content_category == category]
            if category_claims:
                avg_similarity = sum(c.similarity_score for c in category_claims) / len(category_claims)
                category_stats[category.value] = {
                    'total_claims': len(category_claims),
                    'avg_similarity_score': avg_similarity,
                    'copyright_matches': len([c for c in category_claims if c.copyright_status == CopyrightStatus.COPYRIGHT_MATCH])
                }
        
        # Performance metrics
        automatic_claims = [c for c in recent_claims if c.automatic_detection]
        manual_review_needed = [c for c in recent_claims if c.manual_review_required]
        
        return {
            'period_hours': hours,
            'total_claims': len(recent_claims),
            'copyright_infringements': status_counts.get('copyright_match', 0),
            'potential_matches': status_counts.get('potential_match', 0),
            'status_distribution': status_counts,
            'confidence_distribution': confidence_counts,
            'category_analysis': category_stats,
            'detection_performance': {
                'automatic_detection_rate': len(automatic_claims) / len(recent_claims) if recent_claims else 0,
                'manual_review_rate': len(manual_review_needed) / len(recent_claims) if recent_claims else 0,
                'avg_similarity_score': sum(c.similarity_score for c in recent_claims) / len(recent_claims),
                'high_confidence_claims': len([c for c in recent_claims if c.detection_confidence in [DetectionConfidence.HIGH, DetectionConfidence.VERY_HIGH]])
            },
            'database_statistics': {
                'registered_content_items': len(self.copyright_database),
                'registered_owners': len(self.copyright_owners),
                'protected_territories': len(set(territory for entry in self.copyright_database.values() for territory in entry.territories_protected))
            }
        }
    
    def get_territory_compliance_report(self, territory: str) -> Dict[str, Any]:
        """Get compliance report for specific territory."""
        territory_claims = [
            claim for claim in self.copyright_claims
            if territory in self.copyright_database.get(claim.original_content_id, CopyrightDatabase("", "", CopyrightOwner("", "", ""), "", "", ContentCategory.MUSIC, 0.0, [])).territories_protected
        ]
        
        territory_rules = self.territory_rules.get(territory, self.territory_rules['GLOBAL'])
        
        # Analyze compliance with territory rules
        fair_use_claims = [c for c in territory_claims if c.copyright_status == CopyrightStatus.FAIR_USE]
        copyright_violations = [c for c in territory_claims if c.copyright_status == CopyrightStatus.COPYRIGHT_MATCH]
        
        return {
            'territory': territory,
            'total_claims': len(territory_claims),
            'copyright_violations': len(copyright_violations),
            'fair_use_determinations': len(fair_use_claims),
            'territory_rules': territory_rules,
            'compliance_rate': (len(territory_claims) - len(copyright_violations)) / len(territory_claims) if territory_claims else 1.0,
            'average_similarity_score': sum(c.similarity_score for c in territory_claims) / len(territory_claims) if territory_claims else 0.0
        }

# Global copyright detection tracker instance
copyright_detection_tracker = CopyrightDetectionTracker()

# Export main components
__all__ = [
    'CopyrightDetectionTracker',
    'CopyrightClaim',
    'CopyrightDatabase',
    'CopyrightOwner',
    'CopyrightStatus',
    'DetectionConfidence',
    'ContentCategory',
    'copyright_detection_tracker'
]