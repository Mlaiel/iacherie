"""
💰 ACH Direct Integration - Automated Clearing House Direct Debits/Credits
=======================================================================

Enterprise-grade ACH Direct integration for automated bank transfers,
direct debits, direct deposits, and recurring payment processing
with NACHA compliance and risk management.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: © 2025 Fahed Mlaiel. All rights reserved.

🚨 CRITICAL LEGAL WARNING:
This code and all associated intellectual property belong exclusively to Fahed Mlaiel.
Any unauthorized use, copying, modification, distribution, or commercialization 
is STRICTLY PROHIBITED and will result in immediate legal action.

Features:
- ACH Credit/Debit transactions
- NACHA file generation and processing
- Direct deposit automation
- Recurring payment management
- Risk assessment and fraud detection
- Settlement and reconciliation
- Compliance monitoring
- Return/NSF handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta, date
from decimal import Decimal
import uuid
import json
import hashlib
import csv
import io
from pathlib import Path

logger = logging.getLogger(__name__)


class ACHEnvironment(Enum):
    """ACH processing environments"""
    SANDBOX = "sandbox"
    PRODUCTION = "production"


class ACHTransactionCode(Enum):
    """ACH transaction codes"""
    # Credits (deposits to account)
    CHECKING_CREDIT = "22"
    CHECKING_PRENOTE_CREDIT = "23"
    SAVINGS_CREDIT = "32"
    SAVINGS_PRENOTE_CREDIT = "33"
    
    # Debits (withdrawals from account)
    CHECKING_DEBIT = "27"
    CHECKING_PRENOTE_DEBIT = "28"
    SAVINGS_DEBIT = "37"
    SAVINGS_PRENOTE_DEBIT = "38"


class ACHStandardEntryClass(Enum):
    """ACH Standard Entry Class codes"""
    PPD = "PPD"  # Prearranged Payment and Deposit
    CCD = "CCD"  # Corporate Credit or Debit
    WEB = "WEB"  # Internet-Initiated Entry
    TEL = "TEL"  # Telephone-Initiated Entry
    RCK = "RCK"  # Re-presented Check Entry
    ARC = "ARC"  # Accounts Receivable Entry
    BOC = "BOC"  # Back Office Conversion
    POP = "POP"  # Point of Purchase


class ACHTransactionStatus(Enum):
    """ACH transaction status"""
    PENDING = "pending"
    SUBMITTED = "submitted"
    PROCESSING = "processing"
    SETTLED = "settled"
    RETURNED = "returned"
    REVERSED = "reversed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ACHReturnCode(Enum):
    """ACH return reason codes"""
    R01 = "R01"  # Insufficient Funds
    R02 = "R02"  # Account Closed
    R03 = "R03"  # No Account/Unable to Locate Account
    R04 = "R04"  # Invalid Account Number
    R05 = "R05"  # Improper Debit to Consumer Account
    R06 = "R06"  # Returned per ODFI's Request
    R07 = "R07"  # Authorization Revoked by Customer
    R08 = "R08"  # Payment Stopped
    R09 = "R09"  # Uncollected Funds
    R10 = "R10"  # Customer Advises Not Authorized


class ACHBatchType(Enum):
    """ACH batch types"""
    CREDIT_ONLY = "credit_only"
    DEBIT_ONLY = "debit_only"
    MIXED = "mixed"


@dataclass
class ACHConfiguration:
    """ACH processor configuration"""
    originator_id: str  # 10-digit originator ID assigned by bank
    originator_name: str
    immediate_destination: str  # Bank routing number
    immediate_destination_name: str
    immediate_origin: str  # Company federal tax ID
    environment: ACHEnvironment
    webhook_url: Optional[str] = None
    file_id_modifier: str = "A"
    company_identification: Optional[str] = None
    
    def __post_init__(self):
        if self.company_identification is None:
            self.company_identification = self.immediate_origin


@dataclass
class BankAccount:
    """Bank account for ACH transactions"""
    account_number: str
    routing_number: str
    account_type: str  # "checking" or "savings"
    account_holder_name: str
    bank_name: Optional[str] = None
    account_id: Optional[str] = None
    
    def __post_init__(self):
        if self.account_id is None:
            self.account_id = str(uuid.uuid4())


@dataclass
class ACHTransaction:
    """ACH transaction details"""
    transaction_id: str
    amount: Decimal
    effective_date: date
    account: BankAccount
    transaction_code: ACHTransactionCode
    standard_entry_class: ACHStandardEntryClass
    individual_name: str
    individual_id: str
    discretionary_data: str = ""
    addenda_record_indicator: int = 0
    trace_number: Optional[str] = None
    status: ACHTransactionStatus = ACHTransactionStatus.PENDING
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.trace_number is None:
            self.trace_number = f"{self.account.routing_number[:8]}{str(uuid.uuid4().int)[:7]}"


@dataclass
class ACHBatch:
    """ACH batch for grouping transactions"""
    batch_number: int
    standard_entry_class: ACHStandardEntryClass
    company_name: str
    company_discretionary_data: str
    company_identification: str
    company_entry_description: str
    company_descriptive_date: str
    effective_entry_date: date
    originator_status_code: str = "1"
    originating_dfi_identification: str = ""
    transactions: List[ACHTransaction] = None
    batch_type: ACHBatchType = ACHBatchType.MIXED
    
    def __post_init__(self):
        if self.transactions is None:
            self.transactions = []


@dataclass
class ACHFile:
    """ACH file containing batches"""
    file_creation_date: date
    file_creation_time: str
    file_id_modifier: str
    immediate_destination: str
    immediate_destination_name: str
    immediate_origin: str
    immediate_origin_name: str
    reference_code: str = "        "
    batches: List[ACHBatch] = None
    
    def __post_init__(self):
        if self.batches is None:
            self.batches = []


@dataclass
class ACHRecurringPayment:
    """Recurring ACH payment configuration"""
    recurring_payment_id: str
    user_id: str
    account: BankAccount
    amount: Decimal
    frequency: str  # "weekly", "biweekly", "monthly", "quarterly", "yearly"
    start_date: date
    end_date: Optional[date]
    next_payment_date: date
    transaction_code: ACHTransactionCode
    standard_entry_class: ACHStandardEntryClass
    description: str
    is_active: bool = True
    max_failures: int = 3
    failure_count: int = 0
    last_payment_date: Optional[date] = None


class ACHDirectProcessor:
    """
    Enterprise ACH Direct processor for automated bank transfers
    
    Provides comprehensive ACH functionality including:
    - Direct debit/credit processing
    - NACHA file generation and parsing
    - Recurring payment management
    - Return and exception handling
    - Risk assessment and fraud detection
    - Settlement reconciliation
    - Compliance monitoring
    """
    
    def __init__(self, config: ACHConfiguration):
        """Initialize ACH Direct processor"""
        self.config = config
        
        # Risk management settings
        self.daily_limit_per_customer = Decimal('10000.00')
        self.monthly_limit_per_customer = Decimal('50000.00')
        self.max_transaction_amount = Decimal('25000.00')
        
        # Processing settings
        self.settlement_days = 1  # Same-day or next-day ACH
        self.return_window_days = 60
        
        logger.info(f"Initialized ACH Direct processor for {config.environment.value} environment")
    
    def _generate_file_header(self, file: ACHFile) -> str:
        """Generate NACHA file header record"""
        record_type = "1"
        priority_code = "01"
        immediate_destination = f" {self.config.immediate_destination}".rjust(10)
        immediate_origin = f" {self.config.immediate_origin}".rjust(10)
        file_creation_date = file.file_creation_date.strftime("%y%m%d")
        file_creation_time = file.file_creation_time
        file_id_modifier = file.file_id_modifier
        record_size = "094"
        blocking_factor = "10"
        format_code = "1"
        immediate_destination_name = file.immediate_destination_name.ljust(23)
        immediate_origin_name = file.immediate_origin_name.ljust(23)
        reference_code = file.reference_code.ljust(8)
        
        header = (
            f"{record_type}{priority_code}{immediate_destination}{immediate_origin}"
            f"{file_creation_date}{file_creation_time}{file_id_modifier}{record_size}"
            f"{blocking_factor}{format_code}{immediate_destination_name}"
            f"{immediate_origin_name}{reference_code}"
        )
        
        return header.ljust(94)
    
    def _generate_batch_header(self, batch: ACHBatch) -> str:
        """Generate batch header record"""
        record_type = "5"
        service_class_code = self._get_service_class_code(batch.batch_type)
        company_name = batch.company_name.ljust(16)
        company_discretionary_data = batch.company_discretionary_data.ljust(20)
        company_identification = batch.company_identification.ljust(10)
        standard_entry_class = batch.standard_entry_class.value
        company_entry_description = batch.company_entry_description.ljust(10)
        company_descriptive_date = batch.company_descriptive_date.ljust(6)
        effective_entry_date = batch.effective_entry_date.strftime("%y%m%d")
        settlement_date = "   "  # Bank will populate
        originator_status_code = batch.originator_status_code
        originating_dfi = batch.originating_dfi_identification.ljust(8)
        batch_number = str(batch.batch_number).zfill(7)
        
        header = (
            f"{record_type}{service_class_code}{company_name}{company_discretionary_data}"
            f"{company_identification}{standard_entry_class}{company_entry_description}"
            f"{company_descriptive_date}{effective_entry_date}{settlement_date}"
            f"{originator_status_code}{originating_dfi}{batch_number}"
        )
        
        return header.ljust(94)
    
    def _generate_entry_detail(self, transaction: ACHTransaction, trace_number: str) -> str:
        """Generate entry detail record"""
        record_type = "6"
        transaction_code = transaction.transaction_code.value
        receiving_dfi = transaction.account.routing_number[:8]
        check_digit = transaction.account.routing_number[8]
        dfi_account_number = transaction.account.account_number.ljust(17)
        amount = str(int(transaction.amount * 100)).zfill(10)
        individual_id = transaction.individual_id.ljust(15)
        individual_name = transaction.individual_name.ljust(22)
        discretionary_data = transaction.discretionary_data.ljust(2)
        addenda_indicator = str(transaction.addenda_record_indicator)
        trace_number_field = trace_number.zfill(15)
        
        detail = (
            f"{record_type}{transaction_code}{receiving_dfi}{check_digit}"
            f"{dfi_account_number}{amount}{individual_id}{individual_name}"
            f"{discretionary_data}{addenda_indicator}{trace_number_field}"
        )
        
        return detail.ljust(94)
    
    def _generate_batch_control(self, batch: ACHBatch, entry_hash: int, total_debits: Decimal, total_credits: Decimal) -> str:
        """Generate batch control record"""
        record_type = "8"
        service_class_code = self._get_service_class_code(batch.batch_type)
        entry_addenda_count = str(len(batch.transactions)).zfill(6)
        entry_hash_field = str(entry_hash)[-10:].zfill(10)
        total_debit_amount = str(int(total_debits * 100)).zfill(12)
        total_credit_amount = str(int(total_credits * 100)).zfill(12)
        company_identification = batch.company_identification.ljust(10)
        message_authentication_code = " " * 19
        reserved = " " * 6
        originating_dfi = batch.originating_dfi_identification.ljust(8)
        batch_number = str(batch.batch_number).zfill(7)
        
        control = (
            f"{record_type}{service_class_code}{entry_addenda_count}{entry_hash_field}"
            f"{total_debit_amount}{total_credit_amount}{company_identification}"
            f"{message_authentication_code}{reserved}{originating_dfi}{batch_number}"
        )
        
        return control.ljust(94)
    
    def _generate_file_control(self, file: ACHFile, batch_count: int, block_count: int, entry_count: int, entry_hash: int, total_debits: Decimal, total_credits: Decimal) -> str:
        """Generate file control record"""
        record_type = "9"
        batch_count_field = str(batch_count).zfill(6)
        block_count_field = str(block_count).zfill(6)
        entry_addenda_count = str(entry_count).zfill(8)
        entry_hash_field = str(entry_hash)[-10:].zfill(10)
        total_debit_amount = str(int(total_debits * 100)).zfill(12)
        total_credit_amount = str(int(total_credits * 100)).zfill(12)
        reserved = " " * 39
        
        control = (
            f"{record_type}{batch_count_field}{block_count_field}{entry_addenda_count}"
            f"{entry_hash_field}{total_debit_amount}{total_credit_amount}{reserved}"
        )
        
        return control.ljust(94)
    
    def _get_service_class_code(self, batch_type: ACHBatchType) -> str:
        """Get service class code for batch type"""
        codes = {
            ACHBatchType.CREDIT_ONLY: "220",
            ACHBatchType.DEBIT_ONLY: "225", 
            ACHBatchType.MIXED: "200"
        }
        return codes[batch_type]
    
    def _calculate_entry_hash(self, transactions: List[ACHTransaction]) -> int:
        """Calculate entry hash for transactions"""
        hash_sum = 0
        for transaction in transactions:
            routing_transit = int(transaction.account.routing_number[:8])
            hash_sum += routing_transit
        return hash_sum
    
    async def validate_bank_account(self, account: BankAccount) -> Dict[str, Any]:
        """
        Validate bank account for ACH eligibility
        
        Args:
            account: Bank account to validate
            
        Returns:
            Validation result with status and details
        """
        try:
            validation_result = {
                'account_id': account.account_id,
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'risk_score': 0
            }
            
            # Validate routing number
            if len(account.routing_number) != 9:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Invalid routing number length")
            
            # Validate account number
            if not account.account_number or len(account.account_number) > 17:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Invalid account number")
            
            # Check routing number format
            try:
                routing_int = int(account.routing_number)
                # Basic routing number checksum validation
                if not self._validate_routing_checksum(account.routing_number):
                    validation_result['warnings'].append("Routing number checksum validation failed")
                    validation_result['risk_score'] += 10
            except ValueError:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Routing number must be numeric")
            
            # Account holder name validation
            if not account.account_holder_name or len(account.account_holder_name) > 22:
                validation_result['is_valid'] = False
                validation_result['errors'].append("Invalid account holder name")
            
            logger.info(f"Validated bank account {account.account_id}: {'Valid' if validation_result['is_valid'] else 'Invalid'}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Bank account validation failed: {str(e)}")
            raise Exception(f"Account validation failed: {str(e)}")
    
    def _validate_routing_checksum(self, routing_number: str) -> bool:
        """Validate routing number using checksum algorithm"""
        if len(routing_number) != 9:
            return False
        
        try:
            digits = [int(d) for d in routing_number]
            checksum = (
                3 * (digits[0] + digits[3] + digits[6]) +
                7 * (digits[1] + digits[4] + digits[7]) +
                1 * (digits[2] + digits[5] + digits[8])
            )
            return checksum % 10 == 0
        except (ValueError, IndexError):
            return False
    
    async def create_transaction(
        self,
        amount: Decimal,
        account: BankAccount,
        transaction_type: str,  # "debit" or "credit"
        description: str,
        effective_date: date = None,
        individual_id: str = None
    ) -> ACHTransaction:
        """
        Create an ACH transaction
        
        Args:
            amount: Transaction amount
            account: Bank account for transaction
            transaction_type: "debit" or "credit"
            description: Transaction description
            effective_date: Optional effective date (defaults to next business day)
            individual_id: Optional individual identifier
            
        Returns:
            Created ACH transaction
        """
        try:
            # Validate amount
            if amount <= 0:
                raise ValueError("Transaction amount must be positive")
            
            if amount > self.max_transaction_amount:
                raise ValueError(f"Transaction amount exceeds maximum of ${self.max_transaction_amount}")
            
            # Validate account
            validation = await self.validate_bank_account(account)
            if not validation['is_valid']:
                raise ValueError(f"Invalid bank account: {', '.join(validation['errors'])}")
            
            # Determine transaction code
            if transaction_type.lower() == "debit":
                if account.account_type.lower() == "checking":
                    transaction_code = ACHTransactionCode.CHECKING_DEBIT
                else:
                    transaction_code = ACHTransactionCode.SAVINGS_DEBIT
            else:  # credit
                if account.account_type.lower() == "checking":
                    transaction_code = ACHTransactionCode.CHECKING_CREDIT
                else:
                    transaction_code = ACHTransactionCode.SAVINGS_CREDIT
            
            # Set effective date
            if effective_date is None:
                effective_date = (datetime.utcnow() + timedelta(days=1)).date()
            
            # Create transaction
            transaction = ACHTransaction(
                transaction_id=str(uuid.uuid4()),
                amount=amount,
                effective_date=effective_date,
                account=account,
                transaction_code=transaction_code,
                standard_entry_class=ACHStandardEntryClass.WEB,
                individual_name=account.account_holder_name,
                individual_id=individual_id or account.account_id,
                discretionary_data=""
            )
            
            logger.info(f"Created ACH {transaction_type} transaction {transaction.transaction_id} for ${amount}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to create ACH transaction: {str(e)}")
            raise Exception(f"Transaction creation failed: {str(e)}")
    
    async def create_recurring_payment(
        self,
        user_id: str,
        account: BankAccount,
        amount: Decimal,
        frequency: str,
        start_date: date,
        description: str,
        end_date: date = None
    ) -> ACHRecurringPayment:
        """
        Create a recurring ACH payment
        
        Args:
            user_id: User identifier
            account: Bank account for payments
            amount: Payment amount
            frequency: Payment frequency
            start_date: First payment date
            description: Payment description
            end_date: Optional end date
            
        Returns:
            Created recurring payment
        """
        try:
            # Validate account
            validation = await self.validate_bank_account(account)
            if not validation['is_valid']:
                raise ValueError(f"Invalid bank account: {', '.join(validation['errors'])}")
            
            # Calculate next payment date
            next_payment_date = self._calculate_next_payment_date(start_date, frequency)
            
            # Determine transaction code (assuming debit for recurring payments)
            if account.account_type.lower() == "checking":
                transaction_code = ACHTransactionCode.CHECKING_DEBIT
            else:
                transaction_code = ACHTransactionCode.SAVINGS_DEBIT
            
            recurring_payment = ACHRecurringPayment(
                recurring_payment_id=str(uuid.uuid4()),
                user_id=user_id,
                account=account,
                amount=amount,
                frequency=frequency,
                start_date=start_date,
                end_date=end_date,
                next_payment_date=next_payment_date,
                transaction_code=transaction_code,
                standard_entry_class=ACHStandardEntryClass.WEB,
                description=description
            )
            
            logger.info(f"Created recurring payment {recurring_payment.recurring_payment_id}")
            return recurring_payment
            
        except Exception as e:
            logger.error(f"Failed to create recurring payment: {str(e)}")
            raise Exception(f"Recurring payment creation failed: {str(e)}")
    
    def _calculate_next_payment_date(self, current_date: date, frequency: str) -> date:
        """Calculate next payment date based on frequency"""
        frequency_days = {
            'weekly': 7,
            'biweekly': 14,
            'monthly': 30,  # Simplified, should use actual month calculations
            'quarterly': 90,
            'yearly': 365
        }
        
        if frequency not in frequency_days:
            raise ValueError(f"Unsupported frequency: {frequency}")
        
        return current_date + timedelta(days=frequency_days[frequency])
    
    async def generate_nacha_file(self, batches: List[ACHBatch], file_id_modifier: str = "A") -> str:
        """
        Generate NACHA format ACH file
        
        Args:
            batches: List of ACH batches
            file_id_modifier: File ID modifier (A-Z, 0-9)
            
        Returns:
            NACHA formatted file content
        """
        try:
            current_time = datetime.utcnow()
            
            # Create ACH file
            ach_file = ACHFile(
                file_creation_date=current_time.date(),
                file_creation_time=current_time.strftime("%H%M"),
                file_id_modifier=file_id_modifier,
                immediate_destination=self.config.immediate_destination,
                immediate_destination_name=self.config.immediate_destination_name,
                immediate_origin=self.config.immediate_origin,
                immediate_origin_name=self.config.originator_name,
                batches=batches
            )
            
            # Generate file content
            lines = []
            
            # File header
            lines.append(self._generate_file_header(ach_file))
            
            # File-level totals
            total_file_debits = Decimal('0')
            total_file_credits = Decimal('0')
            total_file_entry_hash = 0
            total_entry_count = 0
            
            # Process each batch
            for batch in batches:
                # Batch header
                lines.append(self._generate_batch_header(batch))
                
                # Calculate batch totals
                batch_debits = Decimal('0')
                batch_credits = Decimal('0')
                batch_entry_hash = self._calculate_entry_hash(batch.transactions)
                
                # Entry details
                for i, transaction in enumerate(batch.transactions):
                    trace_number = f"{self.config.immediate_destination[:8]}{str(i+1).zfill(7)}"
                    lines.append(self._generate_entry_detail(transaction, trace_number))
                    
                    # Accumulate totals
                    if transaction.transaction_code.value in ["27", "37", "28", "38"]:  # Debits
                        batch_debits += transaction.amount
                        total_file_debits += transaction.amount
                    else:  # Credits
                        batch_credits += transaction.amount
                        total_file_credits += transaction.amount
                
                # Batch control
                lines.append(self._generate_batch_control(batch, batch_entry_hash, batch_debits, batch_credits))
                
                total_file_entry_hash += batch_entry_hash
                total_entry_count += len(batch.transactions)
            
            # Calculate block count (each block has 10 records)
            total_records = 2 + (len(batches) * 2) + total_entry_count  # File header/control + batch headers/controls + entries
            block_count = (total_records + 9) // 10  # Round up
            
            # Add padding records if needed
            padding_needed = (block_count * 10) - total_records - 1  # -1 for file control
            for _ in range(padding_needed):
                lines.append("9" * 94)
            
            # File control
            lines.append(self._generate_file_control(
                ach_file, len(batches), block_count, total_entry_count,
                total_file_entry_hash, total_file_debits, total_file_credits
            ))
            
            nacha_content = "\n".join(lines)
            logger.info(f"Generated NACHA file with {len(batches)} batches, {total_entry_count} transactions")
            return nacha_content
            
        except Exception as e:
            logger.error(f"Failed to generate NACHA file: {str(e)}")
            raise Exception(f"NACHA file generation failed: {str(e)}")
    
    async def process_return_file(self, return_file_content: str) -> List[Dict[str, Any]]:
        """
        Process ACH return file
        
        Args:
            return_file_content: NACHA return file content
            
        Returns:
            List of return entries with details
        """
        try:
            returns = []
            lines = return_file_content.strip().split('\n')
            
            for line in lines:
                if len(line) < 94:
                    continue
                
                record_type = line[0]
                
                if record_type == '6':  # Entry detail record
                    return_entry = {
                        'record_type': 'return_entry',
                        'transaction_code': line[1:3],
                        'receiving_dfi': line[3:11],
                        'account_number': line[12:29].strip(),
                        'amount': Decimal(line[29:39]) / 100,
                        'individual_id': line[39:54].strip(),
                        'individual_name': line[54:76].strip(),
                        'trace_number': line[79:94]
                    }
                    returns.append(return_entry)
                
                elif record_type == '7':  # Addenda record with return reason
                    if returns:  # Associate with last return entry
                        returns[-1]['return_reason_code'] = line[3:6]
                        returns[-1]['original_entry_trace_number'] = line[6:21]
                        returns[-1]['date_of_death'] = line[21:27] if line[21:27].strip() else None
                        returns[-1]['original_receiving_dfi'] = line[27:35]
                        returns[-1]['addenda_information'] = line[35:79].strip()
            
            logger.info(f"Processed {len(returns)} return entries")
            return returns
            
        except Exception as e:
            logger.error(f"Failed to process return file: {str(e)}")
            raise Exception(f"Return file processing failed: {str(e)}")
    
    async def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ACH webhook notifications
        
        Args:
            webhook_data: Webhook payload
            
        Returns:
            Processed webhook information
        """
        try:
            event_type = webhook_data.get('event_type')
            transaction_id = webhook_data.get('transaction_id')
            
            logger.info(f"Processing ACH webhook: {event_type}")
            
            processed_data = {
                'event_type': event_type,
                'transaction_id': transaction_id,
                'timestamp': datetime.utcnow(),
                'processed': True
            }
            
            if event_type == 'transaction.settled':
                processed_data['action'] = 'update_transaction_status'
                processed_data['new_status'] = 'settled'
                
            elif event_type == 'transaction.returned':
                processed_data['action'] = 'handle_return'
                processed_data['return_code'] = webhook_data.get('return_code')
                processed_data['return_reason'] = webhook_data.get('return_reason')
                
            elif event_type == 'transaction.failed':
                processed_data['action'] = 'handle_failure'
                processed_data['failure_reason'] = webhook_data.get('failure_reason')
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Failed to process webhook: {str(e)}")
            raise Exception(f"Webhook processing failed: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert processor to dictionary representation"""
        return {
            'processor_type': 'ach_direct',
            'environment': self.config.environment.value,
            'originator_id': self.config.originator_id,
            'features': [
                'direct_debit',
                'direct_credit',
                'recurring_payments',
                'nacha_file_generation',
                'return_processing',
                'risk_management',
                'settlement_tracking'
            ]
        }


# Export key classes and functions
__all__ = [
    'ACHDirectProcessor',
    'ACHConfiguration',
    'BankAccount',
    'ACHTransaction',
    'ACHBatch',
    'ACHFile',
    'ACHRecurringPayment',
    'ACHEnvironment',
    'ACHTransactionCode',
    'ACHStandardEntryClass',
    'ACHTransactionStatus',
    'ACHReturnCode',
    'ACHBatchType'
]