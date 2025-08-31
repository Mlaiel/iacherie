"""🚀 Revenue Distributor - Ultra-Advanced Revenue Distribution System
=================================================================

Industrial-grade revenue distribution system handling automated payouts,
multi-currency transactions, tax withholdings, and complex revenue sharing
across creators, collaborators, and platforms.

Created by: Fahed Mlaiel <mlaiel@live.de>
© 2025 Fahed Mlaiel. All rights reserved.

Team Specialists:
- Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️ STRICT COPYRIGHT WARNING - UNAUTHORIZED USE PROHIBITED ⚠️
Contact mlaiel@live.de for licensing inquiries.

Business Logic: Multi-Format Upload → AI Protection → SEO → Collaboration → Revenue Distribution
==============================================================================================
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import uuid
import json
from concurrent.futures import ThreadPoolExecutor

from ...core.database import DatabaseManager
from ...core.security import SecurityManager
from ...core.monitoring import MetricsCollector
from ...integrations.payment.stripe_processor import StripeProcessor
from ...integrations.payment.paypal_processor import PayPalProcessor
from ...integrations.payment.wise_processor import WiseProcessor
from ...integrations.banking.bank_transfer import BankTransferProcessor

logger = logging.getLogger(__name__)


class DistributionStatus(Enum):
    """Revenue distribution status"""    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"
    PARTIALLY_COMPLETED = "partially_completed"


class PaymentMethod(Enum):
    """Supported payment methods"""    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    WISE = "wise"
    CRYPTOCURRENCY = "cryptocurrency"
    CHECK = "check"


class DistributionFrequency(Enum):
    """Revenue distribution frequency options"""    IMMEDIATE = "immediate"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"


@dataclass
class RevenueShare:
    """Revenue share configuration"""    recipient_id: str
    recipient_type: str  # creator, collaborator, platform, agency
    share_percentage: Decimal
    minimum_amount: Decimal = Decimal('5.00')
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DistributionRecord:
    """Revenue distribution record"""    distribution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_revenue_id: str = ""
    creator_id: str = ""
    total_amount: Decimal = Decimal('0')
    distribution_date: datetime = field(default_factory=datetime.utcnow)
    status: DistributionStatus = DistributionStatus.PENDING
    shares: List[RevenueShare] = field(default_factory=list)
    fees: Dict[str, Decimal] = field(default_factory=dict)
    taxes_withheld: Dict[str, Decimal] = field(default_factory=dict)
    payment_details: Dict[str, Any] = field(default_factory=dict)
    error_messages: List[str] = field(default_factory=list)
    completed_at: Optional[datetime] = None


@dataclass
class PayoutInstruction:
    """Individual payout instruction"""    payout_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recipient_id: str = ""
    amount: Decimal = Decimal('0')
    currency: str = "USD"
    payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER
    destination_details: Dict[str, Any] = field(default_factory=dict)
    status: DistributionStatus = DistributionStatus.PENDING
    transaction_id: Optional[str] = None
    processing_fee: Decimal = Decimal('0')
    exchange_rate: Optional[Decimal] = None


class RevenueDistributor:
    """    Ultra-advanced revenue distribution system for content creators
    
    Features:
    - Automated revenue distribution with complex sharing rules
    - Multi-currency support with real-time exchange rates
    - Multiple payment methods and processors
    - Tax withholding and compliance management
    - Fraud detection and security measures
    - Real-time payout tracking and notifications
    - Batch processing for efficiency
    - International banking support
    """    
    def __init__(self,
                 db_manager: DatabaseManager,
                 security_manager: SecurityManager,
                 metrics_collector: MetricsCollector):
        self.db = db_manager
        self.security = security_manager
        self.metrics = metrics_collector
        
        # Payment processors
        self.payment_processors = {
            PaymentMethod.STRIPE: StripeProcessor(),
            PaymentMethod.PAYPAL: PayPalProcessor(),
            PaymentMethod.WISE: WiseProcessor(),
            PaymentMethod.BANK_TRANSFER: BankTransferProcessor()
        }
        
        # Distribution configuration
        self._distribution_configs = {}
        self._exchange_rates = {}
        self._processing_fees = {}
        
        # Security and compliance
        self._compliance_rules = {}
        self._fraud_detection = {}
        
    async def initialize(self):
        """Initialize the revenue distribution system"""        try:
            # Initialize payment processors
            for processor in self.payment_processors.values():
                await processor.initialize()
            
            # Load distribution configurations
            await self._load_distribution_configurations()
            
            # Load exchange rates
            await self._load_exchange_rates()
            
            # Initialize compliance rules
            await self._load_compliance_rules()
            
            # Setup fraud detection
            await self._setup_fraud_detection()
            
            logger.info("Revenue distributor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize revenue distributor: {e}")
            raise

    async def distribute_revenue(self,
                               revenue_id: str,
                               creator_id: str,
                               total_amount: Decimal,
                               currency: str = "USD",
                               distribution_rules: Optional[Dict[str, Any]] = None) -> DistributionRecord:
        """        Distribute revenue according to configured rules
        
        Args:
            revenue_id: Source revenue identifier
            creator_id: Creator ID
            total_amount: Total amount to distribute
            currency: Currency of the amount
            distribution_rules: Custom distribution rules
            
        Returns:
            Distribution record with all payout details
        """        try:
            # Validate distribution request
            await self._validate_distribution_request(revenue_id, creator_id, total_amount)
            
            # Get distribution configuration for creator
            dist_config = await self._get_distribution_config(creator_id, distribution_rules)
            
            # Calculate revenue shares
            revenue_shares = await self._calculate_revenue_shares(
                creator_id, total_amount, currency, dist_config
            )
            
            # Calculate taxes and fees
            taxes_withheld = await self._calculate_tax_withholdings(
                creator_id, revenue_shares, currency
            )
            
            fees = await self._calculate_distribution_fees(revenue_shares)
            
            # Create distribution record
            distribution = DistributionRecord(
                source_revenue_id=revenue_id,
                creator_id=creator_id,
                total_amount=total_amount,
                shares=revenue_shares,
                fees=fees,
                taxes_withheld=taxes_withheld,
                status=DistributionStatus.PENDING
            )
            
            # Store distribution record
            await self._store_distribution_record(distribution)
            
            # Execute distribution
            await self._execute_distribution(distribution)
            
            # Update metrics
            await self.metrics.record_revenue_distribution(distribution)
            
            logger.info(f"Revenue distribution {distribution.distribution_id} initiated for creator {creator_id}")
            return distribution
            
        except Exception as e:
            logger.error(f"Revenue distribution failed: {e}")
            raise

    async def process_bulk_distributions(self,
                                       distributions: List[Dict[str, Any]],
                                       batch_size: int = 50) -> Dict[str, Any]:
        """        Process multiple revenue distributions in batches
        
        Args:
            distributions: List of distribution requests
            batch_size: Number of distributions to process per batch
            
        Returns:
            Bulk processing results
        """        try:
            results = {
                'total_distributions': len(distributions),
                'successful': 0,
                'failed': 0,
                'batch_results': [],
                'errors': []
            }
            
            # Process in batches
            for i in range(0, len(distributions), batch_size):
                batch = distributions[i:i + batch_size]
                batch_result = await self._process_distribution_batch(batch, i // batch_size + 1)
                
                results['batch_results'].append(batch_result)
                results['successful'] += batch_result['successful']
                results['failed'] += batch_result['failed']
                results['errors'].extend(batch_result['errors'])
                
                # Brief pause between batches to avoid overwhelming processors
                if i + batch_size < len(distributions):
                    await asyncio.sleep(2)
            
            # Generate batch processing report
            await self._generate_batch_report(results)
            
            logger.info(f"Bulk distribution processing completed: {results['successful']}/{results['total_distributions']} successful")
            return results
            
        except Exception as e:
            logger.error(f"Bulk distribution processing failed: {e}")
            raise

    async def _process_distribution_batch(self,
                                        batch: List[Dict[str, Any]],
                                        batch_number: int) -> Dict[str, Any]:
        """Process a single batch of distributions"""        batch_result = {
            'batch_number': batch_number,
            'batch_size': len(batch),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'processing_time': 0
        }
        
        start_time = datetime.utcnow()
        
        try:
            # Process distributions concurrently within the batch
            tasks = []
            for dist_request in batch:
                task = self.distribute_revenue(
                    revenue_id=dist_request['revenue_id'],
                    creator_id=dist_request['creator_id'],
                    total_amount=Decimal(str(dist_request['total_amount'])),
                    currency=dist_request.get('currency', 'USD'),
                    distribution_rules=dist_request.get('distribution_rules')
                )
                tasks.append(task)
            
            # Wait for all distributions in batch to complete
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    batch_result['failed'] += 1
                    batch_result['errors'].append({
                        'request_index': i,
                        'error': str(result),
                        'revenue_id': batch[i].get('revenue_id')
                    })
                else:
                    batch_result['successful'] += 1
            
            batch_result['processing_time'] = (datetime.utcnow() - start_time).total_seconds()
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch {batch_number} processing failed: {e}")
            batch_result['failed'] = len(batch)
            batch_result['errors'].append({
                'batch_error': str(e)
            })
            return batch_result

    async def _execute_distribution(self, distribution: DistributionRecord):
        """Execute the actual revenue distribution"""        try:
            distribution.status = DistributionStatus.PROCESSING
            await self._update_distribution_status(distribution.distribution_id, distribution.status)
            
            # Generate payout instructions for each share
            payout_instructions = await self._generate_payout_instructions(distribution)
            
            # Execute payouts concurrently
            payout_results = await self._execute_payouts(payout_instructions)
            
            # Process payout results
            successful_payouts = 0
            failed_payouts = 0
            
            for instruction, result in payout_results.items():
                if result['success']:
                    successful_payouts += 1
                    # Update transaction details
                    distribution.payment_details[instruction] = result
                else:
                    failed_payouts += 1
                    distribution.error_messages.append(
                        f"Payout {instruction} failed: {result.get('error', 'Unknown error')}"
                    )
            
            # Determine final status
            if failed_payouts == 0:
                distribution.status = DistributionStatus.COMPLETED
                distribution.completed_at = datetime.utcnow()
            elif successful_payouts > 0:
                distribution.status = DistributionStatus.PARTIALLY_COMPLETED
            else:
                distribution.status = DistributionStatus.FAILED
            
            # Update distribution record
            await self._update_distribution_record(distribution)
            
            # Send notifications
            await self._send_distribution_notifications(distribution)
            
        except Exception as e:
            logger.error(f"Distribution execution failed: {e}")
            distribution.status = DistributionStatus.FAILED
            distribution.error_messages.append(f"Execution error: {str(e)}")
            await self._update_distribution_record(distribution)

    async def _calculate_revenue_shares(self,
                                      creator_id: str,
                                      total_amount: Decimal,
                                      currency: str,
                                      dist_config: Dict[str, Any]) -> List[RevenueShare]:
        """Calculate revenue shares for all recipients"""        try:
            shares = []
            
            # Get base revenue sharing rules
            sharing_rules = dist_config.get('sharing_rules', {})
            
            # Creator's base share (after platform fees and commissions)
            creator_share_percentage = Decimal(str(sharing_rules.get('creator_share', '70.0')))
            creator_share_amount = total_amount * (creator_share_percentage / Decimal('100'))
            
            # Get creator payment preferences
            creator_payment_prefs = await self._get_payment_preferences(creator_id)
            
            shares.append(RevenueShare(
                recipient_id=creator_id,
                recipient_type="creator",
                share_percentage=creator_share_percentage,
                payment_method=PaymentMethod(creator_payment_prefs.get('preferred_method', 'bank_transfer')),
                currency=creator_payment_prefs.get('preferred_currency', currency),
                metadata={
                    'amount': creator_share_amount,
                    'is_primary_creator': True
                }
            ))
            
            # Calculate collaborator shares
            collaborators = sharing_rules.get('collaborators', [])
            for collab in collaborators:
                collab_percentage = Decimal(str(collab['percentage']))
                collab_amount = total_amount * (collab_percentage / Decimal('100'))
                
                # Get collaborator payment preferences
                collab_payment_prefs = await self._get_payment_preferences(collab['user_id'])
                
                shares.append(RevenueShare(
                    recipient_id=collab['user_id'],
                    recipient_type="collaborator",
                    share_percentage=collab_percentage,
                    payment_method=PaymentMethod(collab_payment_prefs.get('preferred_method', 'bank_transfer')),
                    currency=collab_payment_prefs.get('preferred_currency', currency),
                    metadata={
                        'amount': collab_amount,
                        'collaboration_type': collab.get('type', 'general'),
                        'collaboration_id': collab.get('collaboration_id')
                    }
                ))
            
            # Platform commission (if applicable)
            platform_commission = Decimal(str(sharing_rules.get('platform_commission', '5.0')))
            if platform_commission > 0:
                platform_amount = total_amount * (platform_commission / Decimal('100'))
                
                shares.append(RevenueShare(
                    recipient_id="platform",
                    recipient_type="platform",
                    share_percentage=platform_commission,
                    payment_method=PaymentMethod.BANK_TRANSFER,
                    currency=currency,
                    metadata={
                        'amount': platform_amount,
                        'commission_type': 'platform_fee'
                    }
                ))
            
            # Validate total percentages don't exceed 100%
            total_percentage = sum(share.share_percentage for share in shares)
            if total_percentage > Decimal('100'):
                raise ValueError(f"Total revenue shares exceed 100%: {total_percentage}%")
            
            return shares
            
        except Exception as e:
            logger.error(f"Revenue share calculation failed: {e}")
            raise

    async def _calculate_tax_withholdings(self,
                                        creator_id: str,
                                        revenue_shares: List[RevenueShare],
                                        currency: str) -> Dict[str, Decimal]:
        """Calculate tax withholdings for each recipient"""        try:
            tax_withholdings = {}
            
            for share in revenue_shares:
                # Skip platform shares for tax calculations
                if share.recipient_type == "platform":
                    continue
                
                # Get recipient tax information
                tax_info = await self._get_tax_information(share.recipient_id)
                
                if not tax_info:
                    continue
                
                # Calculate tax withholding based on jurisdiction and type
                tax_rate = await self._calculate_tax_rate(
                    tax_info['country'],
                    tax_info['tax_status'],
                    share.recipient_type,
                    currency
                )
                
                if tax_rate > 0:
                    gross_amount = share.metadata.get('amount', Decimal('0'))
                    withholding_amount = gross_amount * tax_rate
                    
                    tax_withholdings[share.recipient_id] = {
                        'amount': withholding_amount,
                        'rate': tax_rate,
                        'country': tax_info['country'],
                        'tax_id': tax_info.get('tax_id')
                    }
            
            return tax_withholdings
            
        except Exception as e:
            logger.error(f"Tax withholding calculation failed: {e}")
            return {}

    async def _calculate_distribution_fees(self, revenue_shares: List[RevenueShare]) -> Dict[str, Decimal]:
        """Calculate distribution processing fees"""        try:
            fees = {
                'payment_processing': Decimal('0'),
                'currency_conversion': Decimal('0'),
                'international_transfer': Decimal('0'),
                'total': Decimal('0')
            }
            
            for share in revenue_shares:
                amount = share.metadata.get('amount', Decimal('0'))
                payment_method = share.payment_method
                
                # Get processor-specific fees
                processor = self.payment_processors.get(payment_method)
                if processor:
                    processing_fee = await processor.calculate_fee(amount, share.currency)
                    fees['payment_processing'] += processing_fee
                
                # Currency conversion fees
                if share.currency != 'USD':  # Assuming USD is base currency
                    conversion_fee = amount * Decimal('0.015')  # 1.5% conversion fee
                    fees['currency_conversion'] += conversion_fee
                
                # International transfer fees
                if share.recipient_type != "platform":
                    recipient_country = await self._get_recipient_country(share.recipient_id)
                    if recipient_country and recipient_country not in ['US', 'CA']:
                        intl_fee = min(amount * Decimal('0.005'), Decimal('25.00'))  # 0.5% or max $25
                        fees['international_transfer'] += intl_fee
            
            fees['total'] = sum(fees[key] for key in fees if key != 'total')
            return fees
            
        except Exception as e:
            logger.error(f"Distribution fee calculation failed: {e}")
            return {'total': Decimal('0')}

    async def _generate_payout_instructions(self, distribution: DistributionRecord) -> List[PayoutInstruction]:
        """Generate individual payout instructions for each recipient"""        try:
            payout_instructions = []
            
            for share in distribution.shares:
                # Skip platform shares (handled internally)
                if share.recipient_type == "platform":
                    continue
                
                gross_amount = share.metadata.get('amount', Decimal('0'))
                
                # Subtract tax withholding if applicable
                tax_withholding = distribution.taxes_withheld.get(share.recipient_id, {})
                tax_amount = tax_withholding.get('amount', Decimal('0'))
                
                net_amount = gross_amount - tax_amount
                
                # Skip if net amount is below minimum threshold
                if net_amount < share.minimum_amount:
                    logger.warning(f"Payout amount {net_amount} below minimum {share.minimum_amount} for {share.recipient_id}")
                    continue
                
                # Get recipient payout details
                payout_details = await self._get_payout_details(
                    share.recipient_id, share.payment_method
                )
                
                # Calculate processing fee
                processor = self.payment_processors.get(share.payment_method)
                processing_fee = await processor.calculate_fee(net_amount, share.currency) if processor else Decimal('0')
                
                # Create payout instruction
                instruction = PayoutInstruction(
                    recipient_id=share.recipient_id,
                    amount=net_amount - processing_fee,  # Net of processing fees
                    currency=share.currency,
                    payment_method=share.payment_method,
                    destination_details=payout_details,
                    processing_fee=processing_fee
                )
                
                # Handle currency conversion if needed
                if share.currency != 'USD':
                    exchange_rate = await self._get_exchange_rate('USD', share.currency)
                    instruction.exchange_rate = exchange_rate
                    instruction.amount = instruction.amount * exchange_rate
                
                payout_instructions.append(instruction)
            
            return payout_instructions
            
        except Exception as e:
            logger.error(f"Payout instruction generation failed: {e}")
            raise

    async def _execute_payouts(self, instructions: List[PayoutInstruction]) -> Dict[str, Dict[str, Any]]:
        """Execute all payout instructions"""        results = {}
        
        try:
            # Group instructions by payment method for batch processing
            grouped_instructions = {}
            for instruction in instructions:
                method = instruction.payment_method
                if method not in grouped_instructions:
                    grouped_instructions[method] = []
                grouped_instructions[method].append(instruction)
            
            # Execute payouts by payment method
            for method, method_instructions in grouped_instructions.items():
                processor = self.payment_processors.get(method)
                if not processor:
                    for instruction in method_instructions:
                        results[instruction.payout_id] = {
                            'success': False,
                            'error': f'Payment processor not available for {method.value}'
                        }
                    continue
                
                # Process payouts for this method
                method_results = await self._process_payment_method_payouts(
                    processor, method_instructions
                )
                results.update(method_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Payout execution failed: {e}")
            # Mark all as failed
            for instruction in instructions:
                results[instruction.payout_id] = {
                    'success': False,
                    'error': f'Execution failed: {str(e)}'
                }
            return results

    async def _process_payment_method_payouts(self,
                                            processor,
                                            instructions: List[PayoutInstruction]) -> Dict[str, Dict[str, Any]]:
        """Process payouts for a specific payment method"""        results = {}
        
        try:
            # Execute payouts concurrently for this payment method
            tasks = []
            for instruction in instructions:
                task = self._execute_single_payout(processor, instruction)
                tasks.append(task)
            
            # Wait for all payouts to complete
            payout_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(payout_results):
                instruction = instructions[i]
                
                if isinstance(result, Exception):
                    results[instruction.payout_id] = {
                        'success': False,
                        'error': str(result),
                        'instruction': instruction
                    }
                else:
                    results[instruction.payout_id] = result
            
            return results
            
        except Exception as e:
            logger.error(f"Payment method payout processing failed: {e}")
            # Mark all instructions as failed
            for instruction in instructions:
                results[instruction.payout_id] = {
                    'success': False,
                    'error': f'Method processing failed: {str(e)}'
                }
            return results

    async def _execute_single_payout(self, processor, instruction: PayoutInstruction) -> Dict[str, Any]:
        """Execute a single payout instruction"""        try:
            # Validate payout before execution
            validation_result = await processor.validate_payout(
                instruction.amount,
                instruction.currency,
                instruction.destination_details
            )
            
            if not validation_result['valid']:
                return {
                    'success': False,
                    'error': f"Payout validation failed: {validation_result['error']}",
                    'instruction': instruction
                }
            
            # Execute the payout
            payout_result = await processor.execute_payout(
                recipient_id=instruction.recipient_id,
                amount=instruction.amount,
                currency=instruction.currency,
                destination=instruction.destination_details,
                metadata={
                    'payout_id': instruction.payout_id,
                    'distribution_context': 'revenue_sharing'
                }
            )
            
            if payout_result['success']:
                # Update instruction with transaction details
                instruction.status = DistributionStatus.COMPLETED
                instruction.transaction_id = payout_result.get('transaction_id')
                
                return {
                    'success': True,
                    'transaction_id': payout_result.get('transaction_id'),
                    'processor_reference': payout_result.get('reference'),
                    'processed_at': datetime.utcnow().isoformat(),
                    'instruction': instruction
                }
            else:
                instruction.status = DistributionStatus.FAILED
                return {
                    'success': False,
                    'error': payout_result.get('error', 'Unknown payout error'),
                    'instruction': instruction
                }
                
        except Exception as e:
            logger.error(f"Single payout execution failed: {e}")
            instruction.status = DistributionStatus.FAILED
            return {
                'success': False,
                'error': str(e),
                'instruction': instruction
            }

    async def get_distribution_status(self, distribution_id: str) -> Dict[str, Any]:
        """Get detailed status of a revenue distribution"""        try:
            # Get distribution record
            distribution_data = await self.db.fetch_one("""                SELECT * FROM revenue_distributions 
                WHERE distribution_id = %s
            """, (distribution_id,))
            
            if not distribution_data:
                raise ValueError(f"Distribution {distribution_id} not found")
            
            # Get payout details
            payout_details = await self.db.fetch_all("""                SELECT * FROM revenue_payouts 
                WHERE distribution_id = %s
                ORDER BY created_at DESC
            """, (distribution_id,))
            
            return {
                'distribution_id': distribution_id,
                'status': distribution_data['status'],
                'total_amount': float(distribution_data['total_amount']),
                'currency': distribution_data['currency'],
                'created_at': distribution_data['created_at'].isoformat(),
                'completed_at': distribution_data['completed_at'].isoformat() if distribution_data['completed_at'] else None,
                'shares_count': len(json.loads(distribution_data['shares'])),
                'successful_payouts': len([p for p in payout_details if p['status'] == 'completed']),
                'failed_payouts': len([p for p in payout_details if p['status'] == 'failed']),
                'total_fees': float(distribution_data['total_fees']),
                'error_messages': json.loads(distribution_data.get('error_messages', '[]')),
                'payout_details': [
                    {
                        'payout_id': payout['payout_id'],
                        'recipient_id': payout['recipient_id'],
                        'amount': float(payout['amount']),
                        'status': payout['status'],
                        'transaction_id': payout['transaction_id'],
                        'payment_method': payout['payment_method'],
                        'processed_at': payout['processed_at'].isoformat() if payout['processed_at'] else None
                    }
                    for payout in payout_details
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get distribution status: {e}")
            raise

    # Additional helper methods would be implemented here...
    # (Due to length constraints, showing key structure and main methods)

    async def cleanup(self):
        """Cleanup distribution resources"""        try:
            # Close all payment processor connections
            for processor in self.payment_processors.values():
                if hasattr(processor, 'cleanup'):
                    await processor.cleanup()
            
            logger.info("Revenue distributor cleanup completed")
            
        except Exception as e:
            logger.error(f"Revenue distributor cleanup failed: {e}")
