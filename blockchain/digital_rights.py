"""
Advanced Digital Rights Management for IA Influencer Agent Platform
Blockchain-based content protection and usage rights enforcement

Author: Fahed Mlaiel <mlaiel@live.de>
WARNING: This code is protected by copyright. Any unauthorized use, reproduction,
or distribution without written permission from Fahed Mlaiel is strictly prohibited.
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import uuid
from cryptography.fernet import Fernet

from ..core.exceptions import DRMError, BlockchainError
from ..security.encryption import EncryptionManager
from .transaction_manager import TransactionManager
from .smart_contracts import SmartContractManager
from .copyright_registry import CopyrightRegistryManager, CopyrightAsset


class UsageRights(Enum):
    """Digital content usage rights"""
    VIEW_ONLY = "view_only"
    DOWNLOAD = "download"
    STREAM = "stream"
    REMIX = "remix"
    COMMERCIAL_USE = "commercial_use"
    DISTRIBUTION = "distribution"
    MODIFICATION = "modification"
    PUBLIC_PERFORMANCE = "public_performance"
    SYNCHRONIZATION = "synchronization"
    COLLABORATION = "collaboration"


class AccessLevel(Enum):
    """Content access levels"""
    PUBLIC = "public"
    PREMIUM = "premium"
    EXCLUSIVE = "exclusive"
    PRIVATE = "private"
    ENTERPRISE = "enterprise"


class LicenseType(Enum):
    """Digital license types"""
    SINGLE_USE = "single_use"
    LIMITED_TIME = "limited_time"
    UNLIMITED = "unlimited"
    SUBSCRIPTION = "subscription"
    REVENUE_SHARE = "revenue_share"
    EXCLUSIVE_LICENSE = "exclusive_license"
    NON_EXCLUSIVE = "non_exclusive"
    CREATIVE_COMMONS = "creative_commons"


@dataclass
class DigitalLicense:
    """Digital rights license representation"""
    license_id: str
    asset_id: str
    licensor_id: str
    licensee_id: str
    license_type: LicenseType
    usage_rights: Set[UsageRights]
    access_level: AccessLevel
    start_date: datetime
    end_date: Optional[datetime]
    usage_limit: Optional[int]
    current_usage: int
    territory_restrictions: Optional[List[str]]
    platform_restrictions: Optional[List[str]]
    revenue_share_percentage: Optional[float]
    price: Optional[float]
    currency: str
    blockchain_tx_id: Optional[str]
    smart_contract_address: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


@dataclass
class UsageEvent:
    """Content usage tracking event"""
    event_id: str
    license_id: str
    asset_id: str
    user_id: str
    usage_type: UsageRights
    platform: str
    location: Optional[str]
    timestamp: datetime
    session_duration: Optional[int]
    revenue_generated: Optional[float]
    metadata: Dict[str, Any]


@dataclass
class ProtectionPolicy:
    """Content protection policy"""
    policy_id: str
    asset_id: str
    creator_id: str
    watermarking_enabled: bool
    drm_protection: bool
    geographical_blocking: List[str]
    platform_restrictions: List[str]
    download_prevention: bool
    screenshot_blocking: bool
    copy_protection: bool
    forensic_watermarking: bool
    real_time_monitoring: bool
    automated_takedown: bool
    violation_penalties: Dict[str, Any]
    created_at: datetime


class DRMManager:
    """
    Advanced Digital Rights Management system
    Manages content protection, licensing, and usage enforcement
    """
    
    def __init__(self, transaction_manager: TransactionManager,
                 smart_contract_manager: SmartContractManager,
                 copyright_registry: CopyrightRegistryManager,
                 encryption_manager: EncryptionManager):
        self.transaction_manager = transaction_manager
        self.smart_contract_manager = smart_contract_manager
        self.copyright_registry = copyright_registry
        self.encryption_manager = encryption_manager
        self.logger = logging.getLogger(__name__)
        self._license_cache: Dict[str, DigitalLicense] = {}
        self._protection_policies: Dict[str, ProtectionPolicy] = {}
        self._usage_events: List[UsageEvent] = []
    
    async def create_digital_license(self, asset_id: str, licensor_id: str,
                                   licensee_id: str, license_config: Dict[str, Any]) -> DigitalLicense:
        """
        Create digital license for content usage
        
        Args:
            asset_id: Content asset identifier
            licensor_id: License grantor ID
            licensee_id: License recipient ID
            license_config: License configuration parameters
            
        Returns:
            DigitalLicense: Created digital license
            
        Raises:
            DRMError: If license creation fails
        """



        try:
            # Verify asset exists and ownership
            asset = await self.copyright_registry.get_copyright_asset(asset_id)
            if not asset:
                raise DRMError(f"Asset not found: {asset_id}")
            
            if asset.creator_id != licensor_id:
                raise DRMError("Only asset owner can grant licenses")
            
            # Generate license ID
            license_id = self._generate_license_id(asset_id, licensee_id)
            
            # Parse license configuration
            license_type = LicenseType(license_config.get('license_type', 'non_exclusive'))
            usage_rights = set(UsageRights(right) for right in license_config.get('usage_rights', []))
            access_level = AccessLevel(license_config.get('access_level', 'premium'))
            
            # Set license duration
            start_date = datetime.now(timezone.utc)
            duration_days = license_config.get('duration_days')
            end_date = start_date + timedelta(days=duration_days) if duration_days else None
            
            # Create license object
            license_obj = DigitalLicense(
                license_id=license_id,
                asset_id=asset_id,
                licensor_id=licensor_id,
                licensee_id=licensee_id,
                license_type=license_type,
                usage_rights=usage_rights,
                access_level=access_level,
                start_date=start_date,
                end_date=end_date,
                usage_limit=license_config.get('usage_limit'),
                current_usage=0,
                territory_restrictions=license_config.get('territory_restrictions'),
                platform_restrictions=license_config.get('platform_restrictions'),
                revenue_share_percentage=license_config.get('revenue_share_percentage'),
                price=license_config.get('price'),
                currency=license_config.get('currency', 'USD'),
                metadata=license_config.get('metadata', {}),
                created_at=start_date,
                updated_at=start_date
            )
            
            # Deploy license smart contract
            contract_address = await self.smart_contract_manager.deploy_license_contract(
                license_id=license_id,
                asset_id=asset_id,
                licensor=licensor_id,
                licensee=licensee_id,
                terms=asdict(license_obj)
            )
            
            license_obj.smart_contract_address = contract_address
            
            # Record license transaction
            tx_id = await self.transaction_manager.create_license_transaction(
                asset_id=asset_id,
                licensor=licensor_id,
                licensee=licensee_id,
                contract_address=contract_address,
                terms=asdict(license_obj)
            )
            
            license_obj.blockchain_tx_id = tx_id
            
            # Cache license
            self._license_cache[license_id] = license_obj
            
            self.logger.info(f"Digital license created: {license_id}")
            return license_obj
            
        except Exception as e:
            self.logger.error(f"License creation failed: {str(e)}")
            raise DRMError(f"Failed to create digital license: {str(e)}")
    
    async def validate_usage_rights(self, license_id: str, usage_type: UsageRights,
                                  user_id: str, platform: str = None,
                                  location: str = None) -> Tuple[bool, Optional[str]]:
        """
        Validate content usage rights
        
        Args:
            license_id: License identifier
            usage_type: Requested usage type
            user_id: User requesting access
            platform: Platform where content will be used
            location: User location for geo-restrictions
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """



        try:
            # Get license
            license_obj = await self.get_digital_license(license_id)
            if not license_obj:
                return False, "License not found"
            
            # Verify licensee
            if license_obj.licensee_id != user_id:
                return False, "Unauthorized user"
            
            # Check license validity period
            now = datetime.now(timezone.utc)
            if now < license_obj.start_date:
                return False, "License not yet active"
            
            if license_obj.end_date and now > license_obj.end_date:
                return False, "License expired"
            
            # Check usage rights
            if usage_type not in license_obj.usage_rights:
                return False, f"Usage type '{usage_type.value}' not permitted"
            
            # Check usage limit
            if (license_obj.usage_limit and 
                license_obj.current_usage >= license_obj.usage_limit):
                return False, "Usage limit exceeded"
            
            # Check territory restrictions
            if (license_obj.territory_restrictions and location and
                location not in license_obj.territory_restrictions):
                return False, f"Usage not permitted in {location}"
            
            # Check platform restrictions
            if (license_obj.platform_restrictions and platform and
                platform not in license_obj.platform_restrictions):
                return False, f"Usage not permitted on {platform}"
            
            return True, None
            
        except Exception as e:
            self.logger.error(f"Usage rights validation failed: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    async def record_usage_event(self, license_id: str, user_id: str,
                               usage_type: UsageRights, platform: str,
                               session_data: Dict[str, Any]) -> UsageEvent:
        """
        Record content usage event for tracking and billing
        
        Args:
            license_id: License identifier
            user_id: User ID
            usage_type: Type of usage
            platform: Platform used
            session_data: Usage session data
            
        Returns:
            UsageEvent: Recorded usage event
        """



        try:
            # Get license to verify asset
            license_obj = await self.get_digital_license(license_id)
            if not license_obj:
                raise DRMError("License not found")
            
            # Create usage event
            event = UsageEvent(
                event_id=str(uuid.uuid4()),
                license_id=license_id,
                asset_id=license_obj.asset_id,
                user_id=user_id,
                usage_type=usage_type,
                platform=platform,
                location=session_data.get('location'),
                timestamp=datetime.now(timezone.utc),
                session_duration=session_data.get('duration_seconds'),
                revenue_generated=session_data.get('revenue'),
                metadata=session_data.get('metadata', {})
            )
            
            # Update license usage count
            license_obj.current_usage += 1
            license_obj.updated_at = event.timestamp
            self._license_cache[license_id] = license_obj
            
            # Record usage on blockchain
            await self.transaction_manager.create_usage_transaction(
                license_id=license_id,
                user_id=user_id,
                usage_type=usage_type.value,
                platform=platform,
                event_data=asdict(event)
            )
            
            # Store usage event
            self._usage_events.append(event)
            
            # Update smart contract state
            await self.smart_contract_manager.update_license_usage(
                contract_address=license_obj.smart_contract_address,
                usage_count=license_obj.current_usage,
                last_usage=event.timestamp
            )
            
            self.logger.info(f"Usage event recorded: {event.event_id}")
            return event
            
        except Exception as e:
            self.logger.error(f"Failed to record usage event: {str(e)}")
            raise DRMError(f"Usage recording failed: {str(e)}")
    
    async def create_protection_policy(self, asset_id: str, creator_id: str,
                                     policy_config: Dict[str, Any]) -> ProtectionPolicy:
        """
        Create content protection policy
        
        Args:
            asset_id: Asset to protect
            creator_id: Asset owner ID
            policy_config: Protection configuration
            
        Returns:
            ProtectionPolicy: Created protection policy
        """



        try:
            # Verify asset ownership
            asset = await self.copyright_registry.get_copyright_asset(asset_id)
            if not asset or asset.creator_id != creator_id:
                raise DRMError("Unauthorized to create protection policy")
            
            # Create protection policy
            policy = ProtectionPolicy(
                policy_id=f"policy_{asset_id}_{int(datetime.now().timestamp())}",
                asset_id=asset_id,
                creator_id=creator_id,
                watermarking_enabled=policy_config.get('watermarking_enabled', True),
                drm_protection=policy_config.get('drm_protection', True),
                geographical_blocking=policy_config.get('geographical_blocking', []),
                platform_restrictions=policy_config.get('platform_restrictions', []),
                download_prevention=policy_config.get('download_prevention', False),
                screenshot_blocking=policy_config.get('screenshot_blocking', False),
                copy_protection=policy_config.get('copy_protection', True),
                forensic_watermarking=policy_config.get('forensic_watermarking', False),
                real_time_monitoring=policy_config.get('real_time_monitoring', True),
                automated_takedown=policy_config.get('automated_takedown', False),
                violation_penalties=policy_config.get('violation_penalties', {}),
                created_at=datetime.now(timezone.utc)
            )
            
            # Deploy protection smart contract
            await self.smart_contract_manager.deploy_protection_contract(
                asset_id=asset_id,
                creator_id=creator_id,
                policy=asdict(policy)
            )
            
            # Cache policy
            self._protection_policies[asset_id] = policy
            
            self.logger.info(f"Protection policy created: {policy.policy_id}")
            return policy
            
        except Exception as e:
            self.logger.error(f"Protection policy creation failed: {str(e)}")
            raise DRMError(f"Failed to create protection policy: {str(e)}")
    
    async def get_digital_license(self, license_id: str) -> Optional[DigitalLicense]:
        """
        Retrieve digital license
        
        Args:
            license_id: License identifier
            
        Returns:
            Optional[DigitalLicense]: License if found
        """



        try:
            # Check cache first
            if license_id in self._license_cache:
                return self._license_cache[license_id]
            
            # Query blockchain
            license_data = await self.smart_contract_manager.get_license_data(license_id)
            if not license_data:
                return None
            
            # Reconstruct license from blockchain data
            license_obj = self._reconstruct_license_from_blockchain(license_data)
            self._license_cache[license_id] = license_obj
            
            return license_obj
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve license {license_id}: {str(e)}")
            return None
    
    async def get_user_licenses(self, user_id: str, active_only: bool = True) -> List[DigitalLicense]:
        """
        Get all licenses for a user
        
        Args:
            user_id: User identifier
            active_only: Only return active licenses
            
        Returns:
            List[DigitalLicense]: User's licenses
        """



        try:
            license_ids = await self.smart_contract_manager.get_user_licenses(user_id)
            licenses = []
            
            for license_id in license_ids:
                license_obj = await self.get_digital_license(license_id)
                if license_obj:
                    if active_only:
                        now = datetime.now(timezone.utc)
                        if (now >= license_obj.start_date and 
                            (not license_obj.end_date or now <= license_obj.end_date)):
                            licenses.append(license_obj)
                    else:
                        licenses.append(license_obj)
            
            return licenses
            
        except Exception as e:
            self.logger.error(f"Failed to get user licenses: {str(e)}")
            return []
    
    async def revoke_license(self, license_id: str, revoker_id: str,
                           reason: str) -> bool:
        """
        Revoke digital license
        
        Args:
            license_id: License to revoke
            revoker_id: User revoking the license
            reason: Revocation reason
            
        Returns:
            bool: True if revocation successful
        """



        try:
            license_obj = await self.get_digital_license(license_id)
            if not license_obj:
                raise DRMError("License not found")
            
            # Verify authorization to revoke
            if revoker_id != license_obj.licensor_id:
                raise DRMError("Only licensor can revoke license")
            
            # Update license end date to now
            license_obj.end_date = datetime.now(timezone.utc)
            license_obj.updated_at = license_obj.end_date
            
            # Update smart contract
            await self.smart_contract_manager.revoke_license(
                contract_address=license_obj.smart_contract_address,
                reason=reason
            )
            
            # Record revocation transaction
            await self.transaction_manager.create_revocation_transaction(
                license_id=license_id,
                revoker_id=revoker_id,
                reason=reason
            )
            
            # Update cache
            self._license_cache[license_id] = license_obj
            
            self.logger.info(f"License revoked: {license_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"License revocation failed: {str(e)}")
            return False
    
    async def generate_usage_report(self, asset_id: str = None,
                                  user_id: str = None,
                                  start_date: datetime = None,
                                  end_date: datetime = None) -> Dict[str, Any]:
        """
        Generate comprehensive usage analytics report
        
        Args:
            asset_id: Filter by asset ID
            user_id: Filter by user ID
            start_date: Report start date
            end_date: Report end date
            
        Returns:
            Dict[str, Any]: Usage analytics report
        """



        try:
            # Filter usage events
            filtered_events = self._filter_usage_events(
                asset_id, user_id, start_date, end_date
            )
            
            # Calculate analytics
            report = {
                'summary': {
                    'total_events': len(filtered_events),
                    'unique_users': len(set(event.user_id for event in filtered_events)),
                    'unique_assets': len(set(event.asset_id for event in filtered_events)),
                    'total_revenue': sum(event.revenue_generated or 0 for event in filtered_events),
                    'average_session_duration': self._calculate_average_duration(filtered_events)
                },
                'by_usage_type': {},
                'by_platform': {},
                'by_asset': {},
                'by_time': {},
                'revenue_breakdown': {}
            }
            
            # Analyze by usage type
            for event in filtered_events:
                usage_type = event.usage_type.value
                if usage_type not in report['by_usage_type']:
                    report['by_usage_type'][usage_type] = {
                        'count': 0,
                        'revenue': 0,
                        'unique_users': set()
                    }
                
                report['by_usage_type'][usage_type]['count'] += 1
                report['by_usage_type'][usage_type]['revenue'] += event.revenue_generated or 0
                report['by_usage_type'][usage_type]['unique_users'].add(event.user_id)
            
            # Convert sets to counts
            for usage_type in report['by_usage_type']:
                report['by_usage_type'][usage_type]['unique_users'] = len(
                    report['by_usage_type'][usage_type]['unique_users']
                )
            
            # Analyze by platform
            for event in filtered_events:
                platform = event.platform
                if platform not in report['by_platform']:
                    report['by_platform'][platform] = {
                        'count': 0,
                        'revenue': 0
                    }
                
                report['by_platform'][platform]['count'] += 1
                report['by_platform'][platform]['revenue'] += event.revenue_generated or 0
            
            return report
            
        except Exception as e:
            self.logger.error(f"Usage report generation failed: {str(e)}")
            return {}
    
    def _generate_license_id(self, asset_id: str, licensee_id: str) -> str:
        """Generate unique license identifier"""
        timestamp = str(int(datetime.now().timestamp()))
        hash_input = f"{asset_id}_{licensee_id}_{timestamp}"
        hash_suffix = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"license_{hash_suffix}_{timestamp}"
    
    def _filter_usage_events(self, asset_id: str = None, user_id: str = None,
                           start_date: datetime = None, end_date: datetime = None) -> List[UsageEvent]:
        """Filter usage events by criteria"""
        filtered = self._usage_events
        
        if asset_id:
            filtered = [e for e in filtered if e.asset_id == asset_id]
        
        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]
        
        if start_date:
            filtered = [e for e in filtered if e.timestamp >= start_date]
        
        if end_date:
            filtered = [e for e in filtered if e.timestamp <= end_date]
        
        return filtered
    
    def _calculate_average_duration(self, events: List[UsageEvent]) -> Optional[float]:
        """Calculate average session duration"""
        durations = [e.session_duration for e in events if e.session_duration]
        return sum(durations) / len(durations) if durations else None
    
    def _reconstruct_license_from_blockchain(self, blockchain_data: Dict[str, Any]) -> DigitalLicense:
        """Reconstruct license object from blockchain data"""



        return DigitalLicense(
            license_id=blockchain_data['license_id'],
            asset_id=blockchain_data['asset_id'],
            licensor_id=blockchain_data['licensor_id'],
            licensee_id=blockchain_data['licensee_id'],
            license_type=LicenseType(blockchain_data['license_type']),
            usage_rights=set(UsageRights(right) for right in blockchain_data['usage_rights']),
            access_level=AccessLevel(blockchain_data['access_level']),
            start_date=datetime.fromisoformat(blockchain_data['start_date']),
            end_date=datetime.fromisoformat(blockchain_data['end_date']) if blockchain_data.get('end_date') else None,
            usage_limit=blockchain_data.get('usage_limit'),
            current_usage=blockchain_data.get('current_usage', 0),
            territory_restrictions=blockchain_data.get('territory_restrictions'),
            platform_restrictions=blockchain_data.get('platform_restrictions'),
            revenue_share_percentage=blockchain_data.get('revenue_share_percentage'),
            price=blockchain_data.get('price'),
            currency=blockchain_data.get('currency', 'USD'),
            blockchain_tx_id=blockchain_data.get('blockchain_tx_id'),
            smart_contract_address=blockchain_data.get('smart_contract_address'),
            metadata=blockchain_data.get('metadata', {}),
            created_at=datetime.fromisoformat(blockchain_data['created_at']),
            updated_at=datetime.fromisoformat(blockchain_data['updated_at'])
        )
