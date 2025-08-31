"""Rights Manager - Advanced Content Rights Management
==================================================

Industrial-grade content rights management system for multi-format content protection.
Handles licensing, ownership verification, and automated rights enforcement.

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: © 2025 Fahed Mlaiel - All Rights Reserved

⚠️  AVERTISSEMENT STRICT - PROPRIÉTÉ INTELLECTUELLE ⚠️
Ce code est la propriété exclusive de Fahed Mlaiel (mlaiel@live.de).
Toute utilisation, reproduction, modification ou distribution sans autorisation 
écrite explicite de l'auteur est strictement interdite et constitue une violation 
du droit d'auteur. Les contrevenants s'exposent à des poursuites judiciaires.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid
import json
import hashlib

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, update
from redis import Redis


class RightsType(Enum):
    """Content rights types"""    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    DERIVATIVE = "derivative"
    COMMERCIAL = "commercial"
    PERSONAL = "personal"
    CREATIVE_COMMONS = "creative_commons"


class LicenseStatus(Enum):
    """License status enumeration"""    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class RightsTransferType(Enum):
    """Rights transfer types"""    PERMANENT = "permanent"
    TEMPORARY = "temporary"
    SUBLICENSE = "sublicense"
    ASSIGNMENT = "assignment"


@dataclass
class RightsOwnership:
    """Content rights ownership record"""    ownership_id: str
    content_id: str
    owner_id: str
    rights_type: RightsType
    percentage: float
    valid_from: datetime
    valid_until: Optional[datetime]
    territory: List[str]
    media_types: List[str]
    exclusivity: bool
    transferable: bool


@dataclass
class LicenseAgreement:
    """Content license agreement"""    license_id: str
    content_id: str
    licensor_id: str
    licensee_id: str
    rights_type: RightsType
    usage_scope: List[str]
    territory: List[str]
    duration: int
    royalty_rate: float
    minimum_guarantee: float
    status: LicenseStatus
    signed_date: datetime
    start_date: datetime
    end_date: datetime
    auto_renewal: bool


@dataclass
class RightsVerification:
    """Rights verification result"""    verification_id: str
    content_id: str
    requester_id: str
    verification_type: str
    result: bool
    confidence_score: float
    evidence: Dict[str, Any]
    verified_at: datetime
    valid_until: datetime


class RightsManager:
    """    Professional content rights management system.
    
    Manages ownership verification, licensing agreements, and automated
    rights enforcement for multi-format content across platforms.
    """    
    def __init__(self, db_session: AsyncSession, redis_client: Redis):
        """        Initialize RightsManager.
        
        Args:
            db_session: Async database session
            redis_client: Redis client for caching
        """        self.db_session = db_session
        self.redis = redis_client
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.cache_ttl = 3600  # 1 hour
        self.verification_validity = 86400  # 24 hours
        
        # Rights validation thresholds
        self.min_ownership_percentage = 1.0
        self.max_total_ownership = 100.0
        self.license_grace_period = 7  # days
    
    async def register_ownership(self, content_id: str, owner_id: str,
                               rights_data: Dict[str, Any]) -> str:
        """        Register content ownership rights.
        
        Args:
            content_id: Content identifier
            owner_id: Owner user identifier
            rights_data: Rights registration data
            
        Returns:
            Ownership registration ID
        """        try:
            # Validate ownership percentage
            current_ownership = await self._get_total_ownership_percentage(content_id)
            new_percentage = rights_data.get('percentage', 100.0)
            
            if current_ownership + new_percentage > self.max_total_ownership:
                raise ValueError(f"Total ownership cannot exceed {self.max_total_ownership}%")
            
            # Create ownership record
            ownership_id = str(uuid.uuid4())
            ownership = RightsOwnership(
                ownership_id=ownership_id,
                content_id=content_id,
                owner_id=owner_id,
                rights_type=RightsType(rights_data.get('rights_type', 'exclusive')),
                percentage=new_percentage,
                valid_from=datetime.utcnow(),
                valid_until=rights_data.get('valid_until'),
                territory=rights_data.get('territory', ['WORLDWIDE']),
                media_types=rights_data.get('media_types', ['ALL']),
                exclusivity=rights_data.get('exclusivity', True),
                transferable=rights_data.get('transferable', True)
            )
            
            # Store in database
            await self._store_ownership_record(ownership)
            
            # Generate ownership certificate hash
            certificate_hash = await self._generate_ownership_certificate(ownership)
            
            # Cache ownership data
            await self._cache_ownership_data(content_id, owner_id, ownership)
            
            self.logger.info(f"Ownership registered: {ownership_id} for content {content_id}")
            return ownership_id
            
        except Exception as e:
            self.logger.error(f"Error registering ownership: {str(e)}")
            raise
    
    async def verify_rights(self, content_id: str, requester_id: str,
                          verification_type: str = "usage") -> RightsVerification:
        """        Verify content usage rights for a user.
        
        Args:
            content_id: Content identifier
            requester_id: User requesting verification
            verification_type: Type of verification (usage, licensing, transfer)
            
        Returns:
            Rights verification result
        """        try:
            verification_id = str(uuid.uuid4())
            
            # Check direct ownership
            ownership_rights = await self._check_direct_ownership(content_id, requester_id)
            
            # Check licensing agreements
            license_rights = await self._check_license_agreements(content_id, requester_id)
            
            # Check derivative rights
            derivative_rights = await self._check_derivative_rights(content_id, requester_id)
            
            # Calculate overall rights score
            rights_score = await self._calculate_rights_score(
                ownership_rights, license_rights, derivative_rights
            )
            
            # Determine verification result
            has_rights = rights_score >= 0.7  # 70% confidence threshold
            
            # Compile evidence
            evidence = {
                'ownership_rights': ownership_rights,
                'license_rights': license_rights,
                'derivative_rights': derivative_rights,
                'verification_method': verification_type,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            verification = RightsVerification(
                verification_id=verification_id,
                content_id=content_id,
                requester_id=requester_id,
                verification_type=verification_type,
                result=has_rights,
                confidence_score=rights_score,
                evidence=evidence,
                verified_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(seconds=self.verification_validity)
            )
            
            # Store verification result
            await self._store_verification_result(verification)
            
            # Cache verification
            await self._cache_verification_result(verification)
            
            self.logger.info(f"Rights verified for {requester_id} on content {content_id}: {has_rights}")
            return verification
            
        except Exception as e:
            self.logger.error(f"Error verifying rights: {str(e)}")
            raise
    
    async def create_license_agreement(self, license_data: Dict[str, Any]) -> str:
        """        Create new license agreement.
        
        Args:
            license_data: License agreement data
            
        Returns:
            License agreement ID
        """        try:
            # Validate licensor rights
            licensor_verification = await self.verify_rights(
                license_data['content_id'], 
                license_data['licensor_id'],
                'licensing'
            )
            
            if not licensor_verification.result:
                raise ValueError("Licensor does not have sufficient rights to license content")
            
            # Create license agreement
            license_id = str(uuid.uuid4())
            agreement = LicenseAgreement(
                license_id=license_id,
                content_id=license_data['content_id'],
                licensor_id=license_data['licensor_id'],
                licensee_id=license_data['licensee_id'],
                rights_type=RightsType(license_data.get('rights_type', 'non_exclusive')),
                usage_scope=license_data.get('usage_scope', ['COMMERCIAL']),
                territory=license_data.get('territory', ['WORLDWIDE']),
                duration=license_data.get('duration', 365),  # days
                royalty_rate=license_data.get('royalty_rate', 0.0),
                minimum_guarantee=license_data.get('minimum_guarantee', 0.0),
                status=LicenseStatus.PENDING,
                signed_date=datetime.utcnow(),
                start_date=datetime.fromisoformat(license_data.get('start_date', datetime.utcnow().isoformat())),
                end_date=datetime.fromisoformat(license_data.get('end_date', (datetime.utcnow() + timedelta(days=365)).isoformat())),
                auto_renewal=license_data.get('auto_renewal', False)
            )
            
            # Store agreement
            await self._store_license_agreement(agreement)
            
            # Generate license contract hash
            contract_hash = await self._generate_license_hash(agreement)
            
            # Send notifications
            await self._send_license_notifications(agreement)
            
            self.logger.info(f"License agreement created: {license_id}")
            return license_id
            
        except Exception as e:
            self.logger.error(f"Error creating license agreement: {str(e)}")
            raise
    
    async def transfer_rights(self, transfer_data: Dict[str, Any]) -> bool:
        """        Transfer content rights between users.
        
        Args:
            transfer_data: Rights transfer data
            
        Returns:
            Transfer success status
        """        try:
            # Verify transferor rights
            transferor_verification = await self.verify_rights(
                transfer_data['content_id'],
                transfer_data['from_user_id'],
                'transfer'
            )
            
            if not transferor_verification.result:
                raise ValueError("Transferor does not have rights to transfer")
            
            # Get current ownership
            current_ownership = await self._get_ownership_record(
                transfer_data['content_id'],
                transfer_data['from_user_id']
            )
            
            if not current_ownership or not current_ownership.transferable:
                raise ValueError("Rights are not transferable")
            
            # Calculate transfer percentage
            transfer_percentage = transfer_data.get('percentage', current_ownership.percentage)
            
            if transfer_percentage > current_ownership.percentage:
                raise ValueError("Cannot transfer more rights than owned")
            
            # Create new ownership record for transferee
            new_ownership_id = await self.register_ownership(
                transfer_data['content_id'],
                transfer_data['to_user_id'],
                {
                    'rights_type': current_ownership.rights_type.value,
                    'percentage': transfer_percentage,
                    'territory': current_ownership.territory,
                    'media_types': current_ownership.media_types,
                    'exclusivity': current_ownership.exclusivity,
                    'transferable': current_ownership.transferable
                }
            )
            
            # Update or remove transferor ownership
            if transfer_percentage == current_ownership.percentage:
                # Complete transfer - remove old ownership
                await self._remove_ownership_record(current_ownership.ownership_id)
            else:
                # Partial transfer - update remaining percentage
                await self._update_ownership_percentage(
                    current_ownership.ownership_id,
                    current_ownership.percentage - transfer_percentage
                )
            
            # Record transfer transaction
            transfer_id = await self._record_rights_transfer(transfer_data, new_ownership_id)
            
            # Clear ownership cache
            await self._clear_ownership_cache(transfer_data['content_id'])
            
            self.logger.info(f"Rights transferred: {transfer_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error transferring rights: {str(e)}")
            await self.db_session.rollback()
            return False
    
    async def get_ownership_chain(self, content_id: str) -> List[Dict[str, Any]]:
        """        Get complete ownership chain for content.
        
        Args:
            content_id: Content identifier
            
        Returns:
            List of ownership records
        """        try:
            # Get current ownership records
            ownership_records = await self._get_all_ownership_records(content_id)
            
            # Get ownership history
            ownership_history = await self._get_ownership_history(content_id)
            
            # Get license agreements
            license_agreements = await self._get_license_agreements(content_id)
            
            # Build comprehensive ownership chain
            ownership_chain = []
            
            for record in ownership_records:
                chain_entry = {
                    'ownership_id': record.ownership_id,
                    'owner_id': record.owner_id,
                    'rights_type': record.rights_type.value,
                    'percentage': record.percentage,
                    'valid_from': record.valid_from.isoformat(),
                    'valid_until': record.valid_until.isoformat() if record.valid_until else None,
                    'territory': record.territory,
                    'media_types': record.media_types,
                    'exclusivity': record.exclusivity,
                    'transferable': record.transferable,
                    'status': 'active'
                }
                ownership_chain.append(chain_entry)
            
            # Add license information
            for license_agreement in license_agreements:
                if license_agreement.status == LicenseStatus.ACTIVE:
                    chain_entry = {
                        'license_id': license_agreement.license_id,
                        'licensee_id': license_agreement.licensee_id,
                        'rights_type': license_agreement.rights_type.value,
                        'usage_scope': license_agreement.usage_scope,
                        'territory': license_agreement.territory,
                        'valid_from': license_agreement.start_date.isoformat(),
                        'valid_until': license_agreement.end_date.isoformat(),
                        'royalty_rate': license_agreement.royalty_rate,
                        'status': 'licensed'
                    }
                    ownership_chain.append(chain_entry)
            
            return ownership_chain
            
        except Exception as e:
            self.logger.error(f"Error getting ownership chain: {str(e)}")
            return []
    
    async def revoke_license(self, license_id: str, reason: str) -> bool:
        """        Revoke active license agreement.
        
        Args:
            license_id: License agreement ID
            reason: Revocation reason
            
        Returns:
            Revocation success status
        """        try:
            # Get license agreement
            agreement = await self._get_license_agreement(license_id)
            if not agreement:
                return False
            
            # Update license status
            agreement.status = LicenseStatus.REVOKED
            await self._update_license_status(license_id, LicenseStatus.REVOKED, reason)
            
            # Clear licensing cache
            await self._clear_license_cache(agreement.content_id, agreement.licensee_id)
            
            # Send revocation notifications
            await self._send_revocation_notifications(agreement, reason)
            
            self.logger.info(f"License revoked: {license_id} - {reason}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error revoking license: {str(e)}")
            return False
    
    # Private helper methods
    
    async def _get_total_ownership_percentage(self, content_id: str) -> float:
        """Get total ownership percentage for content"""        # Implementation would query database for total ownership
        return 0.0  # Placeholder
    
    async def _store_ownership_record(self, ownership: RightsOwnership):
        """Store ownership record in database"""        # Implementation would store in database
        pass
    
    async def _generate_ownership_certificate(self, ownership: RightsOwnership) -> str:
        """Generate cryptographic ownership certificate"""        certificate_data = {
            'ownership_id': ownership.ownership_id,
            'content_id': ownership.content_id,
            'owner_id': ownership.owner_id,
            'rights_type': ownership.rights_type.value,
            'percentage': ownership.percentage,
            'timestamp': ownership.valid_from.isoformat()
        }
        
        certificate_string = json.dumps(certificate_data, sort_keys=True)
        return hashlib.sha256(certificate_string.encode()).hexdigest()
    
    async def _cache_ownership_data(self, content_id: str, owner_id: str, ownership: RightsOwnership):
        """Cache ownership data in Redis"""        cache_key = f"ownership:{content_id}:{owner_id}"
        ownership_data = {
            'ownership_id': ownership.ownership_id,
            'rights_type': ownership.rights_type.value,
            'percentage': ownership.percentage,
            'territory': ownership.territory,
            'exclusivity': ownership.exclusivity
        }
        
        await self.redis.setex(
            cache_key, 
            self.cache_ttl, 
            json.dumps(ownership_data, default=str)
        )
    
    async def _check_direct_ownership(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Check direct ownership rights"""        # Check cache first
        cache_key = f"ownership:{content_id}:{user_id}"
        cached_ownership = await self.redis.get(cache_key)
        
        if cached_ownership:
            return json.loads(cached_ownership)
        
        # Query database for ownership
        ownership_record = await self._get_ownership_record(content_id, user_id)
        
        if ownership_record:
            return {
                'has_ownership': True,
                'percentage': ownership_record.percentage,
                'rights_type': ownership_record.rights_type.value,
                'exclusivity': ownership_record.exclusivity
            }
        
        return {'has_ownership': False, 'percentage': 0.0}
    
    async def _check_license_agreements(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Check active license agreements"""        # Implementation would query active licenses
        return {'has_license': False, 'scope': []}
    
    async def _check_derivative_rights(self, content_id: str, user_id: str) -> Dict[str, Any]:
        """Check derivative work rights"""        # Implementation would check for derivative rights
        return {'has_derivative': False, 'source_content': None}
    
    async def _calculate_rights_score(self, ownership: Dict, license: Dict, derivative: Dict) -> float:
        """Calculate overall rights confidence score"""        score = 0.0
        
        # Ownership carries highest weight
        if ownership.get('has_ownership'):
            score += ownership.get('percentage', 0) / 100.0 * 0.8
        
        # License agreements
        if license.get('has_license'):
            score += 0.6
        
        # Derivative rights
        if derivative.get('has_derivative'):
            score += 0.4
        
        return min(score, 1.0)
    
    async def _store_verification_result(self, verification: RightsVerification):
        """Store verification result in database"""        # Implementation would store verification
        pass
    
    async def _cache_verification_result(self, verification: RightsVerification):
        """Cache verification result"""        cache_key = f"verification:{verification.content_id}:{verification.requester_id}"
        verification_data = {
            'result': verification.result,
            'confidence_score': verification.confidence_score,
            'valid_until': verification.valid_until.isoformat()
        }
        
        await self.redis.setex(
            cache_key,
            self.verification_validity,
            json.dumps(verification_data, default=str)
        )
    
    async def _store_license_agreement(self, agreement: LicenseAgreement):
        """Store license agreement in database"""        # Implementation would store license
        pass
    
    async def _generate_license_hash(self, agreement: LicenseAgreement) -> str:
        """Generate license agreement hash"""        license_data = {
            'license_id': agreement.license_id,
            'content_id': agreement.content_id,
            'licensor_id': agreement.licensor_id,
            'licensee_id': agreement.licensee_id,
            'signed_date': agreement.signed_date.isoformat()
        }
        
        license_string = json.dumps(license_data, sort_keys=True)
        return hashlib.sha256(license_string.encode()).hexdigest()
    
    async def _send_license_notifications(self, agreement: LicenseAgreement):
        """Send license agreement notifications"""        # Implementation would send notifications
        pass
    
    async def _get_ownership_record(self, content_id: str, user_id: str) -> Optional[RightsOwnership]:
        """Get ownership record from database"""        # Implementation would query database
        return None
    
    async def _remove_ownership_record(self, ownership_id: str):
        """Remove ownership record"""        # Implementation would remove from database
        pass
    
    async def _update_ownership_percentage(self, ownership_id: str, new_percentage: float):
        """Update ownership percentage"""        # Implementation would update database
        pass
    
    async def _record_rights_transfer(self, transfer_data: Dict, new_ownership_id: str) -> str:
        """Record rights transfer transaction"""        transfer_id = str(uuid.uuid4())
        # Implementation would record transfer
        return transfer_id
    
    async def _clear_ownership_cache(self, content_id: str):
        """Clear ownership cache for content"""        pattern = f"ownership:{content_id}:*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
    
    async def _get_all_ownership_records(self, content_id: str) -> List[RightsOwnership]:
        """Get all ownership records for content"""        # Implementation would query all ownership records
        return []
    
    async def _get_ownership_history(self, content_id: str) -> List[Dict]:
        """Get ownership transfer history"""        # Implementation would query transfer history
        return []
    
    async def _get_license_agreements(self, content_id: str) -> List[LicenseAgreement]:
        """Get license agreements for content"""        # Implementation would query license agreements
        return []
    
    async def _get_license_agreement(self, license_id: str) -> Optional[LicenseAgreement]:
        """Get specific license agreement"""        # Implementation would query specific license
        return None
    
    async def _update_license_status(self, license_id: str, status: LicenseStatus, reason: str):
        """Update license status in database"""        # Implementation would update license status
        pass
    
    async def _clear_license_cache(self, content_id: str, licensee_id: str):
        """Clear license cache"""        cache_key = f"license:{content_id}:{licensee_id}"
        await self.redis.delete(cache_key)
    
    async def _send_revocation_notifications(self, agreement: LicenseAgreement, reason: str):
        """Send license revocation notifications"""        # Implementation would send notifications
        pass
