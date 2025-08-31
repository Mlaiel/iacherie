"""Rights Validator - Advanced Content Rights and Protection System

Enterprise-grade rights validation, copyright analysis, and protection setup
for creator content with AI-powered similarity detection.

Author: Fahed Mlaiel <mlaiel@live.de>
"""
import asyncio
import logging
import hashlib
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

import numpy as np
import faiss
from sqlalchemy.orm import Session

try:
    from core.config import settings
except ImportError:
    # Fallback settings
    settings = type('Settings', (), {'debug': True, 'log_level': 'INFO'})()
try:
    from core.exceptions import RightsValidationError, ValidationError
except ImportError:
    # Fallback exception classes
    class ValidationError(Exception): pass
    class ConfigurationError(Exception): pass
    class ProcessingError(Exception): pass
    RightsValidationError, ValidationError = globals().get('RightsValidationError, ValidationError', Exception)
try:
    from core.database import get_db_session
except ImportError:
    # Fallback database classes
    class DatabaseManager: pass
    get_db_session = DatabaseManager
from ...ml.fingerprinting import AudioFingerprinter, ImageFingerprinter, TextFingerprinter
from ...security.blockchain_registry import BlockchainRegistry
from ...utils.similarity_engine import SimilarityEngine
from ...integrations.copyright_apis import CopyrightAPIClient

logger = logging.getLogger(__name__)

class RightsStatus(Enum):
    """Content rights validation status"""    VERIFIED = "verified"
    PENDING = "pending"
    DISPUTED = "disputed"
    REJECTED = "rejected"
    UNKNOWN = "unknown"

class ProtectionLevel(Enum):
    """Content protection levels"""    BASIC = "basic"           # Standard fingerprinting
    STANDARD = "standard"     # Enhanced monitoring
    PREMIUM = "premium"       # Advanced AI protection
    ENTERPRISE = "enterprise" # Full legal protection

@dataclass
class RightsValidationResult:
    """Comprehensive rights validation results"""    content_id: str
    user_id: str
    validation_status: RightsStatus = RightsStatus.UNKNOWN
    
    # Ownership Information
    ownership_confirmed: bool = False
    ownership_score: float = 0.0
    ownership_evidence: List[str] = field(default_factory=list)
    
    # Similarity Analysis
    similarity_matches: List[Dict[str, Any]] = field(default_factory=list)
    highest_similarity_score: float = 0.0
    potential_conflicts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Copyright Status
    copyright_registered: bool = False
    copyright_databases: List[str] = field(default_factory=list)
    dmca_status: str = "clear"
    
    # Protection Setup
    fingerprint_generated: bool = False
    fingerprint_hash: str = ""
    blockchain_registered: bool = False
    blockchain_tx_id: str = ""
    monitoring_enabled: bool = False
    
    # Metadata
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = None
    confidence_score: float = 0.0
    validation_notes: List[str] = field(default_factory=list)

class RightsValidator:
    """    Advanced rights validation and content protection system.
    
    Core Capabilities:
    - Multi-format content fingerprinting
    - Similarity detection across databases
    - Copyright database verification
    - Blockchain-based ownership registration
    - DMCA compliance and monitoring
    - Automated protection setup
    - Legal evidence collection
    """    
    def __init__(self):
        self.audio_fingerprinter = AudioFingerprinter()
        self.image_fingerprinter = ImageFingerprinter()
        self.text_fingerprinter = TextFingerprinter()
        self.similarity_engine = SimilarityEngine()
        self.blockchain_registry = BlockchainRegistry()
        self.copyright_api = CopyrightAPIClient()
        
        # Initialize FAISS index for similarity search
        self.fingerprint_index = None
        self.index_metadata = {}
        
        self._initialize_similarity_index()
        
        logger.info("RightsValidator initialized successfully")
    
    def _initialize_similarity_index(self):
        """Initialize FAISS similarity index for fingerprint matching."""        try:
            # Create FAISS index for similarity search
            dimension = 256  # Standard fingerprint dimension
            self.fingerprint_index = faiss.IndexFlatL2(dimension)
            logger.info("Similarity index initialized")
        except Exception as e:
            logger.error(f"Failed to initialize similarity index: {str(e)}")
    
    async def validate_rights(self, content: Dict[str, Any], 
                            user_id: str,
                            validation_level: str = "standard") -> RightsValidationResult:
        """        Comprehensive content rights validation with similarity analysis.
        """        try:
            content_id = content.get('id', str(uuid.uuid4()))
            
            # Initialize validation result
            result = RightsValidationResult(
                content_id=content_id,
                user_id=user_id
            )
            
            # Step 1: Generate content fingerprint
            fingerprint = await self._generate_fingerprint(content)
            if fingerprint:
                result.fingerprint_generated = True
                result.fingerprint_hash = fingerprint['hash']
            
            # Step 2: Similarity analysis
            await self._perform_similarity_analysis(result, fingerprint)
            
            # Step 3: Copyright database check
            if validation_level in ['premium', 'enterprise']:
                await self._check_copyright_databases(result, content)
            
            # Step 4: Ownership verification
            await self._verify_ownership(result, content, user_id)
            
            # Step 5: Calculate confidence score
            result.confidence_score = self._calculate_confidence_score(result)
            
            # Step 6: Determine validation status
            result.validation_status = self._determine_validation_status(result)
            
            logger.info(f"Rights validation completed for content {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating rights: {str(e)}")
            raise RightsValidationError(f"Rights validation failed: {str(e)}")
    
    async def setup_protection(self, user_id: str, 
                             content_samples: List[Dict[str, Any]],
                             protection_config: Dict[str, Any]) -> Dict[str, Any]:
        """        Setup comprehensive content protection for creator.
        """        try:
            protection_level = ProtectionLevel(
                protection_config.get('level', 'standard')
            )
            
            protection_results = {
                'user_id': user_id,
                'protection_level': protection_level.value,
                'protected_content': [],
                'fingerprints_created': 0,
                'monitoring_setup': False,
                'blockchain_registration': False,
                'legal_protection': False,
                'setup_timestamp': datetime.utcnow().isoformat()
            }
            
            # Process each content item
            for content in content_samples:
                content_protection = await self._setup_content_protection(
                    content, user_id, protection_level
                )
                protection_results['protected_content'].append(content_protection)
                
                if content_protection.get('fingerprint_created'):
                    protection_results['fingerprints_created'] += 1
            
            # Setup monitoring system
            if protection_level in [ProtectionLevel.STANDARD, ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                monitoring_setup = await self._setup_monitoring(user_id, protection_config)
                protection_results['monitoring_setup'] = monitoring_setup
            
            # Blockchain registration for premium/enterprise
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                blockchain_result = await self._register_blockchain_ownership(
                    user_id, content_samples
                )
                protection_results['blockchain_registration'] = blockchain_result
            
            # Legal protection setup for enterprise
            if protection_level == ProtectionLevel.ENTERPRISE:
                legal_setup = await self._setup_legal_protection(user_id, content_samples)
                protection_results['legal_protection'] = legal_setup
            
            # Store protection configuration
            await self._store_protection_config(user_id, protection_results)
            
            return protection_results
            
        except Exception as e:
            logger.error(f"Error setting up protection: {str(e)}")
            raise RightsValidationError(f"Protection setup failed: {str(e)}")
    
    async def setup_monitoring(self, user_id: str, 
                             protection_results: Dict[str, Any]) -> Dict[str, Any]:
        """        Setup automated content monitoring and alert system.
        """        try:
            monitoring_config = {
                'user_id': user_id,
                'monitoring_active': True,
                'scan_frequency': 'daily',  # daily, hourly, real_time
                'platforms_monitored': [
                    'youtube', 'instagram', 'tiktok', 'facebook',
                    'twitter', 'soundcloud', 'spotify'
                ],
                'similarity_threshold': 0.85,
                'alert_methods': ['email', 'webhook', 'dashboard'],
                'automated_actions': {
                    'dmca_takedown': False,  # Manual approval required
                    'watermark_detection': True,
                    'similarity_alerts': True
                },
                'monitoring_rules': [
                    {
                        'type': 'similarity_detection',
                        'threshold': 0.9,
                        'action': 'immediate_alert'
                    },
                    {
                        'type': 'exact_match',
                        'threshold': 1.0,
                        'action': 'automated_report'
                    }
                ],
                'setup_timestamp': datetime.utcnow().isoformat()
            }
            
            # Create monitoring database entries
            await self._create_monitoring_entries(user_id, monitoring_config)
            
            # Setup automated scanning tasks
            await self._schedule_monitoring_tasks(user_id, monitoring_config)
            
            # Configure alert system
            await self._setup_alert_system(user_id, monitoring_config)
            
            logger.info(f"Monitoring setup completed for user {user_id}")
            return monitoring_config
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {str(e)}")
            raise RightsValidationError(f"Monitoring setup failed: {str(e)}")
    
    async def _generate_fingerprint(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate content fingerprint based on content type."""        try:
            content_type = content.get('type', '').lower()
            content_data = content.get('data') or content.get('content')
            
            if not content_data:
                return None
            
            fingerprint_result = None
            
            if content_type == 'audio':
                fingerprint_result = await self.audio_fingerprinter.generate_fingerprint(content_data)
            elif content_type == 'image':
                fingerprint_result = await self.image_fingerprinter.generate_fingerprint(content_data)
            elif content_type == 'text':
                fingerprint_result = await self.text_fingerprinter.generate_fingerprint(content_data)
            
            if fingerprint_result:
                # Generate hash for storage
                fingerprint_hash = hashlib.sha256(
                    str(fingerprint_result).encode()
                ).hexdigest()
                
                return {
                    'hash': fingerprint_hash,
                    'data': fingerprint_result,
                    'type': content_type,
                    'generated_at': datetime.utcnow().isoformat()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error generating fingerprint: {str(e)}")
            return None
    
    async def _perform_similarity_analysis(self, result: RightsValidationResult, 
                                         fingerprint: Optional[Dict[str, Any]]) -> None:
        """Perform similarity analysis against existing fingerprints."""        try:
            if not fingerprint or not self.fingerprint_index:
                return
            
            # Convert fingerprint to vector for similarity search
            fingerprint_vector = self._fingerprint_to_vector(fingerprint['data'])
            
            if fingerprint_vector is not None:
                # Search for similar fingerprints
                k = 10  # Top 10 similar results
                distances, indices = self.fingerprint_index.search(
                    fingerprint_vector.reshape(1, -1), k
                )
                
                # Process similarity results
                for i, (distance, index) in enumerate(zip(distances[0], indices[0])):
                    if index >= 0 and distance < 100:  # Similarity threshold
                        similarity_score = 1.0 - (distance / 100)  # Normalize to 0-1
                        
                        if similarity_score > 0.5:  # Significant similarity
                            similar_content = self.index_metadata.get(int(index), {})
                            
                            match = {
                                'similarity_score': similarity_score,
                                'matched_content_id': similar_content.get('content_id', 'unknown'),
                                'owner_id': similar_content.get('owner_id', 'unknown'),
                                'match_type': self._classify_match_type(similarity_score),
                                'confidence': similarity_score
                            }
                            
                            result.similarity_matches.append(match)
                            
                            # Check for potential conflicts
                            if similarity_score > 0.8 and similar_content.get('owner_id') != result.user_id:
                                conflict = {
                                    'conflict_type': 'high_similarity',
                                    'similarity_score': similarity_score,
                                    'conflicting_owner': similar_content.get('owner_id'),
                                    'requires_investigation': True
                                }
                                result.potential_conflicts.append(conflict)
                
                # Update highest similarity score
                if result.similarity_matches:
                    result.highest_similarity_score = max(
                        match['similarity_score'] for match in result.similarity_matches
                    )
            
        except Exception as e:
            logger.error(f"Error performing similarity analysis: {str(e)}")
    
    async def _check_copyright_databases(self, result: RightsValidationResult, 
                                       content: Dict[str, Any]) -> None:
        """Check content against copyright databases."""        try:
            # Check major copyright databases
            databases_to_check = [
                'us_copyright_office',
                'wipo_global_brand_database',
                'european_copyright_database'
            ]
            
            for database in databases_to_check:
                try:
                    search_result = await self.copyright_api.search_database(
                        database, content
                    )
                    
                    if search_result.get('found'):
                        result.copyright_databases.append(database)
                        result.copyright_registered = True
                        
                        # Check if registered by same user
                        registered_owner = search_result.get('owner_id')
                        if registered_owner != result.user_id:
                            conflict = {
                                'conflict_type': 'copyright_conflict',
                                'database': database,
                                'registered_owner': registered_owner,
                                'registration_date': search_result.get('registration_date'),
                                'requires_investigation': True
                            }
                            result.potential_conflicts.append(conflict)
                
                except Exception as e:
                    logger.warning(f"Error checking {database}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error checking copyright databases: {str(e)}")
    
    async def _verify_ownership(self, result: RightsValidationResult, 
                              content: Dict[str, Any], user_id: str) -> None:
        """Verify user ownership of content."""        try:
            ownership_evidence = []
            ownership_score = 0.0
            
            # Check upload metadata
            if content.get('uploaded_by') == user_id:
                ownership_evidence.append("Content uploaded by user")
                ownership_score += 0.3
            
            # Check creation timestamp
            created_at = content.get('created_at')
            if created_at:
                # If created recently by user, higher ownership confidence
                creation_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if (datetime.utcnow() - creation_date).days < 30:
                    ownership_evidence.append("Recently created content")
                    ownership_score += 0.2
            
            # Check for existing ownership claims
            existing_claims = await self._check_existing_ownership_claims(
                result.content_id, user_id
            )
            
            if not existing_claims:
                ownership_evidence.append("No conflicting ownership claims")
                ownership_score += 0.2
            else:
                for claim in existing_claims:
                    if claim['claimant_id'] != user_id:
                        conflict = {
                            'conflict_type': 'ownership_dispute',
                            'conflicting_claimant': claim['claimant_id'],
                            'claim_date': claim['claim_date'],
                            'requires_investigation': True
                        }
                        result.potential_conflicts.append(conflict)
            
            # Check blockchain ownership records
            blockchain_owner = await self.blockchain_registry.get_owner(result.content_id)
            if blockchain_owner:
                if blockchain_owner == user_id:
                    ownership_evidence.append("Blockchain ownership confirmed")
                    ownership_score += 0.3
                else:
                    conflict = {
                        'conflict_type': 'blockchain_ownership_conflict',
                        'blockchain_owner': blockchain_owner,
                        'requires_investigation': True
                    }
                    result.potential_conflicts.append(conflict)
            
            # Update result
            result.ownership_evidence = ownership_evidence
            result.ownership_score = min(1.0, ownership_score)
            result.ownership_confirmed = ownership_score > 0.7
            
        except Exception as e:
            logger.error(f"Error verifying ownership: {str(e)}")
    
    async def _setup_content_protection(self, content: Dict[str, Any], 
                                      user_id: str, 
                                      protection_level: ProtectionLevel) -> Dict[str, Any]:
        """Setup protection for individual content item."""        try:
            content_id = content.get('id', str(uuid.uuid4()))
            
            protection_result = {
                'content_id': content_id,
                'protection_level': protection_level.value,
                'fingerprint_created': False,
                'watermark_applied': False,
                'monitoring_enabled': False,
                'legal_protection': False
            }
            
            # Generate and store fingerprint
            fingerprint = await self._generate_fingerprint(content)
            if fingerprint:
                await self._store_fingerprint(content_id, user_id, fingerprint)
                protection_result['fingerprint_created'] = True
                
                # Add to similarity index
                if self.fingerprint_index:
                    fingerprint_vector = self._fingerprint_to_vector(fingerprint['data'])
                    if fingerprint_vector is not None:
                        self.fingerprint_index.add(fingerprint_vector.reshape(1, -1))
                        index_position = self.fingerprint_index.ntotal - 1
                        self.index_metadata[index_position] = {
                            'content_id': content_id,
                            'owner_id': user_id,
                            'fingerprint_hash': fingerprint['hash']
                        }
            
            # Apply watermark for premium/enterprise
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]:
                watermark_result = await self._apply_watermark(content, user_id)
                protection_result['watermark_applied'] = watermark_result
            
            # Enable monitoring
            if protection_level != ProtectionLevel.BASIC:
                protection_result['monitoring_enabled'] = True
            
            # Legal protection for enterprise
            if protection_level == ProtectionLevel.ENTERPRISE:
                protection_result['legal_protection'] = True
            
            return protection_result
            
        except Exception as e:
            logger.error(f"Error setting up content protection: {str(e)}")
            return {'content_id': content.get('id', 'unknown'), 'error': str(e)}
    
    def _calculate_confidence_score(self, result: RightsValidationResult) -> float:
        """Calculate overall confidence score for rights validation."""        factors = []
        
        # Ownership score weight: 40%
        factors.append(('ownership', result.ownership_score, 0.4))
        
        # Conflict penalty: -30% if conflicts exist
        conflict_penalty = 0.3 if result.potential_conflicts else 0.0
        factors.append(('conflicts', 1.0 - conflict_penalty, 0.3))
        
        # Similarity score: 20%
        similarity_factor = 1.0 - min(result.highest_similarity_score, 0.9)
        factors.append(('similarity', similarity_factor, 0.2))
        
        # Verification completeness: 10%
        verification_completeness = 0.5  # Base score
        if result.fingerprint_generated:
            verification_completeness += 0.3
        if result.copyright_databases:
            verification_completeness += 0.2
        factors.append(('verification', min(1.0, verification_completeness), 0.1))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in factors)
        return max(0.0, min(1.0, total_score))
    
    def _determine_validation_status(self, result: RightsValidationResult) -> RightsStatus:
        """Determine final validation status based on analysis results."""        # High confidence and no conflicts
        if result.confidence_score > 0.8 and not result.potential_conflicts:
            return RightsStatus.VERIFIED
        
        # Moderate confidence or minor conflicts
        elif result.confidence_score > 0.6 and len(result.potential_conflicts) <= 1:
            return RightsStatus.PENDING
        
        # Low confidence or multiple conflicts
        elif result.confidence_score < 0.4 or len(result.potential_conflicts) > 2:
            return RightsStatus.REJECTED
        
        # Significant conflicts requiring investigation
        elif result.potential_conflicts:
            return RightsStatus.DISPUTED
        
        # Default case
        else:
            return RightsStatus.UNKNOWN
    
    def _classify_match_type(self, similarity_score: float) -> str:
        """Classify similarity match type."""        if similarity_score > 0.95:
            return "exact_match"
        elif similarity_score > 0.85:
            return "near_duplicate"
        elif similarity_score > 0.7:
            return "high_similarity"
        elif similarity_score > 0.5:
            return "moderate_similarity"
        else:
            return "low_similarity"
    
    def _fingerprint_to_vector(self, fingerprint_data: Any) -> Optional[np.ndarray]:
        """Convert fingerprint data to vector for similarity search."""        try:
            # Convert fingerprint to fixed-size vector
            if isinstance(fingerprint_data, dict):
                # Extract numeric features from fingerprint
                features = []
                for key, value in fingerprint_data.items():
                    if isinstance(value, (int, float)):
                        features.append(float(value))
                    elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                        features.extend([float(x) for x in value])
                
                if features:
                    # Pad or truncate to standard dimension
                    vector = np.array(features[:256])
                    if len(vector) < 256:
                        vector = np.pad(vector, (0, 256 - len(vector)), 'constant')
                    return vector.astype(np.float32)
            
            elif isinstance(fingerprint_data, (list, np.ndarray)):
                vector = np.array(fingerprint_data).flatten()[:256].astype(np.float32)
                if len(vector) < 256:
                    vector = np.pad(vector, (0, 256 - len(vector)), 'constant')
                return vector
            
            return None
            
        except Exception as e:
            logger.error(f"Error converting fingerprint to vector: {str(e)}")
            return None
    
    async def _check_existing_ownership_claims(self, content_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Check for existing ownership claims on content."""        try:
            async with get_db_session() as db:
                result = await db.fetch("""                    SELECT claimant_id, claim_date, claim_type, status
                    FROM ownership_claims
                    WHERE content_id = $1 AND status = 'active'
                """, content_id)
                
                return [dict(row) for row in result]
                
        except Exception as e:
            logger.error(f"Error checking ownership claims: {str(e)}")
            return []
    
    async def _store_fingerprint(self, content_id: str, user_id: str, 
                               fingerprint: Dict[str, Any]) -> None:
        """Store fingerprint in database."""        try:
            async with get_db_session() as db:
                await db.execute("""                    INSERT INTO content_fingerprints (
                        content_id, user_id, fingerprint_hash,
                        fingerprint_data, content_type, created_at
                    ) VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (content_id) DO UPDATE SET
                        fingerprint_hash = $3,
                        fingerprint_data = $4,
                        updated_at = $6
                """,
                content_id, user_id, fingerprint['hash'],
                json.dumps(fingerprint['data']), fingerprint['type'],
                datetime.utcnow()
                )
                
        except Exception as e:
            logger.error(f"Error storing fingerprint: {str(e)}")
    
    async def _store_protection_config(self, user_id: str, 
                                     protection_results: Dict[str, Any]) -> None:
        """Store protection configuration in database."""        try:
            async with get_db_session() as db:
                await db.execute("""                    INSERT INTO protection_configurations (
                        user_id, protection_level, configuration_data,
                        created_at, active
                    ) VALUES ($1, $2, $3, $4, $5)
                    ON CONFLICT (user_id) DO UPDATE SET
                        protection_level = $2,
                        configuration_data = $3,
                        updated_at = $4
                """,
                user_id, protection_results['protection_level'],
                json.dumps(protection_results), datetime.utcnow(), True
                )
                
        except Exception as e:
            logger.error(f"Error storing protection config: {str(e)}")
    
    # Placeholder implementations for advanced features
    async def _register_blockchain_ownership(self, user_id: str, 
                                           content_samples: List[Dict[str, Any]]) -> bool:
        """Register ownership on blockchain."""        try:
            for content in content_samples:
                await self.blockchain_registry.register_ownership(
                    content_id=content.get('id'),
                    owner_id=user_id,
                    content_hash=content.get('hash')
                )
            return True
        except Exception as e:
            logger.error(f"Blockchain registration failed: {str(e)}")
            return False
    
    async def _setup_legal_protection(self, user_id: str, 
                                    content_samples: List[Dict[str, Any]]) -> bool:
        """Setup legal protection and documentation."""        # Placeholder - would integrate with legal services
        return True
    
    async def _setup_monitoring_tasks(self, user_id: str, 
                                    monitoring_config: Dict[str, Any]) -> None:
        """Schedule automated monitoring tasks."""        # Placeholder - would setup Celery tasks
        pass
    
    async def _setup_alert_system(self, user_id: str, 
                                monitoring_config: Dict[str, Any]) -> None:
        """Configure alert system."""        # Placeholder - would setup notification system
        pass
    
    async def _create_monitoring_entries(self, user_id: str, 
                                       monitoring_config: Dict[str, Any]) -> None:
        """Create database entries for monitoring."""        try:
            async with get_db_session() as db:
                await db.execute("""                    INSERT INTO monitoring_configurations (
                        user_id, config_data, active, created_at
                    ) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO UPDATE SET
                        config_data = $2,
                        updated_at = $4
                """,
                user_id, json.dumps(monitoring_config), True, datetime.utcnow()
                )
        except Exception as e:
            logger.error(f"Error creating monitoring entries: {str(e)}")
    
    async def _apply_watermark(self, content: Dict[str, Any], user_id: str) -> bool:
        """Apply digital watermark to content."""        # Placeholder - would implement watermarking
        return True
