"""Accounting and Tax Compliance System
Comprehensive financial reporting and tax compliance automation.

Author: Fahed Mlaiel <mlaiel@live.de>
⚠️ COPYRIGHT WARNING: Proprietary code - unauthorized use prohibited.
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import csv
from pathlib import Path

logger = logging.getLogger(__name__)


class AccountingStandard(Enum):
    """Accounting standard enumeration."""
    GAAP = "gaap"           # US GAAP
    IFRS = "ifrs"           # International Financial Reporting Standards
    HGB = "hgb"             # German Commercial Code
    FRS = "frs"             # UK Financial Reporting Standards
    LOCAL = "local"         # Local country standards


class TransactionType(Enum):
    """Transaction type enumeration."""
    REVENUE = "revenue"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REFUND = "refund"
    TAX = "tax"
    COMMISSION = "commission"


class TaxJurisdiction(Enum):
    """Tax jurisdiction enumeration."""
    FEDERAL = "federal"
    STATE = "state"
    LOCAL = "local"
    VAT = "vat"
    GST = "gst"
    SALES = "sales"


@dataclass
class ChartOfAccounts:
    """Chart of accounts structure."""
    account_code: str
    account_name: str
    account_type: TransactionType
    parent_account: Optional[str] = None
    is_active: bool = True
    description: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class JournalEntry:
    """Journal entry for double-entry bookkeeping."""
    entry_id: str
    entry_date: datetime
    description: str
    reference: Optional[str] = None
    total_debit: Decimal = Decimal('0.00')
    total_credit: Decimal = Decimal('0.00')
    currency: str = "EUR"
    created_by: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class JournalEntryLine:
    """Individual line item in a journal entry."""
    line_id: str
    entry_id: str
    account_code: str
    debit_amount: Decimal = Decimal('0.00')
    credit_amount: Decimal = Decimal('0.00')
    description: Optional[str] = None
    reference: Optional[str] = None


@dataclass
class TaxCalculation:
    """Tax calculation result."""
    tax_id: str
    jurisdiction: TaxJurisdiction
    tax_type: str
    tax_rate: Decimal
    taxable_amount: Decimal
    tax_amount: Decimal
    currency: str
    calculation_date: datetime
    period_start: datetime
    period_end: datetime
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class FinancialReport:
    """Financial report structure."""
    report_id: str
    report_type: str
    report_name: str
    accounting_standard: AccountingStandard
    currency: str
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    data: Dict[str, Any]
    notes: List[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []


class AccountingSystem:
    """Comprehensive accounting and tax compliance system."""

    def __init__(self):
        """Initialize accounting system."""
        try:
            logger.info("Initializing AccountingSystem")
            
            # Storage (in production, use proper accounting database)
            self.chart_of_accounts: Dict[str, ChartOfAccounts] = {}
            self.journal_entries: Dict[str, JournalEntry] = {}
            self.journal_entry_lines: Dict[str, List[JournalEntryLine]] = {}
            self.tax_calculations: Dict[str, TaxCalculation] = {}
            self.financial_reports: Dict[str, FinancialReport] = {}
            
            # Initialize standard chart of accounts
            self._initialize_chart_of_accounts()
            
            # Tax configuration
            self.tax_rates = {
                # VAT rates by country
                "DE_VAT": {"rate": Decimal("19.00"), "type": "VAT"},
                "FR_VAT": {"rate": Decimal("20.00"), "type": "VAT"},
                "GB_VAT": {"rate": Decimal("20.00"), "type": "VAT"},
                "IT_VAT": {"rate": Decimal("22.00"), "type": "VAT"},
                "ES_VAT": {"rate": Decimal("21.00"), "type": "VAT"},
                "NL_VAT": {"rate": Decimal("21.00"), "type": "VAT"},
                
                # US sales tax (simplified)
                "US_CA_SALES": {"rate": Decimal("7.25"), "type": "SALES_TAX"},
                "US_NY_SALES": {"rate": Decimal("8.00"), "type": "SALES_TAX"},
                "US_TX_SALES": {"rate": Decimal("6.25"), "type": "SALES_TAX"},
                
                # Other regions
                "CA_GST": {"rate": Decimal("5.00"), "type": "GST"},
                "AU_GST": {"rate": Decimal("10.00"), "type": "GST"},
                "JP_CONSUMPTION": {"rate": Decimal("10.00"), "type": "CONSUMPTION_TAX"},
            }
            
            # Accounting periods
            self.fiscal_year_start = "01-01"  # January 1st
            self.reporting_currency = "EUR"
            
            # Compliance settings
            self.retention_years = 7  # Document retention period
            self.audit_trail_enabled = True
            
            logger.info("AccountingSystem initialized successfully")
            
        except Exception as e:
            logger.error(f"AccountingSystem initialization failed: {e}")
            raise

    def _initialize_chart_of_accounts(self):
        """Initialize standard chart of accounts."""
        try:
            # Standard accounts following international practices
            standard_accounts = [
                # Assets (1000-1999)
                ChartOfAccounts("1000", "Cash and Cash Equivalents", TransactionType.ASSET),
                ChartOfAccounts("1100", "Accounts Receivable", TransactionType.ASSET),
                ChartOfAccounts("1200", "Prepaid Expenses", TransactionType.ASSET),
                ChartOfAccounts("1300", "Property, Plant & Equipment", TransactionType.ASSET),
                ChartOfAccounts("1400", "Intangible Assets", TransactionType.ASSET),
                ChartOfAccounts("1500", "Software and Technology", TransactionType.ASSET),
                
                # Liabilities (2000-2999)
                ChartOfAccounts("2000", "Accounts Payable", TransactionType.LIABILITY),
                ChartOfAccounts("2100", "Accrued Expenses", TransactionType.LIABILITY),
                ChartOfAccounts("2200", "Deferred Revenue", TransactionType.LIABILITY),
                ChartOfAccounts("2300", "Tax Payable", TransactionType.LIABILITY),
                ChartOfAccounts("2400", "Long-term Debt", TransactionType.LIABILITY),
                
                # Equity (3000-3999)
                ChartOfAccounts("3000", "Shareholders' Equity", TransactionType.EQUITY),
                ChartOfAccounts("3100", "Retained Earnings", TransactionType.EQUITY),
                
                # Revenue (4000-4999)
                ChartOfAccounts("4000", "Subscription Revenue", TransactionType.REVENUE),
                ChartOfAccounts("4100", "License Revenue", TransactionType.REVENUE),
                ChartOfAccounts("4200", "Commission Revenue", TransactionType.REVENUE),
                ChartOfAccounts("4300", "Professional Services Revenue", TransactionType.REVENUE),
                ChartOfAccounts("4400", "Platform Transaction Fees", TransactionType.REVENUE),
                
                # Expenses (5000-5999)
                ChartOfAccounts("5000", "Cost of Goods Sold", TransactionType.EXPENSE),
                ChartOfAccounts("5100", "Payroll and Benefits", TransactionType.EXPENSE),
                ChartOfAccounts("5200", "Marketing and Advertising", TransactionType.EXPENSE),
                ChartOfAccounts("5300", "Technology and Infrastructure", TransactionType.EXPENSE),
                ChartOfAccounts("5400", "Professional Services", TransactionType.EXPENSE),
                ChartOfAccounts("5500", "Office and Administrative", TransactionType.EXPENSE),
                ChartOfAccounts("5600", "Payment Processing Fees", TransactionType.EXPENSE),
                ChartOfAccounts("5700", "Research and Development", TransactionType.EXPENSE),
            ]
            
            for account in standard_accounts:
                self.chart_of_accounts[account.account_code] = account
                
            logger.info(f"Initialized {len(standard_accounts)} standard accounts")
            
        except Exception as e:
            logger.error(f"Error initializing chart of accounts: {e}")

    async def create_journal_entry(
        self,
        description: str,
        entry_lines: List[Tuple[str, Decimal, Decimal, str]],  # (account_code, debit, credit, description)
        entry_date: Optional[datetime] = None,
        reference: Optional[str] = None,
        currency: str = "EUR"
    ) -> JournalEntry:
        """Create a journal entry with proper double-entry bookkeeping."""
        try:
            entry_id = str(uuid.uuid4())
            
            if entry_date is None:
                entry_date = datetime.utcnow()
                
            # Calculate totals
            total_debit = sum(line[1] for line in entry_lines)
            total_credit = sum(line[2] for line in entry_lines)
            
            # Validate double-entry principle
            if total_debit != total_credit:
                raise ValueError(f"Journal entry not balanced: Debit {total_debit} != Credit {total_credit}")
                
            # Create journal entry
            journal_entry = JournalEntry(
                entry_id=entry_id,
                entry_date=entry_date,
                description=description,
                reference=reference,
                total_debit=total_debit,
                total_credit=total_credit,
                currency=currency
            )
            
            # Create journal entry lines
            entry_lines_list = []
            for account_code, debit, credit, line_desc in entry_lines:
                # Validate account exists
                if account_code not in self.chart_of_accounts:
                    raise ValueError(f"Account {account_code} not found in chart of accounts")
                    
                line = JournalEntryLine(
                    line_id=str(uuid.uuid4()),
                    entry_id=entry_id,
                    account_code=account_code,
                    debit_amount=debit,
                    credit_amount=credit,
                    description=line_desc,
                    reference=reference
                )
                entry_lines_list.append(line)
                
            # Store entries
            self.journal_entries[entry_id] = journal_entry
            self.journal_entry_lines[entry_id] = entry_lines_list
            
            logger.info(f"Created journal entry {entry_id}: {description}")
            return journal_entry
            
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            raise

    async def record_subscription_revenue(
        self,
        subscription_id: str,
        amount: Decimal,
        currency: str = "EUR",
        transaction_date: Optional[datetime] = None
    ) -> JournalEntry:
        """Record subscription revenue transaction."""
        try:
            if transaction_date is None:
                transaction_date = datetime.utcnow()
                
            description = f"Subscription revenue - {subscription_id}"
            
            # Journal entry: Debit Cash, Credit Subscription Revenue
            entry_lines = [
                ("1000", amount, Decimal('0.00'), "Cash received"),
                ("4000", Decimal('0.00'), amount, "Subscription revenue earned")
            ]
            
            return await self.create_journal_entry(
                description=description,
                entry_lines=entry_lines,
                entry_date=transaction_date,
                reference=f"SUB-{subscription_id}",
                currency=currency
            )
            
        except Exception as e:
            logger.error(f"Error recording subscription revenue: {e}")
            raise

    async def record_commission_expense(
        self,
        platform: str,
        amount: Decimal,
        currency: str = "EUR",
        transaction_date: Optional[datetime] = None
    ) -> JournalEntry:
        """Record platform commission expense."""
        try:
            if transaction_date is None:
                transaction_date = datetime.utcnow()
                
            description = f"Platform commission - {platform}"
            
            # Journal entry: Debit Commission Expense, Credit Cash
            entry_lines = [
                ("5600", amount, Decimal('0.00'), f"Commission to {platform}"),
                ("1000", Decimal('0.00'), amount, "Cash paid")
            ]
            
            return await self.create_journal_entry(
                description=description,
                entry_lines=entry_lines,
                entry_date=transaction_date,
                reference=f"COMM-{platform}",
                currency=currency
            )
            
        except Exception as e:
            logger.error(f"Error recording commission expense: {e}")
            raise

    async def calculate_tax_liability(
        self,
        period_start: datetime,
        period_end: datetime,
        jurisdiction: str = "DE"
    ) -> TaxCalculation:
        """Calculate tax liability for a period."""
        try:
            tax_id = str(uuid.uuid4())
            
            # Get revenue for the period
            taxable_revenue = await self._get_taxable_revenue(period_start, period_end)
            
            # Get applicable tax rate
            tax_key = f"{jurisdiction}_VAT"
            if tax_key not in self.tax_rates:
                tax_key = "DE_VAT"  # Default to German VAT
                
            tax_config = self.tax_rates[tax_key]
            tax_rate = tax_config["rate"]
            tax_type = tax_config["type"]
            
            # Calculate tax amount
            tax_amount = (taxable_revenue * tax_rate) / Decimal('100')
            
            tax_calculation = TaxCalculation(
                tax_id=tax_id,
                jurisdiction=TaxJurisdiction.VAT,
                tax_type=tax_type,
                tax_rate=tax_rate,
                taxable_amount=taxable_revenue,
                tax_amount=tax_amount,
                currency=self.reporting_currency,
                calculation_date=datetime.utcnow(),
                period_start=period_start,
                period_end=period_end,
                metadata={
                    "jurisdiction_code": jurisdiction,
                    "calculation_method": "revenue_based"
                }
            )
            
            self.tax_calculations[tax_id] = tax_calculation
            
            # Create journal entry for tax liability
            await self.create_journal_entry(
                description=f"Tax liability - {jurisdiction} {tax_type}",
                entry_lines=[
                    ("5000", tax_amount, Decimal('0.00'), "Tax expense"),
                    ("2300", Decimal('0.00'), tax_amount, "Tax payable")
                ],
                reference=f"TAX-{tax_id}",
                currency=self.reporting_currency
            )
            
            logger.info(f"Calculated tax liability: {tax_amount} {self.reporting_currency}")
            return tax_calculation
            
        except Exception as e:
            logger.error(f"Error calculating tax liability: {e}")
            raise

    async def generate_income_statement(
        self,
        period_start: datetime,
        period_end: datetime,
        accounting_standard: AccountingStandard = AccountingStandard.IFRS
    ) -> FinancialReport:
        """Generate income statement (P&L)."""
        try:
            report_id = str(uuid.uuid4())
            
            # Get account balances for the period
            revenue_accounts = await self._get_account_balances(
                ["4000", "4100", "4200", "4300", "4400"],
                period_start,
                period_end
            )
            
            expense_accounts = await self._get_account_balances(
                ["5000", "5100", "5200", "5300", "5400", "5500", "5600", "5700"],
                period_start,
                period_end
            )
            
            # Calculate totals
            total_revenue = sum(revenue_accounts.values())
            total_expenses = sum(expense_accounts.values())
            net_income = total_revenue - total_expenses
            
            # Build income statement data
            income_statement_data = {
                "revenue": {
                    "subscription_revenue": revenue_accounts.get("4000", Decimal('0.00')),
                    "license_revenue": revenue_accounts.get("4100", Decimal('0.00')),
                    "commission_revenue": revenue_accounts.get("4200", Decimal('0.00')),
                    "professional_services": revenue_accounts.get("4300", Decimal('0.00')),
                    "platform_fees": revenue_accounts.get("4400", Decimal('0.00')),
                    "total_revenue": total_revenue
                },
                "expenses": {
                    "cost_of_goods_sold": expense_accounts.get("5000", Decimal('0.00')),
                    "payroll_benefits": expense_accounts.get("5100", Decimal('0.00')),
                    "marketing_advertising": expense_accounts.get("5200", Decimal('0.00')),
                    "technology_infrastructure": expense_accounts.get("5300", Decimal('0.00')),
                    "professional_services": expense_accounts.get("5400", Decimal('0.00')),
                    "office_administrative": expense_accounts.get("5500", Decimal('0.00')),
                    "payment_processing": expense_accounts.get("5600", Decimal('0.00')),
                    "research_development": expense_accounts.get("5700", Decimal('0.00')),
                    "total_expenses": total_expenses
                },
                "net_income": net_income,
                "gross_margin": (total_revenue - expense_accounts.get("5000", Decimal('0.00'))) / total_revenue * 100 if total_revenue > 0 else 0,
                "operating_margin": net_income / total_revenue * 100 if total_revenue > 0 else 0
            }
            
            # Convert Decimal to float for JSON compatibility
            def convert_decimals(obj):
                if isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, Decimal):
                    return float(obj)
                else:
                    return obj
                    
            income_statement_data = convert_decimals(income_statement_data)
            
            report = FinancialReport(
                report_id=report_id,
                report_type="income_statement",
                report_name="Income Statement",
                accounting_standard=accounting_standard,
                currency=self.reporting_currency,
                period_start=period_start,
                period_end=period_end,
                generated_at=datetime.utcnow(),
                data=income_statement_data,
                notes=[
                    f"Report generated according to {accounting_standard.value.upper()} standards",
                    f"All amounts in {self.reporting_currency}",
                    f"Period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}"
                ]
            )
            
            self.financial_reports[report_id] = report
            
            logger.info(f"Generated income statement for period {period_start} to {period_end}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating income statement: {e}")
            raise

    async def generate_balance_sheet(
        self,
        as_of_date: datetime,
        accounting_standard: AccountingStandard = AccountingStandard.IFRS
    ) -> FinancialReport:
        """Generate balance sheet."""
        try:
            report_id = str(uuid.uuid4())
            
            # Get account balances as of the date
            asset_accounts = await self._get_account_balances_as_of(
                ["1000", "1100", "1200", "1300", "1400", "1500"],
                as_of_date
            )
            
            liability_accounts = await self._get_account_balances_as_of(
                ["2000", "2100", "2200", "2300", "2400"],
                as_of_date
            )
            
            equity_accounts = await self._get_account_balances_as_of(
                ["3000", "3100"],
                as_of_date
            )
            
            # Calculate totals
            total_assets = sum(asset_accounts.values())
            total_liabilities = sum(liability_accounts.values())
            total_equity = sum(equity_accounts.values())
            
            # Build balance sheet data
            balance_sheet_data = {
                "assets": {
                    "current_assets": {
                        "cash_equivalents": asset_accounts.get("1000", Decimal('0.00')),
                        "accounts_receivable": asset_accounts.get("1100", Decimal('0.00')),
                        "prepaid_expenses": asset_accounts.get("1200", Decimal('0.00')),
                        "total_current_assets": (
                            asset_accounts.get("1000", Decimal('0.00')) +
                            asset_accounts.get("1100", Decimal('0.00')) +
                            asset_accounts.get("1200", Decimal('0.00'))
                        )
                    },
                    "non_current_assets": {
                        "property_plant_equipment": asset_accounts.get("1300", Decimal('0.00')),
                        "intangible_assets": asset_accounts.get("1400", Decimal('0.00')),
                        "software_technology": asset_accounts.get("1500", Decimal('0.00')),
                        "total_non_current_assets": (
                            asset_accounts.get("1300", Decimal('0.00')) +
                            asset_accounts.get("1400", Decimal('0.00')) +
                            asset_accounts.get("1500", Decimal('0.00'))
                        )
                    },
                    "total_assets": total_assets
                },
                "liabilities": {
                    "current_liabilities": {
                        "accounts_payable": liability_accounts.get("2000", Decimal('0.00')),
                        "accrued_expenses": liability_accounts.get("2100", Decimal('0.00')),
                        "deferred_revenue": liability_accounts.get("2200", Decimal('0.00')),
                        "tax_payable": liability_accounts.get("2300", Decimal('0.00')),
                        "total_current_liabilities": (
                            liability_accounts.get("2000", Decimal('0.00')) +
                            liability_accounts.get("2100", Decimal('0.00')) +
                            liability_accounts.get("2200", Decimal('0.00')) +
                            liability_accounts.get("2300", Decimal('0.00'))
                        )
                    },
                    "non_current_liabilities": {
                        "long_term_debt": liability_accounts.get("2400", Decimal('0.00')),
                        "total_non_current_liabilities": liability_accounts.get("2400", Decimal('0.00'))
                    },
                    "total_liabilities": total_liabilities
                },
                "equity": {
                    "shareholders_equity": equity_accounts.get("3000", Decimal('0.00')),
                    "retained_earnings": equity_accounts.get("3100", Decimal('0.00')),
                    "total_equity": total_equity
                },
                "total_liabilities_equity": total_liabilities + total_equity
            }
            
            # Convert Decimal to float for JSON compatibility
            def convert_decimals(obj):
                if isinstance(obj, dict):
                    return {k: convert_decimals(v) for k, v in obj.items()}
                elif isinstance(obj, Decimal):
                    return float(obj)
                else:
                    return obj
                    
            balance_sheet_data = convert_decimals(balance_sheet_data)
            
            report = FinancialReport(
                report_id=report_id,
                report_type="balance_sheet",
                report_name="Balance Sheet",
                accounting_standard=accounting_standard,
                currency=self.reporting_currency,
                period_start=as_of_date,
                period_end=as_of_date,
                generated_at=datetime.utcnow(),
                data=balance_sheet_data,
                notes=[
                    f"Report generated according to {accounting_standard.value.upper()} standards",
                    f"All amounts in {self.reporting_currency}",
                    f"As of {as_of_date.strftime('%Y-%m-%d')}"
                ]
            )
            
            self.financial_reports[report_id] = report
            
            logger.info(f"Generated balance sheet as of {as_of_date}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating balance sheet: {e}")
            raise

    async def export_tax_report(
        self,
        period_start: datetime,
        period_end: datetime,
        jurisdiction: str = "DE",
        format_type: str = "csv"
    ) -> str:
        """Export tax report for compliance."""
        try:
            # Get tax calculations for the period
            tax_calculations = [
                calc for calc in self.tax_calculations.values()
                if (period_start <= calc.period_start <= period_end or
                    period_start <= calc.period_end <= period_end)
            ]
            
            if format_type == "csv":
                file_path = f"/tmp/tax_report_{jurisdiction}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.csv"
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    
                    # Write header
                    writer.writerow([
                        'Tax ID', 'Jurisdiction', 'Tax Type', 'Tax Rate (%)',
                        'Taxable Amount', 'Tax Amount', 'Currency',
                        'Period Start', 'Period End', 'Calculation Date'
                    ])
                    
                    # Write data
                    for calc in tax_calculations:
                        writer.writerow([
                            calc.tax_id,
                            calc.jurisdiction.value,
                            calc.tax_type,
                            float(calc.tax_rate),
                            float(calc.taxable_amount),
                            float(calc.tax_amount),
                            calc.currency,
                            calc.period_start.strftime('%Y-%m-%d'),
                            calc.period_end.strftime('%Y-%m-%d'),
                            calc.calculation_date.strftime('%Y-%m-%d')
                        ])
                        
            else:  # JSON format
                file_path = f"/tmp/tax_report_{jurisdiction}_{period_start.strftime('%Y%m%d')}_{period_end.strftime('%Y%m%d')}.json"
                
                tax_data = {
                    "report_period": {
                        "start": period_start.isoformat(),
                        "end": period_end.isoformat()
                    },
                    "jurisdiction": jurisdiction,
                    "generated_at": datetime.utcnow().isoformat(),
                    "calculations": [asdict(calc) for calc in tax_calculations]
                }
                
                # Convert datetime objects to ISO format
                def convert_datetime(obj):
                    if isinstance(obj, dict):
                        return {k: convert_datetime(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_datetime(item) for item in obj]
                    elif isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, Decimal):
                        return float(obj)
                    else:
                        return obj
                        
                tax_data = convert_datetime(tax_data)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(tax_data, f, indent=2)
                    
            logger.info(f"Exported tax report to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting tax report: {e}")
            raise

    async def _get_taxable_revenue(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> Decimal:
        """Get taxable revenue for a period."""
        try:
            # This is a simplified calculation
            # In production, this would include proper tax rules
            revenue_accounts = await self._get_account_balances(
                ["4000", "4100", "4200", "4300", "4400"],
                period_start,
                period_end
            )
            
            return sum(revenue_accounts.values())
            
        except Exception as e:
            logger.error(f"Error getting taxable revenue: {e}")
            return Decimal('0.00')

    async def _get_account_balances(
        self,
        account_codes: List[str],
        period_start: datetime,
        period_end: datetime
    ) -> Dict[str, Decimal]:
        """Get account balances for a period."""
        try:
            balances = {}
            
            for account_code in account_codes:
                balance = Decimal('0.00')
                
                # Calculate balance from journal entries
                for entry in self.journal_entries.values():
                    if period_start <= entry.entry_date <= period_end:
                        entry_lines = self.journal_entry_lines.get(entry.entry_id, [])
                        
                        for line in entry_lines:
                            if line.account_code == account_code:
                                # For revenue accounts, credit increases balance
                                if account_code.startswith('4'):
                                    balance += line.credit_amount - line.debit_amount
                                # For expense accounts, debit increases balance
                                elif account_code.startswith('5'):
                                    balance += line.debit_amount - line.credit_amount
                                # For asset accounts, debit increases balance
                                elif account_code.startswith('1'):
                                    balance += line.debit_amount - line.credit_amount
                                # For liability/equity accounts, credit increases balance
                                else:
                                    balance += line.credit_amount - line.debit_amount
                                    
                balances[account_code] = balance
                
            return balances
            
        except Exception as e:
            logger.error(f"Error getting account balances: {e}")
            return {}

    async def _get_account_balances_as_of(
        self,
        account_codes: List[str],
        as_of_date: datetime
    ) -> Dict[str, Decimal]:
        """Get account balances as of a specific date."""
        try:
            balances = {}
            
            for account_code in account_codes:
                balance = Decimal('0.00')
                
                # Calculate balance from all journal entries up to the date
                for entry in self.journal_entries.values():
                    if entry.entry_date <= as_of_date:
                        entry_lines = self.journal_entry_lines.get(entry.entry_id, [])
                        
                        for line in entry_lines:
                            if line.account_code == account_code:
                                # For asset accounts, debit increases balance
                                if account_code.startswith('1'):
                                    balance += line.debit_amount - line.credit_amount
                                # For liability/equity accounts, credit increases balance
                                elif account_code.startswith('2') or account_code.startswith('3'):
                                    balance += line.credit_amount - line.debit_amount
                                    
                balances[account_code] = balance
                
            return balances
            
        except Exception as e:
            logger.error(f"Error getting account balances as of date: {e}")
            return {}

    async def get_audit_trail(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get audit trail for transactions."""
        try:
            audit_trail = []
            
            for entry in self.journal_entries.values():
                # Filter by date range
                if start_date and entry.entry_date < start_date:
                    continue
                if end_date and entry.entry_date > end_date:
                    continue
                    
                entry_lines = self.journal_entry_lines.get(entry.entry_id, [])
                
                for line in entry_lines:
                    # Filter by account
                    if account_code and line.account_code != account_code:
                        continue
                        
                    audit_trail.append({
                        "entry_id": entry.entry_id,
                        "entry_date": entry.entry_date.isoformat(),
                        "account_code": line.account_code,
                        "account_name": self.chart_of_accounts.get(
                            line.account_code, ChartOfAccounts("", "Unknown", TransactionType.ASSET)
                        ).account_name,
                        "debit_amount": float(line.debit_amount),
                        "credit_amount": float(line.credit_amount),
                        "description": entry.description,
                        "reference": entry.reference,
                        "created_at": entry.created_at.isoformat()
                    })
                    
            # Sort by date
            audit_trail.sort(key=lambda x: x["entry_date"])
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Error getting audit trail: {e}")
            return []