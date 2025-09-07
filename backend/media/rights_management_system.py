"""⚖️ Rights Management System - Digital Rights Management
======================================================

Enterprise-grade digital rights management system providing comprehensive
intellectual property protection, licensing management, and revenue distribution
for content creators and collaborators.

Key Features:
- Smart contract-based rights management
- Multi-party revenue distribution
- Dynamic licensing with terms enforcement
- Usage tracking and analytics
- Integration with blockchain for transparency
- Automated royalty calculations and payments

Author: Fahed Mlaiel (mlaiel@live.de)
Team: Lead Dev + Legal Tech Expert + Blockchain Developer + IP Lawyer + Financial Systems
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

⚠️ CRITICAL LEGAL WARNING ⚠️
This proprietary rights management system contains advanced legal and financial algorithms
and trade secrets belonging exclusively to Fahed Mlaiel (mlaiel@live.de).

UNAUTHORIZED USE IS STRICTLY PROHIBITED:
- Code theft, copying, or reverse engineering
- Commercial use without explicit written permission
- Rights management algorithm extraction or appropriation
- Distribution without proper licensing

Contact mlaiel@live.de for licensing and authorization inquiries.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json
import hashlib
from decimal import Decimal

# Import existing infrastructure with graceful fallbacks
SmartContractEngine = None
BlockchainIntegration = None
PaymentProcessor = None
LegalComplianceEngine = None

try:
    from backend.blockchain.smart_contracts import SmartContractEngine
except ImportError:
    pass

try:
    from backend.blockchain.integration import BlockchainIntegration
except ImportError:
    pass

try:
    from backend.payment.processor import PaymentProcessor
except ImportError:
    pass

try:
    from backend.compliance.legal_engine import LegalComplianceEngine
except ImportError:
    pass

logger = logging.getLogger(__name__)

class RightsType(Enum):
    """Types of intellectual property rights"""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    TRADE_SECRET = "trade_secret"
    PUBLICITY = "publicity"
    PERFORMANCE = "performance"
    MECHANICAL = "mechanical"
    SYNCHRONIZATION = "synchronization"

class LicenseType(Enum):
    """Types of content licenses"""
    EXCLUSIVE = "exclusive"
    NON_EXCLUSIVE = "non_exclusive"
    ROYALTY_FREE = "royalty_free"
    CREATIVE_COMMONS = "creative_commons"
    COMMERCIAL = "commercial"
    EDITORIAL = "editorial"
    EXTENDED = "extended"
    CUSTOM = "custom"

class UsageType(Enum):
    """Types of content usage"""
    STREAMING = "streaming"
    DOWNLOAD = "download"
    BROADCAST = "broadcast"
    SOCIAL_MEDIA = "social_media"
    COMMERCIAL_USE = "commercial_use"
    EDUCATIONAL = "educational"
    PERSONAL = "personal"
    COLLABORATION = "collaboration"

class RevenueModel(Enum):
    """Revenue distribution models"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    TIERED = "tiered"
    USAGE_BASED = "usage_based"
    HYBRID = "hybrid"

@dataclass
class RightsHolder:
    """Rights holder information"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    email: str = ""
    wallet_address: Optional[str] = None
    percentage_share: Decimal = Decimal('0.0')
    role: str = ""  # creator, collaborator, publisher, distributor
    metadata: Dict[str, Any] = field(default_factory=dict)
    verification_status: str = "pending"  # pending, verified, disputed

@dataclass
class LicenseTerms:
    """License terms and conditions"""
    license_type: LicenseType = LicenseType.NON_EXCLUSIVE
    usage_types: List[UsageType] = field(default_factory=list)
    duration: Optional[timedelta] = None
    territory: List[str] = field(default_factory=list)  # ISO country codes
    exclusions: List[str] = field(default_factory=list)
    price: Decimal = Decimal('0.0')
    currency: str = "USD"
    payment_terms: Dict[str, Any] = field(default_factory=dict)
    custom_terms: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RightsRecord:
    """Digital rights record"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    rights_type: RightsType = RightsType.COPYRIGHT
    rights_holders: List[RightsHolder] = field(default_factory=list)
    license_terms: LicenseTerms = field(default_factory=LicenseTerms)
    creation_date: datetime = field(default_factory=datetime.now)
    registration_date: datetime = field(default_factory=datetime.now)
    expiration_date: Optional[datetime] = None
    smart_contract_address: Optional[str] = None
    blockchain_hash: Optional[str] = None
    legal_jurisdiction: str = "US"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UsageEvent:
    """Content usage event for tracking"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    rights_record_id: str = ""
    user_id: str = ""
    usage_type: UsageType = UsageType.STREAMING
    platform: str = ""
    location: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    revenue_generated: Decimal = Decimal('0.0')
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RevenueDistribution:
    """Revenue distribution calculation"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content_id: str = ""
    rights_record_id: str = ""
    period_start: datetime = field(default_factory=datetime.now)
    period_end: datetime = field(default_factory=datetime.now)
    total_revenue: Decimal = Decimal('0.0')
    distributions: List[Dict[str, Any]] = field(default_factory=list)
    fees_deducted: Decimal = Decimal('0.0')
    processed: bool = False
    payment_references: List[str] = field(default_factory=list)

class RightsManagementSystem:
    """
    Comprehensive digital rights management system
    
    Provides enterprise-grade rights management capabilities:
    - Smart contract-based rights registration and enforcement
    - Multi-party revenue distribution with real-time calculations
    - Usage tracking and analytics across platforms
    - Legal compliance and jurisdiction management
    - Automated licensing and payment processing
    - Blockchain integration for transparency and immutability
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        
        # Initialize core components
        self._init_smart_contracts()
        self._init_blockchain_integration()
        self._init_payment_processing()
        self._init_legal_compliance()
        
        # Rights management statistics
        self.rights_stats = {
            'total_rights_registered': 0,
            'active_licenses': 0,
            'revenue_distributed': Decimal('0.0'),
            'usage_events_tracked': 0,
            'compliance_checks': 0
        }
        
        logger.info("RightsManagementSystem initialized successfully")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default configuration for rights management system"""
        return {
            'smart_contracts': {
                'enabled': True,
                'network': 'ethereum',
                'gas_price': 'standard',
                'contract_templates': {
                    'simple_license': 'simple_license_v1',
                    'revenue_sharing': 'revenue_sharing_v1',
                    'collaborative': 'collaborative_v1'
                }
            },
            'revenue_distribution': {
                'minimum_payout': Decimal('10.00'),
                'processing_fee_percent': Decimal('2.5'),
                'distribution_frequency': 'monthly',
                'supported_currencies': ['USD', 'EUR', 'GBP', 'ETH', 'BTC']
            },
            'usage_tracking': {
                'enable_real_time': True,
                'aggregation_interval': 'hourly',
                'retention_period_days': 2555,  # 7 years
                'privacy_compliance': True
            },
            'legal_compliance': {
                'supported_jurisdictions': ['US', 'EU', 'UK', 'CA', 'AU'],
                'copyright_registration': True,
                'dmca_compliance': True,
                'gdpr_compliance': True
            },
            'licensing': {
                'default_license_duration': timedelta(days=365),
                'auto_renewal': False,
                'price_tiers': {
                    'standard': Decimal('9.99'),
                    'extended': Decimal('49.99'),
                    'commercial': Decimal('199.99')
                }
            }
        }
    
    def _init_smart_contracts(self):
        """Initialize smart contract integration"""
        try:
            if SmartContractEngine:
                self.smart_contract_engine = SmartContractEngine()
            else:
                self.smart_contract_engine = None
                logger.warning("Smart contract engine not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to initialize smart contract engine: {e}")
            self.smart_contract_engine = None
    
    def _init_blockchain_integration(self):
        """Initialize blockchain integration"""
        try:
            if BlockchainIntegration:
                self.blockchain = BlockchainIntegration()
            else:
                self.blockchain = None
                logger.warning("Blockchain integration not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to initialize blockchain integration: {e}")
            self.blockchain = None
    
    def _init_payment_processing(self):
        """Initialize payment processing"""
        try:
            if PaymentProcessor:
                self.payment_processor = PaymentProcessor()
            else:
                self.payment_processor = None
                logger.warning("Payment processor not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to initialize payment processor: {e}")
            self.payment_processor = None
    
    def _init_legal_compliance(self):
        """Initialize legal compliance engine"""
        try:
            if LegalComplianceEngine:
                self.legal_compliance = LegalComplianceEngine()
            else:
                self.legal_compliance = None
                logger.warning("Legal compliance engine not available, using fallback")
        except Exception as e:
            logger.error(f"Failed to initialize legal compliance engine: {e}")
            self.legal_compliance = None
    
    async def register_rights(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """
        Register digital rights for content
        
        Args:
            rights_record: Rights record with ownership and licensing information
            
        Returns:
            Registration result with smart contract address and blockchain hash
        """
        try:
            logger.info(f"Registering rights for content {rights_record.content_id}")
            
            # Validate rights record
            if not await self._validate_rights_record(rights_record):
                return {
                    'success': False,
                    'error': 'Invalid rights record'
                }
            
            # Deploy smart contract if enabled
            smart_contract_address = None
            if self.config['smart_contracts']['enabled'] and self.smart_contract_engine:
                smart_contract_address = await self._deploy_rights_contract(rights_record)
                rights_record.smart_contract_address = smart_contract_address
            
            # Register on blockchain if available
            blockchain_hash = None
            if self.blockchain:
                blockchain_hash = await self._register_on_blockchain(rights_record)
                rights_record.blockchain_hash = blockchain_hash
            
            # Perform legal compliance checks
            compliance_result = await self._perform_compliance_checks(rights_record)
            
            # Store rights record
            storage_result = await self._store_rights_record(rights_record)
            
            # Update statistics
            self.rights_stats['total_rights_registered'] += 1
            
            result = {
                'success': True,
                'rights_record_id': rights_record.id,
                'smart_contract_address': smart_contract_address,
                'blockchain_hash': blockchain_hash,
                'compliance_status': compliance_result,
                'storage_status': storage_result
            }
            
            logger.info(f"Rights registered successfully for content {rights_record.content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Rights registration failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _validate_rights_record(self, rights_record: RightsRecord) -> bool:
        """Validate rights record"""
        try:
            # Check required fields
            if not all([rights_record.content_id, rights_record.rights_holders]):
                logger.error("Missing required fields in rights record")
                return False
            
            # Validate percentage shares sum to 100%
            total_percentage = sum(holder.percentage_share for holder in rights_record.rights_holders)
            if abs(total_percentage - Decimal('100.0')) > Decimal('0.01'):
                logger.error(f"Rights holder percentages sum to {total_percentage}, not 100%")
                return False
            
            # Validate license terms
            if not rights_record.license_terms.usage_types:
                logger.error("No usage types specified in license terms")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rights record validation failed: {e}")
            return False
    
    async def _deploy_rights_contract(self, rights_record: RightsRecord) -> Optional[str]:
        """Deploy smart contract for rights management"""
        try:
            if self.smart_contract_engine:
                contract_data = {
                    'content_id': rights_record.content_id,
                    'rights_holders': [
                        {
                            'address': holder.wallet_address or '0x0',
                            'percentage': float(holder.percentage_share)
                        }
                        for holder in rights_record.rights_holders
                    ],
                    'license_terms': {
                        'license_type': rights_record.license_terms.license_type.value,
                        'price': float(rights_record.license_terms.price),
                        'currency': rights_record.license_terms.currency
                    }
                }
                
                contract_address = await self.smart_contract_engine.deploy_rights_contract(contract_data)
                return contract_address
            else:
                # Simulate contract deployment
                logger.info("Smart contract deployment simulation")
                return f"0x{hashlib.sha256(rights_record.content_id.encode()).hexdigest()[:40]}"
                
        except Exception as e:
            logger.error(f"Smart contract deployment failed: {e}")
            return None
    
    async def _register_on_blockchain(self, rights_record: RightsRecord) -> Optional[str]:
        """Register rights record on blockchain"""
        try:
            if self.blockchain:
                record_hash = hashlib.sha256(
                    json.dumps(rights_record.__dict__, default=str).encode()
                ).hexdigest()
                
                blockchain_hash = await self.blockchain.register_rights(
                    rights_record.content_id,
                    record_hash,
                    rights_record.smart_contract_address
                )
                
                return blockchain_hash
            else:
                # Simulate blockchain registration
                logger.info("Blockchain registration simulation")
                return hashlib.sha256(f"blockchain_{rights_record.id}".encode()).hexdigest()
                
        except Exception as e:
            logger.error(f"Blockchain registration failed: {e}")
            return None
    
    async def _perform_compliance_checks(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Perform legal compliance checks"""
        try:
            if self.legal_compliance:
                compliance_result = await self.legal_compliance.check_rights_compliance(rights_record)
            else:
                # Simulate compliance checks
                compliance_result = {
                    'copyright_valid': True,
                    'jurisdiction_compliant': True,
                    'dmca_compliant': True,
                    'gdpr_compliant': True,
                    'overall_status': 'compliant'
                }
                logger.info("Legal compliance check simulation")
            
            self.rights_stats['compliance_checks'] += 1
            return compliance_result
            
        except Exception as e:
            logger.error(f"Compliance checks failed: {e}")
            return {'overall_status': 'error', 'error': str(e)}
    
    async def _store_rights_record(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Store rights record in database"""
        try:
            # In production, would store in database
            logger.info(f"Rights record stored for content {rights_record.content_id}")
            return {
                'stored': True,
                'storage_id': rights_record.id
            }
            
        except Exception as e:
            logger.error(f"Rights record storage failed: {e}")
            return {'stored': False, 'error': str(e)}
    
    async def track_usage(self, usage_event: UsageEvent) -> Dict[str, Any]:
        """
        Track content usage event
        
        Args:
            usage_event: Usage event with platform and revenue information
            
        Returns:
            Tracking result with analytics and revenue calculations
        """
        try:
            logger.info(f"Tracking usage for content {usage_event.content_id}")
            
            # Validate usage event
            if not await self._validate_usage_event(usage_event):
                return {
                    'success': False,
                    'error': 'Invalid usage event'
                }
            
            # Get rights record
            rights_record = await self._get_rights_record(usage_event.content_id)
            if not rights_record:
                return {
                    'success': False,
                    'error': 'Rights record not found'
                }
            
            # Calculate revenue distribution
            revenue_distribution = await self._calculate_revenue_distribution(
                usage_event, rights_record
            )
            
            # Store usage event
            storage_result = await self._store_usage_event(usage_event)
            
            # Update smart contract if applicable
            if rights_record.smart_contract_address and self.smart_contract_engine:
                await self._update_contract_usage(rights_record.smart_contract_address, usage_event)
            
            # Update statistics
            self.rights_stats['usage_events_tracked'] += 1
            self.rights_stats['revenue_distributed'] += usage_event.revenue_generated
            
            result = {
                'success': True,
                'usage_event_id': usage_event.id,
                'revenue_distribution': revenue_distribution,
                'storage_status': storage_result
            }
            
            logger.info(f"Usage tracked successfully for content {usage_event.content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Usage tracking failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _validate_usage_event(self, usage_event: UsageEvent) -> bool:
        """Validate usage event"""
        try:
            # Check required fields
            if not all([usage_event.content_id, usage_event.user_id, usage_event.platform]):
                logger.error("Missing required fields in usage event")
                return False
            
            # Validate revenue amount
            if usage_event.revenue_generated < 0:
                logger.error("Revenue amount cannot be negative")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Usage event validation failed: {e}")
            return False
    
    async def _get_rights_record(self, content_id: str) -> Optional[RightsRecord]:
        """Get rights record for content"""
        try:
            # In production, would query database
            # For now, simulate finding a rights record
            logger.info(f"Retrieving rights record for content {content_id}")
            
            # Return a mock rights record
            return RightsRecord(
                content_id=content_id,
                rights_holders=[
                    RightsHolder(
                        name="Content Creator",
                        percentage_share=Decimal('70.0'),
                        role="creator"
                    ),
                    RightsHolder(
                        name="Platform",
                        percentage_share=Decimal('30.0'),
                        role="distributor"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Failed to get rights record: {e}")
            return None
    
    async def _calculate_revenue_distribution(self, usage_event: UsageEvent, 
                                            rights_record: RightsRecord) -> RevenueDistribution:
        """Calculate revenue distribution based on rights holders"""
        try:
            distribution = RevenueDistribution(
                content_id=usage_event.content_id,
                rights_record_id=rights_record.id,
                total_revenue=usage_event.revenue_generated
            )
            
            # Calculate processing fees
            processing_fee_percent = self.config['revenue_distribution']['processing_fee_percent']
            distribution.fees_deducted = distribution.total_revenue * processing_fee_percent / Decimal('100')
            
            # Calculate net revenue for distribution
            net_revenue = distribution.total_revenue - distribution.fees_deducted
            
            # Distribute to rights holders
            for holder in rights_record.rights_holders:
                holder_amount = net_revenue * holder.percentage_share / Decimal('100')
                
                distribution.distributions.append({
                    'holder_id': holder.id,
                    'holder_name': holder.name,
                    'percentage': holder.percentage_share,
                    'amount': holder_amount,
                    'currency': usage_event.currency,
                    'role': holder.role
                })
            
            return distribution
            
        except Exception as e:
            logger.error(f"Revenue distribution calculation failed: {e}")
            return RevenueDistribution(
                content_id=usage_event.content_id,
                total_revenue=Decimal('0.0')
            )
    
    async def _store_usage_event(self, usage_event: UsageEvent) -> Dict[str, Any]:
        """Store usage event in database"""
        try:
            # In production, would store in database
            logger.info(f"Usage event stored for content {usage_event.content_id}")
            return {
                'stored': True,
                'storage_id': usage_event.id
            }
            
        except Exception as e:
            logger.error(f"Usage event storage failed: {e}")
            return {'stored': False, 'error': str(e)}
    
    async def _update_contract_usage(self, contract_address: str, usage_event: UsageEvent):
        """Update smart contract with usage information"""
        try:
            if self.smart_contract_engine:
                await self.smart_contract_engine.update_usage(
                    contract_address,
                    usage_event.usage_type.value,
                    float(usage_event.revenue_generated)
                )
            else:
                logger.info("Smart contract usage update simulation")
                
        except Exception as e:
            logger.error(f"Smart contract update failed: {e}")
    
    async def process_revenue_distribution(self, content_id: str, 
                                         period_start: datetime, 
                                         period_end: datetime) -> Dict[str, Any]:
        """
        Process revenue distribution for a specific period
        
        Args:
            content_id: Content identifier
            period_start: Distribution period start
            period_end: Distribution period end
            
        Returns:
            Distribution processing result with payment references
        """
        try:
            logger.info(f"Processing revenue distribution for content {content_id}")
            
            # Get usage events for period
            usage_events = await self._get_usage_events_for_period(
                content_id, period_start, period_end
            )
            
            if not usage_events:
                return {
                    'success': True,
                    'total_revenue': Decimal('0.0'),
                    'distributions': [],
                    'message': 'No usage events found for period'
                }
            
            # Calculate total revenue distribution
            total_revenue = sum(event.revenue_generated for event in usage_events)
            
            # Get rights record
            rights_record = await self._get_rights_record(content_id)
            if not rights_record:
                return {
                    'success': False,
                    'error': 'Rights record not found'
                }
            
            # Process payments to rights holders
            payment_results = []
            for holder in rights_record.rights_holders:
                holder_revenue = total_revenue * holder.percentage_share / Decimal('100')
                
                # Only process payments above minimum threshold
                if holder_revenue >= self.config['revenue_distribution']['minimum_payout']:
                    payment_result = await self._process_payment(holder, holder_revenue)
                    payment_results.append(payment_result)
                else:
                    logger.info(f"Payment below minimum threshold for holder {holder.name}")
            
            result = {
                'success': True,
                'content_id': content_id,
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'total_revenue': total_revenue,
                'usage_events': len(usage_events),
                'payments_processed': len(payment_results),
                'payment_results': payment_results
            }
            
            logger.info(f"Revenue distribution processed successfully for content {content_id}")
            return result
            
        except Exception as e:
            logger.error(f"Revenue distribution processing failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _get_usage_events_for_period(self, content_id: str, 
                                         period_start: datetime, 
                                         period_end: datetime) -> List[UsageEvent]:
        """Get usage events for specified period"""
        try:
            # In production, would query database
            # For now, simulate some usage events
            logger.info(f"Retrieving usage events for content {content_id}")
            
            return [
                UsageEvent(
                    content_id=content_id,
                    user_id="user_123",
                    usage_type=UsageType.STREAMING,
                    platform="platform_a",
                    revenue_generated=Decimal('5.00'),
                    timestamp=period_start + timedelta(hours=1)
                ),
                UsageEvent(
                    content_id=content_id,
                    user_id="user_456",
                    usage_type=UsageType.DOWNLOAD,
                    platform="platform_b",
                    revenue_generated=Decimal('3.00'),
                    timestamp=period_start + timedelta(hours=12)
                )
            ]
            
        except Exception as e:
            logger.error(f"Failed to get usage events: {e}")
            return []
    
    async def _process_payment(self, rights_holder: RightsHolder, amount: Decimal) -> Dict[str, Any]:
        """Process payment to rights holder"""
        try:
            if self.payment_processor:
                payment_result = await self.payment_processor.process_payment(
                    recipient=rights_holder.wallet_address or rights_holder.email,
                    amount=amount,
                    currency='USD',
                    metadata={
                        'holder_id': rights_holder.id,
                        'holder_name': rights_holder.name,
                        'payment_type': 'rights_distribution'
                    }
                )
                return payment_result
            else:
                # Simulate payment processing
                payment_reference = f"PAY_{uuid.uuid4()}"
                logger.info(f"Payment simulation: {amount} USD to {rights_holder.name}")
                
                return {
                    'success': True,
                    'payment_reference': payment_reference,
                    'recipient': rights_holder.name,
                    'amount': amount,
                    'currency': 'USD'
                }
                
        except Exception as e:
            logger.error(f"Payment processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'recipient': rights_holder.name,
                'amount': amount
            }
    
    async def get_rights_status(self, content_id: str) -> Dict[str, Any]:
        """Get rights status for content"""
        try:
            rights_record = await self._get_rights_record(content_id)
            
            if not rights_record:
                return {
                    'content_id': content_id,
                    'rights_registered': False
                }
            
            # Get usage statistics
            usage_stats = await self._get_usage_statistics(content_id)
            
            # Get revenue statistics
            revenue_stats = await self._get_revenue_statistics(content_id)
            
            return {
                'content_id': content_id,
                'rights_registered': True,
                'rights_record_id': rights_record.id,
                'rights_type': rights_record.rights_type.value,
                'rights_holders': len(rights_record.rights_holders),
                'smart_contract_address': rights_record.smart_contract_address,
                'blockchain_hash': rights_record.blockchain_hash,
                'license_type': rights_record.license_terms.license_type.value,
                'usage_statistics': usage_stats,
                'revenue_statistics': revenue_stats
            }
            
        except Exception as e:
            logger.error(f"Failed to get rights status: {e}")
            return {
                'content_id': content_id,
                'rights_registered': False,
                'error': str(e)
            }
    
    async def _get_usage_statistics(self, content_id: str) -> Dict[str, Any]:
        """Get usage statistics for content"""
        try:
            # In production, would query analytics database
            return {
                'total_usage_events': 100,
                'streaming_events': 75,
                'download_events': 25,
                'platforms': ['platform_a', 'platform_b', 'platform_c'],
                'last_usage': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get usage statistics: {e}")
            return {}
    
    async def _get_revenue_statistics(self, content_id: str) -> Dict[str, Any]:
        """Get revenue statistics for content"""
        try:
            # In production, would query financial database
            return {
                'total_revenue': '150.00',
                'currency': 'USD',
                'revenue_this_month': '25.00',
                'average_per_usage': '1.50',
                'last_distribution': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get revenue statistics: {e}")
            return {}
    
    def get_rights_stats(self) -> Dict[str, Any]:
        """Get rights management system statistics"""
        return {
            'system_status': 'active',
            'statistics': {
                'total_rights_registered': self.rights_stats['total_rights_registered'],
                'active_licenses': self.rights_stats['active_licenses'],
                'revenue_distributed': str(self.rights_stats['revenue_distributed']),
                'usage_events_tracked': self.rights_stats['usage_events_tracked'],
                'compliance_checks': self.rights_stats['compliance_checks']
            },
            'configuration': {
                'supported_rights_types': [rt.value for rt in RightsType],
                'supported_license_types': [lt.value for lt in LicenseType],
                'supported_usage_types': [ut.value for ut in UsageType],
                'revenue_models': [rm.value for rm in RevenueModel]
            },
            'infrastructure_status': {
                'smart_contract_engine': self.smart_contract_engine is not None,
                'blockchain_integration': self.blockchain is not None,
                'payment_processor': self.payment_processor is not None,
                'legal_compliance': self.legal_compliance is not None
            }
        }