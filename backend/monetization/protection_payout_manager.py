"""Protection Payout Manager - Protection-based Payout Management System
========================================================================

Enterprise-grade protection-based payout management system providing comprehensive
payout processing for content protection services, recovered revenue distribution,
and automated compensation for rights holders and protection service providers.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/protection_payout_manager.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class ProtectionServiceType(str, Enum):
    """Types of protection services."""
    COPYRIGHT_MONITORING = "copyright_monitoring"
    PIRACY_DETECTION = "piracy_detection"
    TAKEDOWN_SERVICES = "takedown_services"
    LEGAL_ENFORCEMENT = "legal_enforcement"
    REVENUE_RECOVERY = "revenue_recovery"
    RIGHTS_MANAGEMENT = "rights_management"
    FRAUD_PREVENTION = "fraud_prevention"
    COMPLIANCE_MONITORING = "compliance_monitoring"


class PayoutType(str, Enum):
    """Types of protection payouts."""
    RECOVERED_REVENUE = "recovered_revenue"
    SERVICE_FEE = "service_fee"
    SUCCESS_BONUS = "success_bonus"
    LEGAL_SETTLEMENT = "legal_settlement"
    COMPENSATION = "compensation"
    PENALTY_RECOVERY = "penalty_recovery"
    PREVENTION_REWARD = "prevention_reward"
    MONITORING_FEE = "monitoring_fee"


class PayoutStatus(str, Enum):
    """Payout processing status."""
    PENDING = "pending"
    CALCULATED = "calculated"
    APPROVED = "approved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class PayoutFrequency(str, Enum):
    """Payout frequency options."""
    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ON_DEMAND = "on_demand"


@dataclass
class ProtectionServiceProvider:
    """Protection service provider profile."""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    service_types: List[ProtectionServiceType] = field(default_factory=list)
    fee_structure: Dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0
    average_recovery_time: float = 0.0  # days
    minimum_payout: Decimal = Decimal('10.00')
    payout_frequency: PayoutFrequency = PayoutFrequency.MONTHLY
    payment_methods: List[str] = field(default_factory=list)
    contract_terms: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ProtectionCase:
    """Protection case record."""
    id: UUID = field(default_factory=uuid4)
    content_id: UUID = None
    rights_holder_id: UUID = None
    service_provider_id: UUID = None
    case_type: ProtectionServiceType = ProtectionServiceType.COPYRIGHT_MONITORING
    case_description: str = ""
    start_date: datetime = field(default_factory=datetime.utcnow)
    resolution_date: Optional[datetime] = None
    status: str = "open"
    recovered_amount: Decimal = Decimal('0.00')
    service_cost: Decimal = Decimal('0.00')
    success_bonus_amount: Decimal = Decimal('0.00')
    case_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtectionPayout:
    """Protection payout record."""
    id: UUID = field(default_factory=uuid4)
    case_id: UUID = None
    recipient_id: UUID = None
    recipient_type: str = "rights_holder"  # or "service_provider"
    payout_type: PayoutType = PayoutType.RECOVERED_REVENUE
    gross_amount: Decimal = Decimal('0.00')
    fees: Decimal = Decimal('0.00')
    taxes: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    payout_status: PayoutStatus = PayoutStatus.PENDING
    payment_method: str = ""
    scheduled_date: datetime = field(default_factory=datetime.utcnow)
    processed_date: Optional[datetime] = None
    transaction_reference: Optional[str] = None
    payout_metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PayoutCalculation:
    """Payout calculation breakdown."""
    case_id: UUID = None
    total_recovered: Decimal = Decimal('0.00')
    service_fees: Dict[str, Decimal] = field(default_factory=dict)
    rights_holder_share: Decimal = Decimal('0.00')
    service_provider_share: Decimal = Decimal('0.00')
    platform_share: Decimal = Decimal('0.00')
    tax_withholdings: Dict[str, Decimal] = field(default_factory=dict)
    calculation_breakdown: Dict[str, Any] = field(default_factory=dict)
    calculation_date: datetime = field(default_factory=datetime.utcnow)


class ProtectionPayoutManager:
    """Advanced protection payout management system."""
    
    def __init__(self):
        """Initialize protection payout manager."""
        self.service_providers: Dict[UUID, ProtectionServiceProvider] = {}
        self.protection_cases: Dict[UUID, ProtectionCase] = {}
        self.payouts: Dict[UUID, ProtectionPayout] = {}
        self.payout_calculations: Dict[UUID, PayoutCalculation] = {}
        self.fee_structures: Dict[str, Any] = {}
        self._load_default_fee_structures()
        
    def _load_default_fee_structures(self) -> None:
        """Load default fee structures for protection services."""
        self.fee_structures = {
            'standard_recovery': {
                'service_provider_percentage': Decimal('30.00'),  # 30%
                'rights_holder_percentage': Decimal('70.00'),     # 70%
                'platform_percentage': Decimal('0.00'),           # 0%
                'minimum_fee': Decimal('10.00'),
                'success_bonus_percentage': Decimal('5.00')       # 5% bonus for successful cases
            },
            'premium_recovery': {
                'service_provider_percentage': Decimal('25.00'),  # 25%
                'rights_holder_percentage': Decimal('75.00'),     # 75%
                'platform_percentage': Decimal('0.00'),           # 0%
                'minimum_fee': Decimal('25.00'),
                'success_bonus_percentage': Decimal('10.00')      # 10% bonus
            },
            'enterprise_recovery': {
                'service_provider_percentage': Decimal('20.00'),  # 20%
                'rights_holder_percentage': Decimal('80.00'),     # 80%
                'platform_percentage': Decimal('0.00'),           # 0%
                'minimum_fee': Decimal('50.00'),
                'success_bonus_percentage': Decimal('15.00')      # 15% bonus
            },
            'monitoring_only': {
                'service_provider_percentage': Decimal('100.00'), # Fixed fee
                'rights_holder_percentage': Decimal('0.00'),
                'platform_percentage': Decimal('0.00'),
                'flat_fee': Decimal('100.00')                     # Monthly flat fee
            }
        }
        
    async def register_service_provider(
        self,
        provider_data: Dict[str, Any]
    ) -> ProtectionServiceProvider:
        """Register protection service provider."""
        try:
            provider = ProtectionServiceProvider(
                name=provider_data['name'],
                service_types=[
                    ProtectionServiceType(service) 
                    for service in provider_data.get('service_types', [])
                ],
                fee_structure=provider_data.get('fee_structure', {}),
                success_rate=provider_data.get('success_rate', 0.0),
                average_recovery_time=provider_data.get('average_recovery_time', 30.0),
                minimum_payout=Decimal(str(provider_data.get('minimum_payout', '10.00'))),
                payout_frequency=PayoutFrequency(provider_data.get('payout_frequency', 'monthly')),
                payment_methods=provider_data.get('payment_methods', ['bank_transfer']),
                contract_terms=provider_data.get('contract_terms', {})
            )
            
            self.service_providers[provider.id] = provider
            
            logger.info(f"Registered service provider: {provider.id}")
            return provider
            
        except Exception as e:
            logger.error(f"Error registering service provider: {e}")
            raise
            
    async def create_protection_case(
        self,
        case_data: Dict[str, Any]
    ) -> ProtectionCase:
        """Create new protection case."""
        try:
            case = ProtectionCase(
                content_id=UUID(case_data['content_id']),
                rights_holder_id=UUID(case_data['rights_holder_id']),
                service_provider_id=UUID(case_data['service_provider_id']),
                case_type=ProtectionServiceType(case_data['case_type']),
                case_description=case_data.get('case_description', ''),
                case_metadata=case_data.get('metadata', {})
            )
            
            self.protection_cases[case.id] = case
            
            logger.info(f"Created protection case: {case.id}")
            return case
            
        except Exception as e:
            logger.error(f"Error creating protection case: {e}")
            raise
            
    async def resolve_protection_case(
        self,
        case_id: UUID,
        resolution_data: Dict[str, Any]
    ) -> PayoutCalculation:
        """Resolve protection case and calculate payouts."""
        try:
            if case_id not in self.protection_cases:
                raise ValueError(f"Protection case {case_id} not found")
                
            case = self.protection_cases[case_id]
            
            # Update case with resolution data
            case.resolution_date = datetime.utcnow()
            case.status = resolution_data.get('status', 'resolved')
            case.recovered_amount = Decimal(str(resolution_data.get('recovered_amount', '0.00')))
            case.service_cost = Decimal(str(resolution_data.get('service_cost', '0.00')))
            
            # Calculate payouts
            calculation = await self._calculate_case_payouts(case)
            self.payout_calculations[case.id] = calculation
            
            # Create payout records
            await self._create_payout_records(case, calculation)
            
            logger.info(f"Resolved protection case: {case_id}")
            return calculation
            
        except Exception as e:
            logger.error(f"Error resolving protection case: {e}")
            raise
            
    async def _calculate_case_payouts(self, case: ProtectionCase) -> PayoutCalculation:
        """Calculate payout distribution for resolved case."""
        try:
            service_provider = self.service_providers[case.service_provider_id]
            fee_structure = service_provider.fee_structure or self.fee_structures['standard_recovery']
            
            calculation = PayoutCalculation(
                case_id=case.id,
                total_recovered=case.recovered_amount
            )
            
            if case.recovered_amount > Decimal('0.00'):
                # Calculate service provider share
                service_percentage = fee_structure.get('service_provider_percentage', Decimal('30.00'))
                service_provider_share = case.recovered_amount * (service_percentage / Decimal('100.00'))
                
                # Apply minimum fee if specified
                minimum_fee = fee_structure.get('minimum_fee', Decimal('0.00'))
                service_provider_share = max(service_provider_share, minimum_fee)
                
                # Calculate success bonus
                success_bonus = Decimal('0.00')
                if case.status == 'resolved' and 'success_bonus_percentage' in fee_structure:
                    bonus_percentage = fee_structure['success_bonus_percentage']
                    success_bonus = case.recovered_amount * (bonus_percentage / Decimal('100.00'))
                    
                case.success_bonus_amount = success_bonus
                total_service_share = service_provider_share + success_bonus
                
                # Calculate rights holder share
                rights_holder_share = case.recovered_amount - total_service_share
                
                # Calculate platform share (if any)
                platform_percentage = fee_structure.get('platform_percentage', Decimal('0.00'))
                platform_share = case.recovered_amount * (platform_percentage / Decimal('100.00'))
                
                # Adjust rights holder share for platform cut
                rights_holder_share -= platform_share
                
                # Calculate taxes (simplified)
                tax_rate = Decimal('0.10')  # 10% tax rate
                service_provider_tax = total_service_share * tax_rate
                rights_holder_tax = rights_holder_share * tax_rate
                
                # Update calculation
                calculation.service_fees['base_fee'] = service_provider_share
                calculation.service_fees['success_bonus'] = success_bonus
                calculation.service_provider_share = total_service_share - service_provider_tax
                calculation.rights_holder_share = rights_holder_share - rights_holder_tax
                calculation.platform_share = platform_share
                calculation.tax_withholdings['service_provider'] = service_provider_tax
                calculation.tax_withholdings['rights_holder'] = rights_holder_tax
                
                calculation.calculation_breakdown = {
                    'fee_structure_used': fee_structure,
                    'service_percentage': float(service_percentage),
                    'success_bonus_percentage': float(fee_structure.get('success_bonus_percentage', 0)),
                    'tax_rate': float(tax_rate),
                    'breakdown': {
                        'total_recovered': float(case.recovered_amount),
                        'service_provider_gross': float(total_service_share),
                        'rights_holder_gross': float(rights_holder_share + rights_holder_tax),
                        'platform_share': float(platform_share),
                        'total_taxes': float(service_provider_tax + rights_holder_tax),
                        'service_provider_net': float(calculation.service_provider_share),
                        'rights_holder_net': float(calculation.rights_holder_share)
                    }
                }
                
            else:
                # No recovery - only service costs
                flat_fee = fee_structure.get('flat_fee', Decimal('0.00'))
                if flat_fee > Decimal('0.00'):
                    calculation.service_provider_share = flat_fee
                    calculation.rights_holder_share = -flat_fee  # Rights holder pays the fee
                    
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating case payouts: {e}")
            raise
            
    async def _create_payout_records(
        self,
        case: ProtectionCase,
        calculation: PayoutCalculation
    ) -> List[ProtectionPayout]:
        """Create payout records based on calculation."""
        try:
            payouts = []
            
            # Create service provider payout
            if calculation.service_provider_share > Decimal('0.00'):
                service_provider = self.service_providers[case.service_provider_id]
                
                service_payout = ProtectionPayout(
                    case_id=case.id,
                    recipient_id=case.service_provider_id,
                    recipient_type="service_provider",
                    payout_type=PayoutType.SERVICE_FEE,
                    gross_amount=calculation.service_provider_share + calculation.tax_withholdings.get('service_provider', Decimal('0.00')),
                    fees=Decimal('0.00'),
                    taxes=calculation.tax_withholdings.get('service_provider', Decimal('0.00')),
                    net_amount=calculation.service_provider_share,
                    payment_method=service_provider.payment_methods[0] if service_provider.payment_methods else 'bank_transfer',
                    scheduled_date=self._calculate_payout_date(service_provider.payout_frequency)
                )
                
                payouts.append(service_payout)
                self.payouts[service_payout.id] = service_payout
                
            # Create rights holder payout
            if calculation.rights_holder_share > Decimal('0.00'):
                rights_holder_payout = ProtectionPayout(
                    case_id=case.id,
                    recipient_id=case.rights_holder_id,
                    recipient_type="rights_holder",
                    payout_type=PayoutType.RECOVERED_REVENUE,
                    gross_amount=calculation.rights_holder_share + calculation.tax_withholdings.get('rights_holder', Decimal('0.00')),
                    fees=Decimal('0.00'),
                    taxes=calculation.tax_withholdings.get('rights_holder', Decimal('0.00')),
                    net_amount=calculation.rights_holder_share,
                    payment_method='bank_transfer',
                    scheduled_date=datetime.utcnow() + timedelta(days=1)  # Next day for rights holders
                )
                
                payouts.append(rights_holder_payout)
                self.payouts[rights_holder_payout.id] = rights_holder_payout
                
            # Create success bonus payout if applicable
            if case.success_bonus_amount > Decimal('0.00'):
                bonus_payout = ProtectionPayout(
                    case_id=case.id,
                    recipient_id=case.service_provider_id,
                    recipient_type="service_provider",
                    payout_type=PayoutType.SUCCESS_BONUS,
                    gross_amount=case.success_bonus_amount,
                    fees=Decimal('0.00'),
                    taxes=Decimal('0.00'),
                    net_amount=case.success_bonus_amount,
                    payment_method=self.service_providers[case.service_provider_id].payment_methods[0],
                    scheduled_date=self._calculate_payout_date(PayoutFrequency.IMMEDIATE)
                )
                
                payouts.append(bonus_payout)
                self.payouts[bonus_payout.id] = bonus_payout
                
            return payouts
            
        except Exception as e:
            logger.error(f"Error creating payout records: {e}")
            raise
            
    def _calculate_payout_date(self, frequency: PayoutFrequency) -> datetime:
        """Calculate payout date based on frequency."""
        now = datetime.utcnow()
        
        if frequency == PayoutFrequency.IMMEDIATE:
            return now
        elif frequency == PayoutFrequency.DAILY:
            return now + timedelta(days=1)
        elif frequency == PayoutFrequency.WEEKLY:
            # Next Monday
            days_ahead = 7 - now.weekday()
            return now + timedelta(days=days_ahead)
        elif frequency == PayoutFrequency.MONTHLY:
            # First day of next month
            if now.month == 12:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, now.month + 1, 1)
        elif frequency == PayoutFrequency.QUARTERLY:
            # Next quarter
            current_quarter = (now.month - 1) // 3 + 1
            if current_quarter == 4:
                return datetime(now.year + 1, 1, 1)
            else:
                return datetime(now.year, current_quarter * 3 + 1, 1)
        else:
            return now + timedelta(days=30)  # Default to monthly
            
    async def process_payout(self, payout_id: UUID) -> Dict[str, Any]:
        """Process individual payout."""
        try:
            if payout_id not in self.payouts:
                raise ValueError(f"Payout {payout_id} not found")
                
            payout = self.payouts[payout_id]
            
            # Check if payout is ready for processing
            if payout.payout_status != PayoutStatus.PENDING:
                return {'error': f'Payout status is {payout.payout_status}, cannot process'}
                
            if datetime.utcnow() < payout.scheduled_date:
                return {'error': 'Payout not yet scheduled for processing'}
                
            # Update status to processing
            payout.payout_status = PayoutStatus.PROCESSING
            
            # Simulate payment processing
            processing_result = await self._execute_payment(payout)
            
            if processing_result['success']:
                payout.payout_status = PayoutStatus.COMPLETED
                payout.processed_date = datetime.utcnow()
                payout.transaction_reference = processing_result['transaction_id']
                
                logger.info(f"Payout processed successfully: {payout_id}")
                return {
                    'status': 'success',
                    'payout_id': payout_id,
                    'transaction_reference': processing_result['transaction_id'],
                    'processed_amount': float(payout.net_amount)
                }
            else:
                payout.payout_status = PayoutStatus.FAILED
                payout.payout_metadata['failure_reason'] = processing_result['error']
                
                logger.error(f"Payout processing failed: {payout_id}")
                return {
                    'status': 'failed',
                    'payout_id': payout_id,
                    'error': processing_result['error']
                }
                
        except Exception as e:
            logger.error(f"Error processing payout: {e}")
            return {'status': 'error', 'error': str(e)}
            
    async def _execute_payment(self, payout: ProtectionPayout) -> Dict[str, Any]:
        """Execute payment for payout."""
        try:
            # Simulate payment processing based on payment method
            if payout.payment_method == 'bank_transfer':
                # Simulate bank transfer
                if payout.net_amount >= Decimal('10.00'):  # Minimum amount
                    return {
                        'success': True,
                        'transaction_id': f'BT_{uuid4().hex[:8].upper()}',
                        'processing_time': 1-3  # days
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Amount below minimum for bank transfer'
                    }
                    
            elif payout.payment_method == 'paypal':
                # Simulate PayPal transfer
                return {
                    'success': True,
                    'transaction_id': f'PP_{uuid4().hex[:8].upper()}',
                    'processing_time': 0  # immediate
                }
                
            elif payout.payment_method == 'crypto':
                # Simulate cryptocurrency transfer
                return {
                    'success': True,
                    'transaction_id': f'CR_{uuid4().hex[:8].upper()}',
                    'processing_time': 0.1  # minutes
                }
                
            else:
                return {
                    'success': False,
                    'error': f'Unsupported payment method: {payout.payment_method}'
                }
                
        except Exception as e:
            logger.error(f"Error executing payment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
            
    async def process_scheduled_payouts(self) -> Dict[str, Any]:
        """Process all scheduled payouts."""
        try:
            current_time = datetime.utcnow()
            
            # Find payouts ready for processing
            ready_payouts = [
                payout for payout in self.payouts.values()
                if payout.payout_status == PayoutStatus.PENDING
                and payout.scheduled_date <= current_time
            ]
            
            processed_count = 0
            failed_count = 0
            results = []
            
            for payout in ready_payouts:
                result = await self.process_payout(payout.id)
                results.append(result)
                
                if result.get('status') == 'success':
                    processed_count += 1
                else:
                    failed_count += 1
                    
            return {
                'total_scheduled': len(ready_payouts),
                'processed_successfully': processed_count,
                'failed': failed_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error processing scheduled payouts: {e}")
            return {'error': str(e)}
            
    async def get_payout_summary(
        self,
        recipient_id: UUID,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get payout summary for recipient."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Filter payouts for recipient in time period
            recipient_payouts = [
                payout for payout in self.payouts.values()
                if payout.recipient_id == recipient_id
                and start_date <= payout.created_at <= end_date
            ]
            
            # Calculate summary statistics
            total_payouts = len(recipient_payouts)
            completed_payouts = len([p for p in recipient_payouts if p.payout_status == PayoutStatus.COMPLETED])
            pending_payouts = len([p for p in recipient_payouts if p.payout_status == PayoutStatus.PENDING])
            failed_payouts = len([p for p in recipient_payouts if p.payout_status == PayoutStatus.FAILED])
            
            total_amount = sum(p.net_amount for p in recipient_payouts)
            completed_amount = sum(
                p.net_amount for p in recipient_payouts 
                if p.payout_status == PayoutStatus.COMPLETED
            )
            pending_amount = sum(
                p.net_amount for p in recipient_payouts 
                if p.payout_status == PayoutStatus.PENDING
            )
            
            # Group by payout type
            payout_by_type = {}
            for payout in recipient_payouts:
                payout_type = payout.payout_type.value
                if payout_type not in payout_by_type:
                    payout_by_type[payout_type] = {
                        'count': 0,
                        'total_amount': Decimal('0.00'),
                        'completed_amount': Decimal('0.00')
                    }
                    
                payout_by_type[payout_type]['count'] += 1
                payout_by_type[payout_type]['total_amount'] += payout.net_amount
                
                if payout.payout_status == PayoutStatus.COMPLETED:
                    payout_by_type[payout_type]['completed_amount'] += payout.net_amount
                    
            return {
                'recipient_id': recipient_id,
                'time_period_days': time_period.days,
                'summary': {
                    'total_payouts': total_payouts,
                    'completed_payouts': completed_payouts,
                    'pending_payouts': pending_payouts,
                    'failed_payouts': failed_payouts,
                    'completion_rate': completed_payouts / total_payouts if total_payouts > 0 else 0.0
                },
                'amounts': {
                    'total_amount': float(total_amount),
                    'completed_amount': float(completed_amount),
                    'pending_amount': float(pending_amount),
                    'completion_percentage': float(completed_amount / total_amount) if total_amount > 0 else 0.0
                },
                'by_type': {
                    payout_type: {
                        'count': data['count'],
                        'total_amount': float(data['total_amount']),
                        'completed_amount': float(data['completed_amount'])
                    }
                    for payout_type, data in payout_by_type.items()
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting payout summary: {e}")
            return {'error': str(e)}


# Example usage and testing
async def main():
    """Test protection payout management functionality."""
    manager = ProtectionPayoutManager()
    
    # Register service provider
    provider_data = {
        'name': 'Elite Protection Services',
        'service_types': ['copyright_monitoring', 'piracy_detection', 'takedown_services'],
        'fee_structure': manager.fee_structures['premium_recovery'],
        'success_rate': 0.85,
        'average_recovery_time': 14.0,
        'minimum_payout': '25.00',
        'payout_frequency': 'monthly',
        'payment_methods': ['bank_transfer', 'paypal']
    }
    
    provider = await manager.register_service_provider(provider_data)
    print(f"Registered service provider: {provider.id}")
    
    # Create protection case
    case_data = {
        'content_id': str(uuid4()),
        'rights_holder_id': str(uuid4()),
        'service_provider_id': str(provider.id),
        'case_type': 'piracy_detection',
        'case_description': 'Unauthorized distribution on peer-to-peer networks'
    }
    
    case = await manager.create_protection_case(case_data)
    print(f"Created protection case: {case.id}")
    
    # Resolve case with recovery
    resolution_data = {
        'status': 'resolved',
        'recovered_amount': '500.00',
        'service_cost': '100.00'
    }
    
    calculation = await manager.resolve_protection_case(case.id, resolution_data)
    print(f"Case resolved with calculation: {calculation.calculation_breakdown}")
    
    # Process scheduled payouts
    payout_results = await manager.process_scheduled_payouts()
    print(f"Payout processing results: {payout_results}")
    
    # Get payout summary
    summary = await manager.get_payout_summary(case.rights_holder_id)
    print(f"Payout summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())