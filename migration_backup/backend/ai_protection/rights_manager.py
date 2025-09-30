"""Digital Rights Manager

Comprehensive digital rights management system coordinating all protection mechanisms.
Centralizes watermarking, blockchain registry, copyright detection, and NFT generation.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel - All Rights Reserved
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import uuid

from .watermark_engine import WatermarkEngine, WatermarkConfig, ContentType, WatermarkType
from .blockchain_registry import BlockchainRightsRegistry, RightsType
from .copyright_detector import CopyrightDetector, ViolationType
from .nft_generator import NFTGenerator

logger = logging.getLogger(__name__)


class ProtectionLevel(Enum):
    """Levels of content protection"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class RightsStatus(Enum):
    """Rights management status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    SUSPENDED = "suspended"
    VIOLATED = "violated"
    PENDING = "pending"


@dataclass
class ContentRegistration:
    """Content registration record"""
    content_id: str
    owner_id: str
    content_type: str
    protection_level: ProtectionLevel
    watermark_id: Optional[str]
    blockchain_tx: Optional[str]
    nft_certificate: Optional[str]
    registration_timestamp: str
    rights_status: RightsStatus
    metadata: Dict[str, Any]


@dataclass
class ProtectionReport:
    """Comprehensive protection report"""
    content_id: str
    protection_summary: Dict[str, Any]
    watermark_status: Dict[str, Any]
    blockchain_status: Dict[str, Any]
    copyright_monitoring: Dict[str, Any]
    nft_certificate_status: Dict[str, Any]
    violations_detected: List[Dict[str, Any]]
    recommendations: List[str]
    report_timestamp: str


class DigitalRightsManager:
    """Comprehensive digital rights management system"""
    
    def __init__(self,
                 blockchain_url: Optional[str] = None,
                 private_key: Optional[str] = None,
                 contract_address: Optional[str] = None):
        """
        Initialize digital rights manager
        
        Args:
            blockchain_url: Blockchain RPC URL
            private_key: Private key for transactions
            contract_address: Smart contract address
        """
        # Initialize component engines
        self.watermark_engine = WatermarkEngine()
        self.blockchain_registry = BlockchainRightsRegistry(
            blockchain_url, private_key, contract_address
        )
        self.copyright_detector = CopyrightDetector()
        self.nft_generator = NFTGenerator(
            blockchain_url, private_key, contract_address
        )
        
        # Content registry
        self._content_registry = {}
        self._protection_policies = {}
        
        # Initialize default protection policies
        self._initialize_protection_policies()
    
    async def register_content(self,
                             content_data: Union[bytes, str],
                             content_type: str,
                             owner_id: str,
                             protection_level: ProtectionLevel = ProtectionLevel.STANDARD,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive content registration with full protection
        
        Args:
            content_data: Content to protect
            content_type: Type of content
            owner_id: Content owner
            protection_level: Level of protection to apply
            metadata: Additional metadata
            
        Returns:
            Registration result with all protection details
        """
        try:
            content_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            logger.info(f"Starting content registration: {content_id}")
            
            # Get protection policy
            policy = self._protection_policies[protection_level]
            
            protection_results = {}
            
            # Step 1: Register with copyright detector
            if policy['enable_copyright_detection']:
                copyright_result = await self.copyright_detector.register_original_content(
                    content_id, content_data, content_type, owner_id, metadata
                )
                protection_results['copyright_registration'] = copyright_result
            
            # Step 2: Apply watermarking
            watermark_id = None
            if policy['enable_watermarking']:
                watermark_config = WatermarkConfig(
                    watermark_type=WatermarkType.INVISIBLE,
                    strength=policy['watermark_strength'],
                    redundancy=policy['watermark_redundancy']
                )
                
                watermark_result = await self.watermark_engine.embed_watermark(
                    content_data,
                    ContentType(content_type),
                    f"© {owner_id} - {content_id}",
                    owner_id,
                    watermark_config
                )
                
                if watermark_result.success:
                    watermark_id = watermark_result.watermark_id
                    content_data = watermark_result.watermark_data.get('watermarked_content', content_data)
                
                protection_results['watermarking'] = asdict(watermark_result)
            
            # Step 3: Blockchain registration
            blockchain_tx = None
            if policy['enable_blockchain']:
                blockchain_result = await self.blockchain_registry.register_rights(
                    content_id,
                    owner_id,
                    RightsType.COPYRIGHT,
                    {
                        'content_type': content_type,
                        'protection_level': protection_level.value,
                        'watermark_id': watermark_id,
                        'metadata': metadata or {}
                    }
                )
                
                if blockchain_result['success']:
                    blockchain_tx = blockchain_result['blockchain_tx']
                
                protection_results['blockchain_registration'] = blockchain_result
            
            # Step 4: NFT certificate generation
            nft_certificate = None
            if policy['enable_nft_certificates']:
                nft_result = await self.nft_generator.generate_copyright_certificate(
                    content_id,
                    owner_id,
                    metadata or {'type': content_type}
                )
                
                if nft_result.success:
                    nft_certificate = nft_result.nft_id
                
                protection_results['nft_certificate'] = asdict(nft_result)
            
            # Create content registration record
            registration = ContentRegistration(
                content_id=content_id,
                owner_id=owner_id,
                content_type=content_type,
                protection_level=protection_level,
                watermark_id=watermark_id,
                blockchain_tx=blockchain_tx,
                nft_certificate=nft_certificate,
                registration_timestamp=timestamp,
                rights_status=RightsStatus.ACTIVE,
                metadata=metadata or {}
            )
            
            # Store registration
            self._content_registry[content_id] = asdict(registration)
            
            logger.info(f"Content registration completed: {content_id}")
            
            return {
                'success': True,
                'content_id': content_id,
                'registration': asdict(registration),
                'protection_results': protection_results,
                'protected_content': content_data if isinstance(content_data, bytes) else None
            }
            
        except Exception as e:
            logger.error(f"Content registration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def monitor_content_violations(self,
                                       content_id: str,
                                       suspected_content_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Monitor for copyright violations of registered content
        
        Args:
            content_id: Registered content identifier
            suspected_content_list: List of suspected infringing content
            
        Returns:
            Violation monitoring report
        """
        try:
            if content_id not in self._content_registry:
                return {
                    'success': False,
                    'error': 'Content not registered'
                }
            
            registration = self._content_registry[content_id]
            
            # Detect violations
            violation_results = []
            for suspected_item in suspected_content_list:
                detection_result = await self.copyright_detector.detect_violations(
                    suspected_item['content'],
                    suspected_item['content_type'],
                    suspected_item.get('platform_info')
                )
                
                # Filter matches for this specific content
                relevant_matches = [
                    match for match in detection_result.matches
                    if match.original_content_id == content_id
                ]
                
                if relevant_matches:
                    violation_results.append({
                        'suspected_content_id': suspected_item.get('id', str(uuid.uuid4())),
                        'platform_info': suspected_item.get('platform_info'),
                        'matches': [asdict(match) for match in relevant_matches],
                        'violation_severity': self._calculate_violation_severity(relevant_matches)
                    })
            
            # Generate takedown notices if needed
            takedown_notices = []
            for violation in violation_results:
                if violation['violation_severity'] >= 0.8:  # High confidence violations
                    for match_data in violation['matches']:
                        # Reconstruct match object for notice generation
                        from .copyright_detector import CopyrightMatch
                        match = CopyrightMatch(**match_data)
                        
                        notice_result = await self.copyright_detector.generate_takedown_notice(
                            match,
                            {
                                'name': registration['owner_id'],
                                'email': 'rights@ainflue.com',
                                'content_id': content_id
                            }
                        )
                        
                        if notice_result['success']:
                            takedown_notices.append(notice_result)
            
            return {
                'success': True,
                'content_id': content_id,
                'violations_detected': len(violation_results),
                'violation_details': violation_results,
                'takedown_notices_generated': len(takedown_notices),
                'takedown_notices': takedown_notices,
                'monitoring_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Violation monitoring failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_protection_report(self, content_id: str) -> ProtectionReport:
        """
        Generate comprehensive protection report for content
        
        Args:
            content_id: Content identifier
            
        Returns:
            Detailed protection report
        """
        try:
            if content_id not in self._content_registry:
                raise ValueError("Content not registered")
            
            registration = self._content_registry[content_id]
            
            # Check watermark status
            watermark_status = {'enabled': False}
            if registration['watermark_id']:
                # Verify watermark integrity (would need original content)
                watermark_status = {
                    'enabled': True,
                    'watermark_id': registration['watermark_id'],
                    'status': 'active'
                }
            
            # Check blockchain status
            blockchain_status = {'registered': False}
            if registration['blockchain_tx']:
                rights_verification = await self.blockchain_registry.verify_rights(
                    registration['blockchain_tx'], content_id
                )
                blockchain_status = {
                    'registered': True,
                    'transaction_hash': registration['blockchain_tx'],
                    'verification_status': rights_verification
                }
            
            # Check NFT certificate status
            nft_status = {'issued': False}
            if registration['nft_certificate']:
                nft_verification = await self.nft_generator.verify_nft_certificate(
                    registration['nft_certificate']
                )
                nft_status = {
                    'issued': True,
                    'certificate_id': registration['nft_certificate'],
                    'verification_status': nft_verification
                }
            
            # Check for recent violations (placeholder)
            violations_detected = []
            
            # Generate recommendations
            recommendations = self._generate_protection_recommendations(registration)
            
            # Protection summary
            protection_summary = {
                'protection_level': registration['protection_level'],
                'rights_status': registration['rights_status'],
                'registration_date': registration['registration_timestamp'],
                'protection_score': self._calculate_protection_score(registration),
                'last_updated': datetime.now().isoformat()
            }
            
            return ProtectionReport(
                content_id=content_id,
                protection_summary=protection_summary,
                watermark_status=watermark_status,
                blockchain_status=blockchain_status,
                copyright_monitoring={'enabled': True, 'last_scan': datetime.now().isoformat()},
                nft_certificate_status=nft_status,
                violations_detected=violations_detected,
                recommendations=recommendations,
                report_timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Protection report generation failed: {e}")
            raise
    
    async def update_protection_level(self,
                                    content_id: str,
                                    new_protection_level: ProtectionLevel) -> Dict[str, Any]:
        """
        Update protection level for existing content
        
        Args:
            content_id: Content identifier
            new_protection_level: New protection level
            
        Returns:
            Update result
        """
        try:
            if content_id not in self._content_registry:
                return {
                    'success': False,
                    'error': 'Content not registered'
                }
            
            registration = self._content_registry[content_id]
            current_level = ProtectionLevel(registration['protection_level'])
            
            if current_level == new_protection_level:
                return {
                    'success': True,
                    'message': 'Protection level already at requested level'
                }
            
            # Update protection based on new level
            new_policy = self._protection_policies[new_protection_level]
            update_results = {}
            
            # Enable additional protections if upgrading
            if self._is_protection_upgrade(current_level, new_protection_level):
                # Add NFT certificate if not present and policy requires it
                if new_policy['enable_nft_certificates'] and not registration['nft_certificate']:
                    nft_result = await self.nft_generator.generate_copyright_certificate(
                        content_id,
                        registration['owner_id'],
                        registration['metadata']
                    )
                    
                    if nft_result.success:
                        registration['nft_certificate'] = nft_result.nft_id
                        update_results['nft_added'] = True
                
                # Enhanced blockchain registration if needed
                if new_policy['enable_blockchain'] and not registration['blockchain_tx']:
                    blockchain_result = await self.blockchain_registry.register_rights(
                        content_id,
                        registration['owner_id'],
                        RightsType.COPYRIGHT,
                        {
                            'upgrade_to': new_protection_level.value,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                    
                    if blockchain_result['success']:
                        registration['blockchain_tx'] = blockchain_result['blockchain_tx']
                        update_results['blockchain_enhanced'] = True
            
            # Update registration
            registration['protection_level'] = new_protection_level.value
            self._content_registry[content_id] = registration
            
            return {
                'success': True,
                'content_id': content_id,
                'previous_level': current_level.value,
                'new_level': new_protection_level.value,
                'updates_applied': update_results,
                'update_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Protection level update failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def batch_process_content(self,
                                  content_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process multiple content items in batch
        
        Args:
            content_batch: List of content items to process
            
        Returns:
            List of processing results
        """
        tasks = []
        
        for content_item in content_batch:
            task = self.register_content(
                content_item['content_data'],
                content_item['content_type'],
                content_item['owner_id'],
                ProtectionLevel(content_item.get('protection_level', 'standard')),
                content_item.get('metadata')
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                results[i] = {
                    'success': False,
                    'error': str(result),
                    'content_index': i
                }
        
        return results
    
    def _initialize_protection_policies(self):
        """Initialize protection policies for different levels"""
        self._protection_policies = {
            ProtectionLevel.BASIC: {
                'enable_watermarking': True,
                'watermark_strength': 0.3,
                'watermark_redundancy': 1,
                'enable_blockchain': False,
                'enable_copyright_detection': True,
                'enable_nft_certificates': False
            },
            ProtectionLevel.STANDARD: {
                'enable_watermarking': True,
                'watermark_strength': 0.5,
                'watermark_redundancy': 2,
                'enable_blockchain': True,
                'enable_copyright_detection': True,
                'enable_nft_certificates': False
            },
            ProtectionLevel.PREMIUM: {
                'enable_watermarking': True,
                'watermark_strength': 0.7,
                'watermark_redundancy': 3,
                'enable_blockchain': True,
                'enable_copyright_detection': True,
                'enable_nft_certificates': True
            },
            ProtectionLevel.ENTERPRISE: {
                'enable_watermarking': True,
                'watermark_strength': 0.9,
                'watermark_redundancy': 5,
                'enable_blockchain': True,
                'enable_copyright_detection': True,
                'enable_nft_certificates': True
            }
        }
    
    def _calculate_violation_severity(self, matches: List) -> float:
        """Calculate severity score for violations"""
        if not matches:
            return 0.0
        
        # Average confidence weighted by violation type
        type_weights = {
            ViolationType.EXACT_MATCH: 1.0,
            ViolationType.PARTIAL_MATCH: 0.8,
            ViolationType.DERIVATIVE_WORK: 0.6,
            ViolationType.UNAUTHORIZED_USE: 0.4
        }
        
        total_score = 0.0
        for match in matches:
            weight = type_weights.get(match.violation_type, 0.5)
            total_score += match.confidence * weight
        
        return min(total_score / len(matches), 1.0)
    
    def _calculate_protection_score(self, registration: Dict[str, Any]) -> float:
        """Calculate overall protection score"""
        score = 0.0
        
        if registration.get('watermark_id'):
            score += 25
        if registration.get('blockchain_tx'):
            score += 35
        if registration.get('nft_certificate'):
            score += 25
        
        # Add score based on protection level
        level_scores = {
            'basic': 5,
            'standard': 10,
            'premium': 15,
            'enterprise': 15
        }
        score += level_scores.get(registration['protection_level'], 0)
        
        return min(score, 100)
    
    def _generate_protection_recommendations(self, registration: Dict[str, Any]) -> List[str]:
        """Generate protection recommendations"""
        recommendations = []
        
        if not registration.get('watermark_id'):
            recommendations.append("Consider adding watermarking for content authentication")
        
        if not registration.get('blockchain_tx'):
            recommendations.append("Enable blockchain registration for immutable ownership records")
        
        if not registration.get('nft_certificate'):
            recommendations.append("Generate NFT certificate for enhanced legal protection")
        
        if registration['protection_level'] == 'basic':
            recommendations.append("Upgrade to Standard protection for enhanced security")
        
        return recommendations
    
    def _is_protection_upgrade(self, current: ProtectionLevel, new: ProtectionLevel) -> bool:
        """Check if new level is an upgrade"""
        levels = [ProtectionLevel.BASIC, ProtectionLevel.STANDARD, 
                 ProtectionLevel.PREMIUM, ProtectionLevel.ENTERPRISE]
        
        return levels.index(new) > levels.index(current)
    
    def get_content_registration(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get content registration by ID"""
        return self._content_registry.get(content_id)
    
    def list_content_by_owner(self, owner_id: str) -> List[Dict[str, Any]]:
        """List all content registered by a specific owner"""
        return [
            registration for registration in self._content_registry.values()
            if registration['owner_id'] == owner_id
        ]
    
    def get_protection_statistics(self) -> Dict[str, Any]:
        """Get overall protection statistics"""
        total_content = len(self._content_registry)
        
        if total_content == 0:
            return {
                'total_content': 0,
                'protection_levels': {},
                'protection_features': {}
            }
        
        # Count by protection level
        level_counts = {}
        watermarked = 0
        blockchain_registered = 0
        nft_certified = 0
        
        for registration in self._content_registry.values():
            level = registration['protection_level']
            level_counts[level] = level_counts.get(level, 0) + 1
            
            if registration.get('watermark_id'):
                watermarked += 1
            if registration.get('blockchain_tx'):
                blockchain_registered += 1
            if registration.get('nft_certificate'):
                nft_certified += 1
        
        return {
            'total_content': total_content,
            'protection_levels': level_counts,
            'protection_features': {
                'watermarked': watermarked,
                'blockchain_registered': blockchain_registered,
                'nft_certified': nft_certified
            },
            'coverage_percentages': {
                'watermarking': (watermarked / total_content) * 100,
                'blockchain': (blockchain_registered / total_content) * 100,
                'nft_certificates': (nft_certified / total_content) * 100
            }
        }