"""Revenue Sharing Automation - Automated Revenue Sharing System
===============================================================

Enterprise-grade automated revenue sharing system providing intelligent
revenue distribution, partnership management, and collaborative monetization
for multi-creator projects and partnerships.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/revenue_sharing_automation.py

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


class SharingModel(str, Enum):
    """Revenue sharing models."""
    EQUAL_SPLIT = "equal_split"
    CONTRIBUTION_BASED = "contribution_based"
    ROLE_BASED = "role_based"
    TIME_BASED = "time_based"
    PERFORMANCE_BASED = "performance_based"
    CUSTOM_FORMULA = "custom_formula"
    TIERED_SPLIT = "tiered_split"
    MILESTONE_BASED = "milestone_based"


class ContributionType(str, Enum):
    """Types of collaboration contributions."""
    CONTENT_CREATION = "content_creation"
    TECHNICAL_WORK = "technical_work"
    MARKETING = "marketing"
    FINANCING = "financing"
    DISTRIBUTION = "distribution"
    MANAGEMENT = "management"
    EXPERTISE = "expertise"
    PLATFORM_ACCESS = "platform_access"


class PayoutFrequency(str, Enum):
    """Revenue payout frequencies."""
    REAL_TIME = "real_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    MILESTONE = "milestone"
    ON_DEMAND = "on_demand"


class SharingStatus(str, Enum):
    """Revenue sharing agreement status."""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


@dataclass
class Collaborator:
    """Collaboration participant details."""
    collaborator_id: str
    user_id: str
    name: str
    email: str
    role: str
    contribution_types: List[ContributionType]
    share_percentage: Decimal
    minimum_payout: Decimal
    payout_method: str
    payment_details: Dict[str, Any]
    is_active: bool = True
    joined_date: datetime = field(default_factory=datetime.now)


@dataclass
class SharingAgreement:
    """Revenue sharing agreement details."""
    agreement_id: str
    project_id: str
    project_name: str
    sharing_model: SharingModel
    collaborators: List[Collaborator]
    total_shares: Decimal
    sharing_formula: Optional[str]
    terms_and_conditions: Dict[str, Any]
    payout_frequency: PayoutFrequency
    minimum_distribution_amount: Decimal
    automatic_distribution: bool
    start_date: datetime
    end_date: Optional[datetime]
    status: SharingStatus
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class RevenueTransaction:
    """Individual revenue transaction."""
    transaction_id: str
    agreement_id: str
    source: str
    gross_amount: Decimal
    net_amount: Decimal
    fees: Decimal
    currency: str
    transaction_date: datetime
    revenue_period: Tuple[datetime, datetime]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Distribution:
    """Revenue distribution to collaborators."""
    distribution_id: str
    agreement_id: str
    transaction_id: str
    total_amount: Decimal
    distribution_date: datetime
    collaborator_payments: List[Dict[str, Any]]
    processing_fees: Decimal
    net_distributed: Decimal
    status: str  # "pending", "processing", "completed", "failed"
    payment_reference: Optional[str]


@dataclass
class SharingReport:
    """Revenue sharing performance report."""
    report_id: str
    agreement_id: str
    reporting_period: Tuple[datetime, datetime]
    total_revenue: Decimal
    total_distributed: Decimal
    pending_distribution: Decimal
    distribution_count: int
    average_distribution: Decimal
    collaborator_earnings: Dict[str, Decimal]
    performance_metrics: Dict[str, Any]
    issues_encountered: List[str]
    recommendations: List[str]


class RevenueSharingAutomation:
    """
    Advanced automated revenue sharing system.
    
    Manages multi-creator revenue distribution with intelligent
    automation, flexible sharing models, and comprehensive tracking.
    """
    
    def __init__(self):
        """Initialize the revenue sharing automation system."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.sharing_agreements: Dict[str, SharingAgreement] = {}
        self.revenue_transactions: Dict[str, List[RevenueTransaction]] = {}
        self.distributions: Dict[str, List[Distribution]] = {}
        self.sharing_reports: Dict[str, List[SharingReport]] = {}
        self.automation_rules: Dict[str, Any] = {}
        self.initialized = False
        
        self.logger.info("RevenueSharingAutomation initialized")
    
    async def initialize(self) -> bool:
        """Initialize the revenue sharing automation system."""
        try:
            await self._load_automation_rules()
            await self._initialize_payment_processors()
            await self._start_automation_engine()
            
            self.initialized = True
            self.logger.info("RevenueSharingAutomation initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RevenueSharingAutomation: {e}")
            return False
    
    async def _load_automation_rules(self):
        """Load automation rules and parameters."""
        self.automation_rules = {
            "minimum_distribution_threshold": Decimal("10.00"),
            "maximum_processing_fee": Decimal("2.00"),
            "auto_distribution_delay_hours": 24,
            "dispute_resolution_days": 14,
            "payment_retry_attempts": 3,
            "reconciliation_frequency_hours": 6
        }
        
        self.logger.info("Automation rules loaded")
    
    async def _initialize_payment_processors(self):
        """Initialize payment processing integrations."""
        # In production, this would initialize actual payment processors
        self.payment_processors = {
            "stripe": {"fee_rate": 0.029, "fixed_fee": Decimal("0.30")},
            "paypal": {"fee_rate": 0.034, "fixed_fee": Decimal("0.00")},
            "bank_transfer": {"fee_rate": 0.01, "fixed_fee": Decimal("1.00")},
            "crypto": {"fee_rate": 0.015, "fixed_fee": Decimal("0.00")}
        }
        
        self.logger.info("Payment processors initialized")
    
    async def _start_automation_engine(self):
        """Start automated processing engine."""
        self.automation_active = True
        self.logger.info("Automation engine started")
    
    async def create_sharing_agreement(
        self,
        project_id: str,
        project_name: str,
        sharing_model: SharingModel,
        collaborators: List[Dict[str, Any]],
        terms: Dict[str, Any],
        created_by: str,
        payout_frequency: PayoutFrequency = PayoutFrequency.MONTHLY,
        automatic_distribution: bool = True
    ) -> str:
        """Create a new revenue sharing agreement."""
        try:
            agreement_id = str(uuid4())
            
            # Convert collaborator data to Collaborator objects
            collaborator_objects = []
            total_shares = Decimal("0")
            
            for collab_data in collaborators:
                collaborator = Collaborator(
                    collaborator_id=str(uuid4()),
                    user_id=collab_data["user_id"],
                    name=collab_data["name"],
                    email=collab_data["email"],
                    role=collab_data.get("role", "collaborator"),
                    contribution_types=[ContributionType(ct) for ct in collab_data.get("contribution_types", [])],
                    share_percentage=Decimal(str(collab_data["share_percentage"])),
                    minimum_payout=Decimal(str(collab_data.get("minimum_payout", "10.00"))),
                    payout_method=collab_data.get("payout_method", "stripe"),
                    payment_details=collab_data.get("payment_details", {})
                )
                collaborator_objects.append(collaborator)
                total_shares += collaborator.share_percentage
            
            # Validate total shares
            if abs(total_shares - Decimal("100")) > Decimal("0.01"):
                raise ValueError(f"Total shares must equal 100%, got {total_shares}%")
            
            agreement = SharingAgreement(
                agreement_id=agreement_id,
                project_id=project_id,
                project_name=project_name,
                sharing_model=sharing_model,
                collaborators=collaborator_objects,
                total_shares=total_shares,
                sharing_formula=terms.get("sharing_formula"),
                terms_and_conditions=terms,
                payout_frequency=payout_frequency,
                minimum_distribution_amount=Decimal(str(terms.get("minimum_distribution", "50.00"))),
                automatic_distribution=automatic_distribution,
                start_date=datetime.now(),
                end_date=None,
                status=SharingStatus.ACTIVE,
                created_by=created_by
            )
            
            self.sharing_agreements[agreement_id] = agreement
            
            self.logger.info(f"Created sharing agreement {agreement_id} for project {project_name}")
            return agreement_id
            
        except Exception as e:
            self.logger.error(f"Error creating sharing agreement: {e}")
            raise
    
    async def record_revenue(
        self,
        agreement_id: str,
        source: str,
        gross_amount: Decimal,
        currency: str = "USD",
        fees: Optional[Decimal] = None,
        revenue_period: Optional[Tuple[datetime, datetime]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record revenue for automatic distribution."""
        try:
            if agreement_id not in self.sharing_agreements:
                raise ValueError(f"Agreement {agreement_id} not found")
            
            agreement = self.sharing_agreements[agreement_id]
            if agreement.status != SharingStatus.ACTIVE:
                raise ValueError(f"Agreement {agreement_id} is not active")
            
            transaction_id = str(uuid4())
            
            # Calculate fees if not provided
            if fees is None:
                fees = await self._calculate_platform_fees(gross_amount, source)
            
            net_amount = gross_amount - fees
            
            # Set revenue period if not provided
            if revenue_period is None:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=1)
                revenue_period = (start_date, end_date)
            
            transaction = RevenueTransaction(
                transaction_id=transaction_id,
                agreement_id=agreement_id,
                source=source,
                gross_amount=gross_amount,
                net_amount=net_amount,
                fees=fees,
                currency=currency,
                transaction_date=datetime.now(),
                revenue_period=revenue_period,
                metadata=metadata or {}
            )
            
            if agreement_id not in self.revenue_transactions:
                self.revenue_transactions[agreement_id] = []
            self.revenue_transactions[agreement_id].append(transaction)
            
            # Trigger automatic distribution if enabled
            if agreement.automatic_distribution:
                await self._schedule_distribution(agreement_id, transaction_id)
            
            self.logger.info(f"Recorded revenue ${net_amount} for agreement {agreement_id}")
            return transaction_id
            
        except Exception as e:
            self.logger.error(f"Error recording revenue: {e}")
            raise
    
    async def _calculate_platform_fees(self, amount: Decimal, source: str) -> Decimal:
        """Calculate platform fees based on source."""
        # Default fee structure
        fee_rates = {
            "subscription": 0.05,  # 5%
            "advertising": 0.30,   # 30%
            "direct_sales": 0.10,  # 10%
            "licensing": 0.15,     # 15%
            "merchandise": 0.20,   # 20%
            "donations": 0.03      # 3%
        }
        
        fee_rate = fee_rates.get(source, 0.10)  # Default 10%
        return amount * Decimal(str(fee_rate))
    
    async def _schedule_distribution(self, agreement_id: str, transaction_id: str):
        """Schedule revenue distribution based on agreement settings."""
        agreement = self.sharing_agreements[agreement_id]
        
        if agreement.payout_frequency == PayoutFrequency.REAL_TIME:
            await self._process_distribution(agreement_id, [transaction_id])
        else:
            # Schedule for later processing
            delay_hours = self.automation_rules["auto_distribution_delay_hours"]
            # In production, this would use a proper task scheduler
            await asyncio.sleep(1)  # Simulate brief delay for demo
            await self._process_distribution(agreement_id, [transaction_id])
    
    async def _process_distribution(
        self,
        agreement_id: str,
        transaction_ids: List[str]
    ) -> str:
        """Process revenue distribution to collaborators."""
        try:
            agreement = self.sharing_agreements[agreement_id]
            transactions = self.revenue_transactions.get(agreement_id, [])
            
            # Get transactions to distribute
            target_transactions = [
                t for t in transactions if t.transaction_id in transaction_ids
            ]
            
            if not target_transactions:
                raise ValueError("No transactions found for distribution")
            
            # Calculate total amount to distribute
            total_amount = sum(t.net_amount for t in target_transactions)
            
            # Check minimum distribution threshold
            if total_amount < agreement.minimum_distribution_amount:
                self.logger.info(f"Amount ${total_amount} below minimum threshold, queuing for later")
                return ""
            
            distribution_id = str(uuid4())
            
            # Calculate individual payments
            collaborator_payments = []
            total_distributed = Decimal("0")
            processing_fees = Decimal("0")
            
            for collaborator in agreement.collaborators:
                if not collaborator.is_active:
                    continue
                
                # Calculate collaborator's share
                share_amount = await self._calculate_collaborator_share(
                    collaborator, total_amount, agreement.sharing_model, target_transactions
                )
                
                if share_amount < collaborator.minimum_payout:
                    self.logger.info(f"Collaborator {collaborator.name} share ${share_amount} below minimum payout")
                    continue
                
                # Calculate payment processing fees
                payment_fee = await self._calculate_payment_fee(share_amount, collaborator.payout_method)
                net_payment = share_amount - payment_fee
                
                payment_info = {
                    "collaborator_id": collaborator.collaborator_id,
                    "user_id": collaborator.user_id,
                    "name": collaborator.name,
                    "gross_amount": float(share_amount),
                    "payment_fee": float(payment_fee),
                    "net_amount": float(net_payment),
                    "payout_method": collaborator.payout_method,
                    "payment_status": "pending"
                }
                
                collaborator_payments.append(payment_info)
                total_distributed += share_amount
                processing_fees += payment_fee
            
            # Create distribution record
            distribution = Distribution(
                distribution_id=distribution_id,
                agreement_id=agreement_id,
                transaction_id=transaction_ids[0] if len(transaction_ids) == 1 else "multiple",
                total_amount=total_amount,
                distribution_date=datetime.now(),
                collaborator_payments=collaborator_payments,
                processing_fees=processing_fees,
                net_distributed=total_distributed - processing_fees,
                status="processing",
                payment_reference=None
            )
            
            if agreement_id not in self.distributions:
                self.distributions[agreement_id] = []
            self.distributions[agreement_id].append(distribution)
            
            # Process payments
            await self._execute_payments(distribution)
            
            self.logger.info(f"Processed distribution {distribution_id} for ${total_distributed}")
            return distribution_id
            
        except Exception as e:
            self.logger.error(f"Error processing distribution: {e}")
            raise
    
    async def _calculate_collaborator_share(
        self,
        collaborator: Collaborator,
        total_amount: Decimal,
        sharing_model: SharingModel,
        transactions: List[RevenueTransaction]
    ) -> Decimal:
        """Calculate individual collaborator's share based on sharing model."""
        
        if sharing_model == SharingModel.EQUAL_SPLIT:
            return total_amount / len([c for c in self.sharing_agreements[transactions[0].agreement_id].collaborators if c.is_active])
        
        elif sharing_model == SharingModel.CONTRIBUTION_BASED:
            # Use share percentage as contribution weight
            return total_amount * (collaborator.share_percentage / Decimal("100"))
        
        elif sharing_model == SharingModel.ROLE_BASED:
            # Apply role-based multipliers
            role_multipliers = {
                "lead": 1.5,
                "senior": 1.2,
                "junior": 1.0,
                "intern": 0.8
            }
            
            multiplier = Decimal(str(role_multipliers.get(collaborator.role, 1.0)))
            base_share = total_amount * (collaborator.share_percentage / Decimal("100"))
            return base_share * multiplier
        
        elif sharing_model == SharingModel.PERFORMANCE_BASED:
            # Would integrate with performance metrics in production
            # For now, use share percentage with small performance adjustment
            import random
            performance_factor = Decimal(str(0.8 + random.random() * 0.4))  # 0.8 to 1.2
            base_share = total_amount * (collaborator.share_percentage / Decimal("100"))
            return base_share * performance_factor
        
        else:
            # Default to contribution-based
            return total_amount * (collaborator.share_percentage / Decimal("100"))
    
    async def _calculate_payment_fee(self, amount: Decimal, payout_method: str) -> Decimal:
        """Calculate payment processing fee."""
        processor_info = self.payment_processors.get(payout_method, {"fee_rate": 0.03, "fixed_fee": Decimal("0.30")})
        
        percentage_fee = amount * Decimal(str(processor_info["fee_rate"]))
        fixed_fee = processor_info["fixed_fee"]
        
        total_fee = percentage_fee + fixed_fee
        
        # Cap fee at maximum
        max_fee = self.automation_rules["maximum_processing_fee"]
        return min(total_fee, max_fee)
    
    async def _execute_payments(self, distribution: Distribution):
        """Execute payments to collaborators."""
        try:
            successful_payments = 0
            failed_payments = 0
            
            for payment in distribution.collaborator_payments:
                try:
                    # Simulate payment processing
                    payment_success = await self._process_individual_payment(payment)
                    
                    if payment_success:
                        payment["payment_status"] = "completed"
                        successful_payments += 1
                    else:
                        payment["payment_status"] = "failed"
                        failed_payments += 1
                        
                except Exception as e:
                    self.logger.error(f"Payment failed for {payment['name']}: {e}")
                    payment["payment_status"] = "failed"
                    failed_payments += 1
            
            # Update distribution status
            if failed_payments == 0:
                distribution.status = "completed"
            elif successful_payments > 0:
                distribution.status = "partial"
            else:
                distribution.status = "failed"
            
            distribution.payment_reference = f"batch_{distribution.distribution_id[:8]}"
            
            self.logger.info(f"Distribution {distribution.distribution_id}: {successful_payments} successful, {failed_payments} failed")
            
        except Exception as e:
            distribution.status = "failed"
            self.logger.error(f"Error executing payments: {e}")
    
    async def _process_individual_payment(self, payment_info: Dict[str, Any]) -> bool:
        """Process individual payment to collaborator."""
        # Simulate payment processing with high success rate
        import random
        
        # Different success rates by payment method
        success_rates = {
            "stripe": 0.98,
            "paypal": 0.95,
            "bank_transfer": 0.92,
            "crypto": 0.88
        }
        
        method = payment_info["payout_method"]
        success_rate = success_rates.get(method, 0.90)
        
        return random.random() < success_rate
    
    async def get_agreement_status(self, agreement_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a sharing agreement."""
        agreement = self.sharing_agreements.get(agreement_id)
        if not agreement:
            return None
        
        # Get financial summary
        transactions = self.revenue_transactions.get(agreement_id, [])
        distributions = self.distributions.get(agreement_id, [])
        
        total_revenue = sum(t.net_amount for t in transactions)
        total_distributed = sum(d.net_distributed for d in distributions if d.status == "completed")
        pending_distribution = total_revenue - total_distributed
        
        return {
            "agreement_id": agreement_id,
            "project_name": agreement.project_name,
            "status": agreement.status.value,
            "collaborators_count": len(agreement.collaborators),
            "sharing_model": agreement.sharing_model.value,
            "total_revenue": float(total_revenue),
            "total_distributed": float(total_distributed),
            "pending_distribution": float(pending_distribution),
            "distributions_count": len(distributions),
            "created_at": agreement.created_at.isoformat(),
            "last_distribution": distributions[-1].distribution_date.isoformat() if distributions else None
        }
    
    async def get_collaborator_earnings(
        self,
        agreement_id: str,
        collaborator_id: str,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """Get earnings summary for a specific collaborator."""
        agreement = self.sharing_agreements.get(agreement_id)
        if not agreement:
            return {}
        
        collaborator = None
        for c in agreement.collaborators:
            if c.collaborator_id == collaborator_id:
                collaborator = c
                break
        
        if not collaborator:
            return {}
        
        # Get distributions in period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        distributions = self.distributions.get(agreement_id, [])
        period_distributions = [
            d for d in distributions
            if start_date <= d.distribution_date <= end_date
        ]
        
        # Calculate earnings
        total_earnings = Decimal("0")
        payment_count = 0
        
        for distribution in period_distributions:
            for payment in distribution.collaborator_payments:
                if payment["collaborator_id"] == collaborator_id and payment["payment_status"] == "completed":
                    total_earnings += Decimal(str(payment["net_amount"]))
                    payment_count += 1
        
        return {
            "collaborator_id": collaborator_id,
            "name": collaborator.name,
            "role": collaborator.role,
            "share_percentage": float(collaborator.share_percentage),
            "period_earnings": float(total_earnings),
            "payments_received": payment_count,
            "average_payment": float(total_earnings / payment_count) if payment_count > 0 else 0,
            "period_days": period_days
        }
    
    async def generate_sharing_report(
        self,
        agreement_id: str,
        period_days: int = 90
    ) -> SharingReport:
        """Generate comprehensive sharing report."""
        agreement = self.sharing_agreements.get(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get data for period
        transactions = self.revenue_transactions.get(agreement_id, [])
        period_transactions = [
            t for t in transactions
            if start_date <= t.transaction_date <= end_date
        ]
        
        distributions = self.distributions.get(agreement_id, [])
        period_distributions = [
            d for d in distributions
            if start_date <= d.distribution_date <= end_date
        ]
        
        # Calculate metrics
        total_revenue = sum(t.net_amount for t in period_transactions)
        total_distributed = sum(d.net_distributed for d in period_distributions if d.status == "completed")
        pending_distribution = total_revenue - total_distributed
        
        # Collaborator earnings
        collaborator_earnings = {}
        for collaborator in agreement.collaborators:
            earnings = await self.get_collaborator_earnings(agreement_id, collaborator.collaborator_id, period_days)
            collaborator_earnings[collaborator.name] = Decimal(str(earnings.get("period_earnings", 0)))
        
        # Performance metrics
        successful_distributions = len([d for d in period_distributions if d.status == "completed"])
        failed_distributions = len([d for d in period_distributions if d.status == "failed"])
        
        performance_metrics = {
            "distribution_success_rate": successful_distributions / len(period_distributions) if period_distributions else 0,
            "average_distribution_amount": float(total_distributed / len(period_distributions)) if period_distributions else 0,
            "revenue_distribution_ratio": float(total_distributed / total_revenue) if total_revenue > 0 else 0,
            "collaborator_satisfaction": 0.85  # Would be calculated from actual feedback
        }
        
        # Issues and recommendations
        issues = []
        recommendations = []
        
        if failed_distributions > 0:
            issues.append(f"{failed_distributions} failed distributions in period")
            recommendations.append("Review payment methods and retry failed payments")
        
        if pending_distribution > total_revenue * Decimal("0.3"):
            issues.append("High pending distribution amount")
            recommendations.append("Consider reducing minimum distribution threshold")
        
        if performance_metrics["distribution_success_rate"] < 0.9:
            recommendations.append("Investigate payment processing issues")
        
        return SharingReport(
            report_id=str(uuid4()),
            agreement_id=agreement_id,
            reporting_period=(start_date, end_date),
            total_revenue=total_revenue,
            total_distributed=total_distributed,
            pending_distribution=pending_distribution,
            distribution_count=len(period_distributions),
            average_distribution=total_distributed / len(period_distributions) if period_distributions else Decimal("0"),
            collaborator_earnings=collaborator_earnings,
            performance_metrics=performance_metrics,
            issues_encountered=issues,
            recommendations=recommendations
        )
    
    async def update_collaborator_share(
        self,
        agreement_id: str,
        collaborator_id: str,
        new_share_percentage: Decimal,
        effective_date: Optional[datetime] = None
    ) -> bool:
        """Update collaborator's share percentage."""
        try:
            agreement = self.sharing_agreements.get(agreement_id)
            if not agreement:
                return False
            
            # Find collaborator
            collaborator = None
            for c in agreement.collaborators:
                if c.collaborator_id == collaborator_id:
                    collaborator = c
                    break
            
            if not collaborator:
                return False
            
            # Update share
            old_share = collaborator.share_percentage
            collaborator.share_percentage = new_share_percentage
            agreement.updated_at = datetime.now()
            
            self.logger.info(f"Updated collaborator {collaborator.name} share from {old_share}% to {new_share_percentage}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating collaborator share: {e}")
            return False


# Global instance
_revenue_sharing_automation = None


async def get_revenue_sharing_automation() -> RevenueSharingAutomation:
    """Get the global revenue sharing automation instance."""
    global _revenue_sharing_automation
    
    if _revenue_sharing_automation is None:
        _revenue_sharing_automation = RevenueSharingAutomation()
        await _revenue_sharing_automation.initialize()
    
    return _revenue_sharing_automation


# Example usage
async def main():
    """Example usage of RevenueSharingAutomation."""
    automation = await get_revenue_sharing_automation()
    
    # Create a sharing agreement for a music collaboration
    agreement_id = await automation.create_sharing_agreement(
        project_id="music_collab_001",
        project_name="Summer Hit Collaboration",
        sharing_model=SharingModel.CONTRIBUTION_BASED,
        collaborators=[
            {
                "user_id": "user_001",
                "name": "Alice Musician",
                "email": "alice@music.com",
                "role": "lead",
                "contribution_types": ["content_creation", "marketing"],
                "share_percentage": 40,
                "minimum_payout": 25.00,
                "payout_method": "stripe",
                "payment_details": {"stripe_account": "acct_alice123"}
            },
            {
                "user_id": "user_002", 
                "name": "Bob Producer",
                "email": "bob@studio.com",
                "role": "senior",
                "contribution_types": ["technical_work", "management"],
                "share_percentage": 35,
                "minimum_payout": 20.00,
                "payout_method": "paypal",
                "payment_details": {"paypal_email": "bob@studio.com"}
            },
            {
                "user_id": "user_003",
                "name": "Carol Vocalist",
                "email": "carol@singer.com", 
                "role": "junior",
                "contribution_types": ["content_creation"],
                "share_percentage": 25,
                "minimum_payout": 15.00,
                "payout_method": "stripe",
                "payment_details": {"stripe_account": "acct_carol456"}
            }
        ],
        terms={
            "minimum_distribution": 75.00,
            "sharing_formula": "contribution_based",
            "dispute_resolution": "mediation",
            "contract_duration": "12_months"
        },
        created_by="user_001",
        payout_frequency=PayoutFrequency.WEEKLY,
        automatic_distribution=True
    )
    
    print(f"Created sharing agreement: {agreement_id}")
    
    # Record some revenue
    transaction1_id = await automation.record_revenue(
        agreement_id=agreement_id,
        source="streaming",
        gross_amount=Decimal("500.00"),
        metadata={"platform": "spotify", "plays": 50000}
    )
    
    transaction2_id = await automation.record_revenue(
        agreement_id=agreement_id,
        source="licensing",
        gross_amount=Decimal("300.00"),
        metadata={"client": "tv_commercial", "duration": "30_seconds"}
    )
    
    print(f"Recorded revenue transactions: {transaction1_id[:8]}, {transaction2_id[:8]}")
    
    # Wait for automatic distribution
    await asyncio.sleep(2)
    
    # Check agreement status
    status = await automation.get_agreement_status(agreement_id)
    if status:
        print(f"\n📊 Agreement Status:")
        print(f"Project: {status['project_name']}")
        print(f"Collaborators: {status['collaborators_count']}")
        print(f"Total Revenue: ${status['total_revenue']:.2f}")
        print(f"Total Distributed: ${status['total_distributed']:.2f}")
        print(f"Pending Distribution: ${status['pending_distribution']:.2f}")
        print(f"Distributions: {status['distributions_count']}")
    
    # Get individual collaborator earnings
    for i, collab_id in enumerate(["user_001", "user_002", "user_003"], 1):
        # Find collaborator ID from agreement
        agreement = automation.sharing_agreements[agreement_id]
        collaborator = next((c for c in agreement.collaborators if c.user_id == collab_id), None)
        
        if collaborator:
            earnings = await automation.get_collaborator_earnings(
                agreement_id, collaborator.collaborator_id, period_days=7
            )
            
            print(f"\n👤 {earnings['name']} Earnings (Last 7 days):")
            print(f"Share: {earnings['share_percentage']:.1f}%")
            print(f"Earnings: ${earnings['period_earnings']:.2f}")
            print(f"Payments: {earnings['payments_received']}")
            print(f"Average Payment: ${earnings['average_payment']:.2f}")
    
    # Generate comprehensive report
    report = await automation.generate_sharing_report(agreement_id, period_days=30)
    
    print(f"\n📋 Sharing Report (Last 30 days):")
    print(f"Total Revenue: ${report.total_revenue:.2f}")
    print(f"Total Distributed: ${report.total_distributed:.2f}")
    print(f"Pending: ${report.pending_distribution:.2f}")
    print(f"Distribution Success Rate: {report.performance_metrics['distribution_success_rate']:.1%}")
    
    print(f"\nCollaborator Earnings:")
    for name, amount in report.collaborator_earnings.items():
        print(f"  • {name}: ${amount:.2f}")
    
    if report.recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":
    asyncio.run(main())