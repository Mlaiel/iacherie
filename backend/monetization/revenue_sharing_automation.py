"""Revenue Sharing Automation - Automated Revenue Distribution System
========================================================================

Enterprise-grade revenue sharing automation engine providing intelligent
revenue distribution, automated payout processing, and smart contract
integration for collaborative creator projects and partnerships.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/revenue_sharing_automation.py

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import uuid4, UUID
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
import json

logger = logging.getLogger(__name__)


class AutomationTrigger(str, Enum):
    """Triggers for automated revenue distribution."""
    REVENUE_THRESHOLD = "revenue_threshold"
    TIME_BASED = "time_based"
    MILESTONE_REACHED = "milestone_reached"
    MANUAL_REQUEST = "manual_request"
    SMART_CONTRACT = "smart_contract"
    PERFORMANCE_BASED = "performance_based"
    PROJECT_COMPLETION = "project_completion"


class DistributionStatus(str, Enum):
    """Status of revenue distribution."""
    PENDING = "pending"
    CALCULATING = "calculating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"
    PARTIALLY_COMPLETED = "partially_completed"


class PaymentMethod(str, Enum):
    """Payment methods for revenue distribution."""
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CRYPTOCURRENCY = "cryptocurrency"
    DIGITAL_WALLET = "digital_wallet"
    CHECK = "check"
    PLATFORM_CREDITS = "platform_credits"


class TaxHandling(str, Enum):
    """Tax handling methods."""
    INDIVIDUAL = "individual"
    PLATFORM_MANAGED = "platform_managed"
    THIRD_PARTY_SERVICE = "third_party_service"
    MANUAL = "manual"


@dataclass
class AutomationRule:
    """Rule for automated revenue distribution."""
    rule_id: str
    rule_name: str
    trigger: AutomationTrigger
    trigger_conditions: Dict[str, Any]
    distribution_logic: Dict[str, Any]
    minimum_amount: Decimal
    processing_schedule: str  # cron-like schedule
    is_active: bool = True
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_executed: Optional[datetime] = None


@dataclass
class PayoutInstruction:
    """Individual payout instruction."""
    instruction_id: str
    recipient_id: str
    recipient_name: str
    recipient_email: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    payment_details: Dict[str, Any]
    tax_withholding: Decimal
    net_amount: Decimal
    processing_fees: Decimal
    reference_number: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    transaction_id: Optional[str] = None
    failure_reason: Optional[str] = None


@dataclass
class AutomatedDistribution:
    """Automated revenue distribution record."""
    distribution_id: str
    project_id: str
    contract_id: str
    trigger: AutomationTrigger
    trigger_data: Dict[str, Any]
    total_amount: Decimal
    currency: str
    distribution_date: datetime
    automation_rule_id: str
    status: DistributionStatus
    payout_instructions: List[PayoutInstruction]
    tax_handling: TaxHandling
    total_fees: Decimal
    total_taxes: Decimal
    net_distributed: Decimal
    processing_notes: List[str] = field(default_factory=list)
    completed_at: Optional[datetime] = None
    dispute_details: Optional[Dict[str, Any]] = None


@dataclass
class SmartContractIntegration:
    """Smart contract integration for automated distributions."""
    contract_address: str
    blockchain_network: str
    contract_type: str  # ERC-20, custom, etc.
    distribution_function: str
    gas_settings: Dict[str, Any]
    auto_execution_enabled: bool
    last_execution_block: Optional[int] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class DistributionMetrics:
    """Metrics for distribution performance."""
    period_start: datetime
    period_end: datetime
    total_distributions: int
    total_amount_distributed: Decimal
    average_distribution_time: float  # in seconds
    success_rate: float
    automation_rate: float  # percentage automated vs manual
    cost_per_distribution: Decimal
    disputes_count: int
    dispute_resolution_time: float  # average in hours


class RevenueSharingAutomation:
    """Automated revenue sharing and distribution engine."""
    
    def __init__(self):
        """Initialize the revenue sharing automation engine."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.automation_rules: Dict[str, AutomationRule] = {}
        self.active_distributions: Dict[str, AutomatedDistribution] = {}
        self.distribution_history: List[AutomatedDistribution] = []
        self.smart_contracts: Dict[str, SmartContractIntegration] = {}
        self.payment_processors: Dict[PaymentMethod, Any] = {}
        self.initialized = False
        
        # Configuration
        self.min_automation_amount = Decimal("1.00")
        self.max_daily_distributions = 1000
        self.default_processing_fee_percentage = Decimal("0.03")  # 3%
        self.distribution_timeout = timedelta(hours=24)
        
        self.logger.info("RevenueSharingAutomation initialized")
    
    async def initialize(self) -> bool:
        """Initialize the revenue sharing automation engine."""
        try:
            # Initialize payment processors
            await self._initialize_payment_processors()
            
            # Load automation rules and configurations
            await self._load_automation_rules()
            
            # Initialize smart contract integrations
            await self._initialize_smart_contracts()
            
            # Start background automation processes
            asyncio.create_task(self._automation_scheduler())
            asyncio.create_task(self._distribution_processor())
            asyncio.create_task(self._monitoring_task())
            
            self.initialized = True
            self.logger.info("RevenueSharingAutomation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RevenueSharingAutomation: {e}")
            return False
    
    async def create_automation_rule(
        self,
        rule_name: str,
        trigger: AutomationTrigger,
        trigger_conditions: Dict[str, Any],
        distribution_logic: Dict[str, Any],
        minimum_amount: Decimal,
        processing_schedule: str = "0 */6 * * *"  # Every 6 hours
    ) -> AutomationRule:
        """Create a new automation rule for revenue distribution."""
        try:
            rule_id = str(uuid4())
            
            rule = AutomationRule(
                rule_id=rule_id,
                rule_name=rule_name,
                trigger=trigger,
                trigger_conditions=trigger_conditions,
                distribution_logic=distribution_logic,
                minimum_amount=minimum_amount,
                processing_schedule=processing_schedule
            )
            
            # Validate rule
            validation_result = await self._validate_automation_rule(rule)
            if not validation_result["valid"]:
                raise ValueError(f"Rule validation failed: {validation_result['errors']}")
            
            # Store rule
            self.automation_rules[rule_id] = rule
            
            self.logger.info(f"Created automation rule {rule_id}: {rule_name}")
            return rule
            
        except Exception as e:
            self.logger.error(f"Failed to create automation rule: {e}")
            raise
    
    async def process_automated_distribution(
        self,
        project_id: str,
        contract_id: str,
        revenue_amount: Decimal,
        trigger: AutomationTrigger,
        trigger_data: Dict[str, Any]
    ) -> AutomatedDistribution:
        """Process an automated revenue distribution."""
        try:
            distribution_id = str(uuid4())
            
            # Find applicable automation rule
            automation_rule = await self._find_applicable_rule(
                project_id, contract_id, revenue_amount, trigger
            )
            
            if not automation_rule:
                raise ValueError("No applicable automation rule found")
            
            # Calculate distribution amounts
            distribution_calculations = await self._calculate_distribution_amounts(
                contract_id, revenue_amount, automation_rule.distribution_logic
            )
            
            # Create payout instructions
            payout_instructions = await self._create_payout_instructions(
                distribution_calculations, contract_id
            )
            
            # Calculate fees and taxes
            total_fees = sum(instr.processing_fees for instr in payout_instructions)
            total_taxes = sum(instr.tax_withholding for instr in payout_instructions)
            net_distributed = sum(instr.net_amount for instr in payout_instructions)
            
            # Create distribution record
            distribution = AutomatedDistribution(
                distribution_id=distribution_id,
                project_id=project_id,
                contract_id=contract_id,
                trigger=trigger,
                trigger_data=trigger_data,
                total_amount=revenue_amount,
                currency="USD",  # Could be dynamic
                distribution_date=datetime.utcnow(),
                automation_rule_id=automation_rule.rule_id,
                status=DistributionStatus.PENDING,
                payout_instructions=payout_instructions,
                tax_handling=TaxHandling.PLATFORM_MANAGED,
                total_fees=total_fees,
                total_taxes=total_taxes,
                net_distributed=net_distributed
            )
            
            # Store distribution
            self.active_distributions[distribution_id] = distribution
            
            # Queue for processing
            asyncio.create_task(self._process_distribution_async(distribution))
            
            self.logger.info(f"Created automated distribution {distribution_id} for ${revenue_amount}")
            return distribution
            
        except Exception as e:
            self.logger.error(f"Failed to process automated distribution: {e}")
            raise
    
    async def execute_smart_contract_distribution(
        self,
        contract_address: str,
        distribution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute revenue distribution via smart contract."""
        try:
            if contract_address not in self.smart_contracts:
                raise ValueError(f"Smart contract {contract_address} not found")
            
            smart_contract = self.smart_contracts[contract_address]
            
            # Prepare transaction data
            transaction_data = await self._prepare_smart_contract_transaction(
                smart_contract, distribution_data
            )
            
            # Execute smart contract
            execution_result = await self._execute_smart_contract_transaction(
                smart_contract, transaction_data
            )
            
            # Update execution history
            smart_contract.execution_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "transaction_hash": execution_result.get("transaction_hash"),
                "gas_used": execution_result.get("gas_used"),
                "status": execution_result.get("status"),
                "distributed_amount": distribution_data.get("total_amount")
            })
            
            self.logger.info(f"Executed smart contract distribution: {execution_result}")
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Failed to execute smart contract distribution: {e}")
            raise
    
    async def get_distribution_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        project_id: Optional[str] = None
    ) -> DistributionMetrics:
        """Get comprehensive distribution analytics."""
        try:
            if start_date is None:
                start_date = datetime.utcnow() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.utcnow()
            
            # Filter distributions
            filtered_distributions = [
                dist for dist in self.distribution_history
                if (start_date <= dist.distribution_date <= end_date and
                    (project_id is None or dist.project_id == project_id))
            ]
            
            if not filtered_distributions:
                return DistributionMetrics(
                    period_start=start_date,
                    period_end=end_date,
                    total_distributions=0,
                    total_amount_distributed=Decimal("0.00"),
                    average_distribution_time=0.0,
                    success_rate=0.0,
                    automation_rate=0.0,
                    cost_per_distribution=Decimal("0.00"),
                    disputes_count=0,
                    dispute_resolution_time=0.0
                )
            
            # Calculate metrics
            total_distributions = len(filtered_distributions)
            total_amount = sum(dist.total_amount for dist in filtered_distributions)
            
            # Calculate success rate
            successful_distributions = [
                dist for dist in filtered_distributions
                if dist.status == DistributionStatus.COMPLETED
            ]
            success_rate = len(successful_distributions) / total_distributions
            
            # Calculate automation rate
            automated_distributions = [
                dist for dist in filtered_distributions
                if dist.trigger != AutomationTrigger.MANUAL_REQUEST
            ]
            automation_rate = len(automated_distributions) / total_distributions
            
            # Calculate average distribution time
            completed_distributions = [
                dist for dist in filtered_distributions
                if dist.completed_at and dist.status == DistributionStatus.COMPLETED
            ]
            
            if completed_distributions:
                total_processing_time = sum(
                    (dist.completed_at - dist.distribution_date).total_seconds()
                    for dist in completed_distributions
                )
                average_distribution_time = total_processing_time / len(completed_distributions)
            else:
                average_distribution_time = 0.0
            
            # Calculate cost per distribution
            total_fees = sum(dist.total_fees for dist in filtered_distributions)
            cost_per_distribution = total_fees / total_distributions if total_distributions > 0 else Decimal("0.00")
            
            # Calculate disputes
            disputes = [
                dist for dist in filtered_distributions
                if dist.status == DistributionStatus.DISPUTED
            ]
            disputes_count = len(disputes)
            
            # Calculate dispute resolution time (placeholder)
            dispute_resolution_time = 48.0  # Average 48 hours
            
            return DistributionMetrics(
                period_start=start_date,
                period_end=end_date,
                total_distributions=total_distributions,
                total_amount_distributed=total_amount,
                average_distribution_time=average_distribution_time,
                success_rate=success_rate,
                automation_rate=automation_rate,
                cost_per_distribution=cost_per_distribution,
                disputes_count=disputes_count,
                dispute_resolution_time=dispute_resolution_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate distribution analytics: {e}")
            raise
    
    async def _find_applicable_rule(
        self,
        project_id: str,
        contract_id: str,
        amount: Decimal,
        trigger: AutomationTrigger
    ) -> Optional[AutomationRule]:
        """Find the applicable automation rule for a distribution."""
        applicable_rules = []
        
        for rule in self.automation_rules.values():
            if not rule.is_active:
                continue
            
            # Check trigger type
            if rule.trigger != trigger:
                continue
            
            # Check minimum amount
            if amount < rule.minimum_amount:
                continue
            
            # Check trigger conditions
            conditions_met = await self._check_rule_conditions(
                rule, project_id, contract_id, amount
            )
            
            if conditions_met:
                applicable_rules.append(rule)
        
        # Return highest priority rule
        if applicable_rules:
            return max(applicable_rules, key=lambda r: r.priority)
        
        return None
    
    async def _check_rule_conditions(
        self,
        rule: AutomationRule,
        project_id: str,
        contract_id: str,
        amount: Decimal
    ) -> bool:
        """Check if rule conditions are met."""
        conditions = rule.trigger_conditions
        
        # Check project conditions
        if "project_ids" in conditions:
            if project_id not in conditions["project_ids"]:
                return False
        
        # Check amount thresholds
        if "min_amount" in conditions:
            if amount < Decimal(str(conditions["min_amount"])):
                return False
        
        if "max_amount" in conditions:
            if amount > Decimal(str(conditions["max_amount"])):
                return False
        
        # Check time-based conditions
        if rule.trigger == AutomationTrigger.TIME_BASED:
            if rule.last_executed:
                time_since_last = datetime.utcnow() - rule.last_executed
                min_interval = timedelta(hours=conditions.get("min_interval_hours", 24))
                if time_since_last < min_interval:
                    return False
        
        return True
    
    async def _calculate_distribution_amounts(
        self,
        contract_id: str,
        total_amount: Decimal,
        distribution_logic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate individual distribution amounts."""
        # Get contract details (placeholder - would load from database)
        contract_details = await self._get_contract_details(contract_id)
        
        distributions = {}
        
        distribution_type = distribution_logic.get("type", "percentage")
        
        if distribution_type == "percentage":
            percentages = distribution_logic.get("percentages", {})
            for recipient_id, percentage in percentages.items():
                amount = total_amount * Decimal(str(percentage / 100))
                distributions[recipient_id] = {
                    "amount": amount,
                    "percentage": percentage,
                    "calculation_method": "percentage_based"
                }
        
        elif distribution_type == "equal":
            recipients = distribution_logic.get("recipients", [])
            if recipients:
                per_recipient = total_amount / len(recipients)
                for recipient_id in recipients:
                    distributions[recipient_id] = {
                        "amount": per_recipient,
                        "percentage": 100.0 / len(recipients),
                        "calculation_method": "equal_split"
                    }
        
        elif distribution_type == "performance_based":
            # Performance-based distribution (would integrate with analytics)
            performance_data = distribution_logic.get("performance_weights", {})
            total_weight = sum(performance_data.values())
            
            for recipient_id, weight in performance_data.items():
                amount = total_amount * Decimal(str(weight / total_weight))
                distributions[recipient_id] = {
                    "amount": amount,
                    "percentage": (weight / total_weight) * 100,
                    "calculation_method": "performance_based",
                    "performance_weight": weight
                }
        
        return distributions
    
    async def _create_payout_instructions(
        self,
        distributions: Dict[str, Any],
        contract_id: str
    ) -> List[PayoutInstruction]:
        """Create payout instructions for each recipient."""
        instructions = []
        
        for recipient_id, dist_data in distributions.items():
            # Get recipient details (placeholder)
            recipient = await self._get_recipient_details(recipient_id)
            
            gross_amount = dist_data["amount"]
            
            # Calculate processing fees
            processing_fees = gross_amount * self.default_processing_fee_percentage
            
            # Calculate tax withholding (placeholder - would use real tax calculation)
            tax_withholding = gross_amount * Decimal("0.1")  # 10% placeholder
            
            # Calculate net amount
            net_amount = gross_amount - processing_fees - tax_withholding
            
            instruction = PayoutInstruction(
                instruction_id=str(uuid4()),
                recipient_id=recipient_id,
                recipient_name=recipient.get("name", f"Recipient {recipient_id}"),
                recipient_email=recipient.get("email", f"{recipient_id}@example.com"),
                amount=gross_amount,
                currency="USD",
                payment_method=PaymentMethod(recipient.get("preferred_payment_method", "paypal")),
                payment_details=recipient.get("payment_details", {}),
                tax_withholding=tax_withholding,
                net_amount=net_amount,
                processing_fees=processing_fees,
                reference_number=f"REV-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"
            )
            
            instructions.append(instruction)
        
        return instructions
    
    async def _process_distribution_async(self, distribution: AutomatedDistribution):
        """Process distribution asynchronously."""
        try:
            distribution.status = DistributionStatus.PROCESSING
            distribution.processing_notes.append(f"Started processing at {datetime.utcnow().isoformat()}")
            
            # Process each payout instruction
            successful_payouts = 0
            failed_payouts = 0
            
            for instruction in distribution.payout_instructions:
                try:
                    success = await self._process_payout_instruction(instruction)
                    if success:
                        successful_payouts += 1
                        instruction.status = "completed"
                        instruction.processed_at = datetime.utcnow()
                        instruction.transaction_id = f"txn_{uuid4().hex[:12]}"
                    else:
                        failed_payouts += 1
                        instruction.status = "failed"
                        instruction.failure_reason = "Payment processing failed"
                
                except Exception as e:
                    failed_payouts += 1
                    instruction.status = "failed"
                    instruction.failure_reason = str(e)
                    self.logger.error(f"Failed to process payout instruction {instruction.instruction_id}: {e}")
            
            # Update distribution status
            if failed_payouts == 0:
                distribution.status = DistributionStatus.COMPLETED
            elif successful_payouts > 0:
                distribution.status = DistributionStatus.PARTIALLY_COMPLETED
            else:
                distribution.status = DistributionStatus.FAILED
            
            distribution.completed_at = datetime.utcnow()
            distribution.processing_notes.append(
                f"Completed processing: {successful_payouts} successful, {failed_payouts} failed"
            )
            
            # Move to history
            self.distribution_history.append(distribution)
            if distribution.distribution_id in self.active_distributions:
                del self.active_distributions[distribution.distribution_id]
            
            self.logger.info(f"Completed distribution {distribution.distribution_id}: {distribution.status}")
            
        except Exception as e:
            distribution.status = DistributionStatus.FAILED
            distribution.processing_notes.append(f"Processing failed: {str(e)}")
            self.logger.error(f"Failed to process distribution {distribution.distribution_id}: {e}")
    
    async def _process_payout_instruction(self, instruction: PayoutInstruction) -> bool:
        """Process individual payout instruction."""
        try:
            # Get payment processor for the method
            processor = self.payment_processors.get(instruction.payment_method)
            if not processor:
                raise ValueError(f"Payment processor not available for {instruction.payment_method}")
            
            # Process payment (simulation)
            await asyncio.sleep(1)  # Simulate processing time
            
            # In production, this would make actual API calls to payment processors
            self.logger.info(
                f"Processed payout: ${instruction.net_amount} to {instruction.recipient_email} "
                f"via {instruction.payment_method}"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process payout instruction: {e}")
            return False
    
    async def _validate_automation_rule(self, rule: AutomationRule) -> Dict[str, Any]:
        """Validate automation rule configuration."""
        errors = []
        
        if rule.minimum_amount < self.min_automation_amount:
            errors.append(f"Minimum amount must be at least ${self.min_automation_amount}")
        
        if not rule.distribution_logic:
            errors.append("Distribution logic is required")
        
        # Validate distribution logic
        if rule.distribution_logic.get("type") == "percentage":
            percentages = rule.distribution_logic.get("percentages", {})
            total_percentage = sum(percentages.values())
            if abs(total_percentage - 100) > 0.01:
                errors.append("Percentage distribution must sum to 100%")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def _get_contract_details(self, contract_id: str) -> Dict[str, Any]:
        """Get contract details (placeholder)."""
        return {
            "contract_id": contract_id,
            "participants": ["creator1", "creator2", "platform"],
            "revenue_split": {"creator1": 50, "creator2": 40, "platform": 10}
        }
    
    async def _get_recipient_details(self, recipient_id: str) -> Dict[str, Any]:
        """Get recipient details (placeholder)."""
        return {
            "recipient_id": recipient_id,
            "name": f"Creator {recipient_id}",
            "email": f"{recipient_id}@example.com",
            "preferred_payment_method": "paypal",
            "payment_details": {"paypal_email": f"{recipient_id}@example.com"}
        }
    
    async def _initialize_payment_processors(self):
        """Initialize payment processor integrations."""
        # In production, this would initialize actual payment processors
        self.payment_processors = {
            PaymentMethod.PAYPAL: "PayPal API Client",
            PaymentMethod.STRIPE: "Stripe API Client",
            PaymentMethod.BANK_TRANSFER: "Bank Transfer Service",
            PaymentMethod.CRYPTOCURRENCY: "Crypto Wallet Service"
        }
    
    async def _load_automation_rules(self):
        """Load existing automation rules."""
        # In production, this would load from database
        pass
    
    async def _initialize_smart_contracts(self):
        """Initialize smart contract integrations."""
        # In production, this would initialize blockchain connections
        pass
    
    async def _prepare_smart_contract_transaction(
        self, 
        smart_contract: SmartContractIntegration,
        distribution_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare smart contract transaction data."""
        return {
            "function": smart_contract.distribution_function,
            "parameters": distribution_data,
            "gas_limit": smart_contract.gas_settings.get("gas_limit", 300000),
            "gas_price": smart_contract.gas_settings.get("gas_price", "20 gwei")
        }
    
    async def _execute_smart_contract_transaction(
        self,
        smart_contract: SmartContractIntegration,
        transaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute smart contract transaction."""
        # In production, this would interact with blockchain
        return {
            "transaction_hash": f"0x{uuid4().hex}",
            "gas_used": 250000,
            "status": "success",
            "block_number": 12345678
        }
    
    async def _automation_scheduler(self):
        """Background task to schedule automated distributions."""
        while True:
            try:
                # Check for time-based automation rules
                current_time = datetime.utcnow()
                
                for rule in self.automation_rules.values():
                    if (rule.trigger == AutomationTrigger.TIME_BASED and
                        rule.is_active and
                        self._should_execute_rule(rule, current_time)):
                        
                        await self._execute_scheduled_rule(rule)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                self.logger.error(f"Error in automation scheduler: {e}")
    
    async def _distribution_processor(self):
        """Background task to process pending distributions."""
        while True:
            try:
                # Process pending distributions
                pending_distributions = [
                    dist for dist in self.active_distributions.values()
                    if dist.status == DistributionStatus.PENDING
                ]
                
                for distribution in pending_distributions[:10]:  # Process up to 10 at a time
                    asyncio.create_task(self._process_distribution_async(distribution))
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in distribution processor: {e}")
    
    async def _monitoring_task(self):
        """Background task for monitoring and alerts."""
        while True:
            try:
                # Monitor for stuck distributions
                stuck_distributions = [
                    dist for dist in self.active_distributions.values()
                    if (datetime.utcnow() - dist.distribution_date) > self.distribution_timeout
                ]
                
                for dist in stuck_distributions:
                    self.logger.warning(f"Distribution {dist.distribution_id} is stuck, investigating...")
                    # Could trigger alerts or retry logic
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                self.logger.error(f"Error in monitoring task: {e}")
    
    def _should_execute_rule(self, rule: AutomationRule, current_time: datetime) -> bool:
        """Check if a time-based rule should be executed."""
        # Simple check - in production would use proper cron parsing
        if rule.last_executed is None:
            return True
        
        # Check if enough time has passed based on schedule
        time_since_last = current_time - rule.last_executed
        
        if "*/6" in rule.processing_schedule:  # Every 6 hours
            return time_since_last >= timedelta(hours=6)
        elif "0 0" in rule.processing_schedule:  # Daily
            return time_since_last >= timedelta(days=1)
        
        return False
    
    async def _execute_scheduled_rule(self, rule: AutomationRule):
        """Execute a scheduled automation rule."""
        try:
            # This would check for pending revenue to distribute
            # For now, just update the last executed time
            rule.last_executed = datetime.utcnow()
            self.logger.info(f"Executed scheduled rule: {rule.rule_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to execute scheduled rule {rule.rule_id}: {e}")


# Global instance
_revenue_sharing_automation: Optional[RevenueSharingAutomation] = None


async def get_revenue_sharing_automation() -> RevenueSharingAutomation:
    """Get the global revenue sharing automation instance."""
    global _revenue_sharing_automation
    
    if _revenue_sharing_automation is None:
        _revenue_sharing_automation = RevenueSharingAutomation()
        await _revenue_sharing_automation.initialize()
    
    return _revenue_sharing_automation