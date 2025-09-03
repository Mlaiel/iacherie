"""Accounting Export and Tax Compliance System
Enterprise-grade accounting export and tax compliance module for automated financial reporting and regulatory compliance.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: All rights reserved. Unauthorized use, reproduction, or distribution prohibited.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP
import json
import uuid
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    EXCEL = "excel"
    PDF = "pdf"
    DATEV = "datev"  # German accounting standard
    SEPA = "sepa"    # EU payment standard
    GAAP = "gaap"    # US accounting standard
    IFRS = "ifrs"    # International accounting standard


class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    GERMANY = "DE"
    FRANCE = "FR"
    UNITED_STATES = "US"
    UNITED_KINGDOM = "GB"
    EUROPEAN_UNION = "EU"
    CANADA = "CA"
    AUSTRALIA = "AU"
    JAPAN = "JP"
    SWITZERLAND = "CH"
    NETHERLANDS = "NL"


class TransactionType(Enum):
    """Transaction types for accounting"""
    REVENUE = "revenue"
    EXPENSE = "expense"
    ROYALTY_PAYMENT = "royalty_payment"
    PLATFORM_FEE = "platform_fee"
    PROCESSING_FEE = "processing_fee"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    TAX_PAYMENT = "tax_payment"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit"


class TaxCategory(Enum):
    """Tax categories"""
    DIGITAL_SERVICES = "digital_services"
    ROYALTIES = "royalties"
    ADVERTISING = "advertising"
    SUBSCRIPTION = "subscription"
    TRANSACTION_FEE = "transaction_fee"
    PLATFORM_FEE = "platform_fee"
    LICENSING = "licensing"
    CONSULTATION = "consultation"


@dataclass
class AccountingTransaction:
    """Accounting transaction record"""
    transaction_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    external_id: Optional[str] = None
    transaction_type: TransactionType = TransactionType.REVENUE
    amount: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    tax_amount: Decimal = Decimal('0.00')
    currency: str = "EUR"
    exchange_rate: Decimal = Decimal('1.00')
    base_currency_amount: Decimal = Decimal('0.00')
    
    # Accounting details
    debit_account: str = ""
    credit_account: str = ""
    description: str = ""
    reference_number: str = ""
    
    # Tax details
    tax_jurisdiction: TaxJurisdiction = TaxJurisdiction.GERMANY
    tax_category: TaxCategory = TaxCategory.DIGITAL_SERVICES
    tax_rate: Decimal = Decimal('0.19')  # 19% VAT
    tax_exempt: bool = False
    
    # Timestamps
    transaction_date: datetime = field(default_factory=datetime.utcnow)
    booking_date: datetime = field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = None
    
    # Metadata
    user_id: Optional[int] = None
    content_id: Optional[int] = None
    platform: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Compliance
    compliance_status: str = "pending"  # pending, validated, exported, filed
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TaxReport:
    """Tax report structure"""
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    jurisdiction: TaxJurisdiction = TaxJurisdiction.GERMANY
    period_start: datetime = field(default_factory=datetime.utcnow)
    period_end: datetime = field(default_factory=datetime.utcnow)
    total_revenue: Decimal = Decimal('0.00')
    total_expenses: Decimal = Decimal('0.00')
    taxable_income: Decimal = Decimal('0.00')
    tax_owed: Decimal = Decimal('0.00')
    tax_paid: Decimal = Decimal('0.00')
    tax_balance: Decimal = Decimal('0.00')
    transactions: List[AccountingTransaction] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "draft"  # draft, final, submitted


class AccountingExportCompliance:
    """Enterprise accounting export and tax compliance system"""

    def __init__(self):
        self.transactions: Dict[str, AccountingTransaction] = {}
        self.tax_reports: Dict[str, TaxReport] = {}
        
        # Tax rates by jurisdiction and category
        self.tax_rates = {
            TaxJurisdiction.GERMANY: {
                TaxCategory.DIGITAL_SERVICES: Decimal('0.19'),
                TaxCategory.ROYALTIES: Decimal('0.19'),
                TaxCategory.ADVERTISING: Decimal('0.19'),
                TaxCategory.SUBSCRIPTION: Decimal('0.19'),
                TaxCategory.LICENSING: Decimal('0.19')
            },
            TaxJurisdiction.FRANCE: {
                TaxCategory.DIGITAL_SERVICES: Decimal('0.20'),
                TaxCategory.ROYALTIES: Decimal('0.20'),
                TaxCategory.ADVERTISING: Decimal('0.20'),
                TaxCategory.SUBSCRIPTION: Decimal('0.20'),
                TaxCategory.LICENSING: Decimal('0.20')
            },
            TaxJurisdiction.UNITED_STATES: {
                TaxCategory.DIGITAL_SERVICES: Decimal('0.0875'),  # NY state average
                TaxCategory.ROYALTIES: Decimal('0.30'),  # Federal withholding
                TaxCategory.ADVERTISING: Decimal('0.0875'),
                TaxCategory.SUBSCRIPTION: Decimal('0.0875'),
                TaxCategory.LICENSING: Decimal('0.30')
            }
        }
        
        # Chart of accounts
        self.chart_of_accounts = {
            "revenue": {
                "4000": "Digital Services Revenue",
                "4100": "Royalty Revenue", 
                "4200": "Advertising Revenue",
                "4300": "Subscription Revenue",
                "4400": "Licensing Revenue"
            },
            "expenses": {
                "5000": "Platform Fees",
                "5100": "Processing Fees",
                "5200": "Marketing Expenses",
                "5300": "Technology Expenses",
                "5400": "Professional Services"
            },
            "assets": {
                "1000": "Cash and Cash Equivalents",
                "1100": "Accounts Receivable",
                "1200": "Prepaid Expenses",
                "1300": "Fixed Assets"
            },
            "liabilities": {
                "2000": "Accounts Payable",
                "2100": "Accrued Expenses",
                "2200": "Tax Liabilities",
                "2300": "Deferred Revenue"
            }
        }

    async def record_transaction(
        self,
        transaction_data: Dict[str, Any],
        auto_calculate_tax: bool = True
    ) -> AccountingTransaction:
        """Record accounting transaction with automatic tax calculation"""
        try:
            # Create transaction
            transaction = AccountingTransaction(
                external_id=transaction_data.get('external_id'),
                transaction_type=TransactionType(transaction_data.get('type', 'revenue')),
                amount=Decimal(str(transaction_data.get('amount', 0))),
                currency=transaction_data.get('currency', 'EUR'),
                description=transaction_data.get('description', ''),
                reference_number=transaction_data.get('reference', ''),
                user_id=transaction_data.get('user_id'),
                content_id=transaction_data.get('content_id'),
                platform=transaction_data.get('platform'),
                tax_jurisdiction=TaxJurisdiction(transaction_data.get('jurisdiction', 'DE')),
                tax_category=TaxCategory(transaction_data.get('tax_category', 'digital_services')),
                transaction_date=datetime.fromisoformat(transaction_data['date']) if transaction_data.get('date') else datetime.utcnow(),
                metadata=transaction_data.get('metadata', {})
            )
            
            # Auto-calculate tax if enabled
            if auto_calculate_tax:
                await self._calculate_transaction_tax(transaction)
            
            # Set accounting codes
            await self._set_accounting_codes(transaction)
            
            # Add to audit trail
            transaction.audit_trail.append({
                "action": "transaction_recorded",
                "timestamp": datetime.utcnow().isoformat(),
                "user": "system",
                "details": "Transaction recorded and tax calculated"
            })
            
            # Store transaction
            self.transactions[transaction.transaction_id] = transaction
            
            logger.info(f"Recorded transaction {transaction.transaction_id}: {transaction.amount} {transaction.currency}")
            return transaction
            
        except Exception as e:
            logger.error(f"Failed to record transaction: {str(e)}")
            raise

    async def _calculate_transaction_tax(self, transaction: AccountingTransaction):
        """Calculate tax for transaction"""
        try:
            # Get applicable tax rate
            jurisdiction_rates = self.tax_rates.get(transaction.tax_jurisdiction, {})
            tax_rate = jurisdiction_rates.get(transaction.tax_category, Decimal('0.19'))
            
            transaction.tax_rate = tax_rate
            
            if not transaction.tax_exempt:
                # Calculate tax amount
                if transaction.transaction_type in [TransactionType.REVENUE, TransactionType.ROYALTY_PAYMENT]:
                    # Revenue transactions - tax inclusive
                    transaction.tax_amount = (transaction.amount * tax_rate / (Decimal('1') + tax_rate)).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
                    transaction.net_amount = transaction.amount - transaction.tax_amount
                else:
                    # Expense transactions - tax exclusive
                    transaction.net_amount = transaction.amount
                    transaction.tax_amount = (transaction.amount * tax_rate).quantize(
                        Decimal('0.01'), rounding=ROUND_HALF_UP
                    )
            else:
                transaction.net_amount = transaction.amount
                transaction.tax_amount = Decimal('0.00')
            
            # Convert to base currency if needed
            if transaction.currency != "EUR":
                # In real implementation, fetch exchange rate from API
                transaction.exchange_rate = Decimal('1.10')  # Placeholder rate
                transaction.base_currency_amount = (transaction.amount * transaction.exchange_rate).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                transaction.base_currency_amount = transaction.amount
                
        except Exception as e:
            logger.error(f"Failed to calculate transaction tax: {str(e)}")
            raise

    async def _set_accounting_codes(self, transaction: AccountingTransaction):
        """Set debit and credit account codes"""
        try:
            if transaction.transaction_type == TransactionType.REVENUE:
                transaction.debit_account = "1000"  # Cash
                if transaction.tax_category == TaxCategory.DIGITAL_SERVICES:
                    transaction.credit_account = "4000"
                elif transaction.tax_category == TaxCategory.ROYALTIES:
                    transaction.credit_account = "4100"
                elif transaction.tax_category == TaxCategory.ADVERTISING:
                    transaction.credit_account = "4200"
                else:
                    transaction.credit_account = "4000"
                    
            elif transaction.transaction_type == TransactionType.EXPENSE:
                transaction.debit_account = "5000"  # Platform Fees
                transaction.credit_account = "1000"  # Cash
                
            elif transaction.transaction_type == TransactionType.PLATFORM_FEE:
                transaction.debit_account = "5000"  # Platform Fees
                transaction.credit_account = "1000"  # Cash
                
            elif transaction.transaction_type == TransactionType.ROYALTY_PAYMENT:
                transaction.debit_account = "5100"  # Royalty Expenses
                transaction.credit_account = "1000"  # Cash
                
        except Exception as e:
            logger.error(f"Failed to set accounting codes: {str(e)}")

    async def generate_tax_report(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: datetime,
        period_end: datetime
    ) -> TaxReport:
        """Generate comprehensive tax report for jurisdiction and period"""
        try:
            # Filter transactions for period and jurisdiction
            applicable_transactions = []
            for transaction in self.transactions.values():
                if (transaction.tax_jurisdiction == jurisdiction and 
                    period_start <= transaction.transaction_date <= period_end):
                    applicable_transactions.append(transaction)
            
            # Calculate totals
            total_revenue = sum(
                t.net_amount for t in applicable_transactions 
                if t.transaction_type in [TransactionType.REVENUE, TransactionType.ROYALTY_PAYMENT]
            )
            
            total_expenses = sum(
                t.net_amount for t in applicable_transactions
                if t.transaction_type in [TransactionType.EXPENSE, TransactionType.PLATFORM_FEE, TransactionType.PROCESSING_FEE]
            )
            
            taxable_income = total_revenue - total_expenses
            
            # Calculate tax owed
            tax_owed = sum(t.tax_amount for t in applicable_transactions)
            
            # Calculate tax paid (from tax payment transactions)
            tax_paid = sum(
                t.amount for t in applicable_transactions
                if t.transaction_type == TransactionType.TAX_PAYMENT
            )
            
            tax_balance = tax_owed - tax_paid
            
            # Create tax report
            report = TaxReport(
                jurisdiction=jurisdiction,
                period_start=period_start,
                period_end=period_end,
                total_revenue=total_revenue,
                total_expenses=total_expenses,
                taxable_income=taxable_income,
                tax_owed=tax_owed,
                tax_paid=tax_paid,
                tax_balance=tax_balance,
                transactions=applicable_transactions
            )
            
            self.tax_reports[report.report_id] = report
            
            logger.info(f"Generated tax report {report.report_id} for {jurisdiction.value}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate tax report: {str(e)}")
            raise

    async def export_accounting_data(
        self,
        export_format: ExportFormat,
        start_date: datetime,
        end_date: datetime,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Export accounting data in specified format"""
        try:
            # Filter transactions for period
            filtered_transactions = [
                t for t in self.transactions.values()
                if start_date <= t.transaction_date <= end_date
            ]
            
            if export_format == ExportFormat.CSV:
                return await self._export_csv(filtered_transactions, output_path)
            elif export_format == ExportFormat.JSON:
                return await self._export_json(filtered_transactions, output_path)
            elif export_format == ExportFormat.XML:
                return await self._export_xml(filtered_transactions, output_path)
            elif export_format == ExportFormat.DATEV:
                return await self._export_datev(filtered_transactions, output_path)
            elif export_format == ExportFormat.SEPA:
                return await self._export_sepa(filtered_transactions, output_path)
            else:
                raise ValueError(f"Unsupported export format: {export_format.value}")
                
        except Exception as e:
            logger.error(f"Failed to export accounting data: {str(e)}")
            raise

    async def _export_csv(self, transactions: List[AccountingTransaction], output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export transactions to CSV format"""
        try:
            output_path = output_path or f"/tmp/accounting_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # Define CSV headers
            headers = [
                "Transaction ID", "External ID", "Date", "Type", "Amount", "Net Amount", 
                "Tax Amount", "Currency", "Tax Rate", "Tax Jurisdiction", "Tax Category",
                "Debit Account", "Credit Account", "Description", "Reference", 
                "User ID", "Content ID", "Platform"
            ]
            
            # Create CSV content
            csv_data = []
            for transaction in transactions:
                row = [
                    transaction.transaction_id,
                    transaction.external_id or "",
                    transaction.transaction_date.isoformat(),
                    transaction.transaction_type.value,
                    str(transaction.amount),
                    str(transaction.net_amount),
                    str(transaction.tax_amount),
                    transaction.currency,
                    str(transaction.tax_rate),
                    transaction.tax_jurisdiction.value,
                    transaction.tax_category.value,
                    transaction.debit_account,
                    transaction.credit_account,
                    transaction.description,
                    transaction.reference_number,
                    str(transaction.user_id) if transaction.user_id else "",
                    str(transaction.content_id) if transaction.content_id else "",
                    transaction.platform or ""
                ]
                csv_data.append(row)
            
            # Write CSV file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(csv_data)
            
            return {
                "format": "csv",
                "file_path": output_path,
                "transaction_count": len(transactions),
                "total_amount": sum(t.amount for t in transactions),
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {str(e)}")
            raise

    async def _export_json(self, transactions: List[AccountingTransaction], output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export transactions to JSON format"""
        try:
            output_path = output_path or f"/tmp/accounting_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Convert transactions to JSON-serializable format
            json_data = {
                "export_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "transaction_count": len(transactions),
                    "total_amount": float(sum(t.amount for t in transactions)),
                    "format": "json"
                },
                "transactions": []
            }
            
            for transaction in transactions:
                transaction_data = {
                    "transaction_id": transaction.transaction_id,
                    "external_id": transaction.external_id,
                    "type": transaction.transaction_type.value,
                    "amount": float(transaction.amount),
                    "net_amount": float(transaction.net_amount),
                    "tax_amount": float(transaction.tax_amount),
                    "currency": transaction.currency,
                    "tax_rate": float(transaction.tax_rate),
                    "tax_jurisdiction": transaction.tax_jurisdiction.value,
                    "tax_category": transaction.tax_category.value,
                    "debit_account": transaction.debit_account,
                    "credit_account": transaction.credit_account,
                    "description": transaction.description,
                    "reference_number": transaction.reference_number,
                    "transaction_date": transaction.transaction_date.isoformat(),
                    "booking_date": transaction.booking_date.isoformat(),
                    "user_id": transaction.user_id,
                    "content_id": transaction.content_id,
                    "platform": transaction.platform,
                    "compliance_status": transaction.compliance_status,
                    "metadata": transaction.metadata
                }
                json_data["transactions"].append(transaction_data)
            
            # Write JSON file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
            
            return {
                "format": "json",
                "file_path": output_path,
                "transaction_count": len(transactions),
                "total_amount": float(sum(t.amount for t in transactions)),
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export JSON: {str(e)}")
            raise

    async def _export_datev(self, transactions: List[AccountingTransaction], output_path: Optional[str] = None) -> Dict[str, Any]:
        """Export transactions to DATEV format (German accounting standard)"""
        try:
            output_path = output_path or f"/tmp/datev_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            
            # DATEV CSV format headers
            datev_headers = [
                "Umsatz (ohne Soll/Haben-Kz)",  # Amount
                "Soll/Haben-Kennzeichen",       # Debit/Credit indicator
                "WKZ Umsatz",                   # Currency
                "Kurs",                         # Exchange rate
                "Basis-Umsatz",                 # Base amount
                "WKZ Basis-Umsatz",             # Base currency
                "Konto",                        # Account
                "Gegenkonto (ohne BU-Schlüssel)", # Counter account
                "BU-Schlüssel",                 # Tax key
                "Belegdatum",                   # Document date
                "Belegfeld 1",                  # Reference 1
                "Belegfeld 2",                  # Reference 2
                "Skonto",                       # Discount
                "Buchungstext"                  # Booking text
            ]
            
            # Convert transactions to DATEV format
            datev_data = []
            for transaction in transactions:
                # Determine debit/credit indicator
                soll_haben = "S" if transaction.transaction_type in [TransactionType.REVENUE] else "H"
                
                # Tax key based on tax rate
                tax_key = ""
                if transaction.tax_rate == Decimal('0.19'):
                    tax_key = "9"  # 19% VAT
                elif transaction.tax_rate == Decimal('0.07'):
                    tax_key = "5"  # 7% VAT
                
                row = [
                    str(transaction.net_amount),
                    soll_haben,
                    transaction.currency,
                    str(transaction.exchange_rate),
                    str(transaction.base_currency_amount),
                    "EUR",
                    transaction.debit_account,
                    transaction.credit_account,
                    tax_key,
                    transaction.transaction_date.strftime("%d%m%Y"),
                    transaction.reference_number,
                    transaction.external_id or "",
                    "",  # No discount
                    transaction.description
                ]
                datev_data.append(row)
            
            # Write DATEV file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', newline='', encoding='latin-1') as csvfile:
                writer = csv.writer(csvfile, delimiter=';')
                writer.writerow(datev_headers)
                writer.writerows(datev_data)
            
            return {
                "format": "datev",
                "file_path": output_path,
                "transaction_count": len(transactions),
                "total_amount": float(sum(t.amount for t in transactions)),
                "export_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to export DATEV: {str(e)}")
            raise

    async def get_compliance_status(self) -> Dict[str, Any]:
        """Get overall compliance status"""
        try:
            total_transactions = len(self.transactions)
            validated_transactions = len([
                t for t in self.transactions.values() 
                if t.compliance_status == "validated"
            ])
            
            # Check for missing tax calculations
            missing_tax = [
                t for t in self.transactions.values()
                if not t.tax_exempt and t.tax_amount == Decimal('0.00')
            ]
            
            # Check for missing account codes
            missing_accounts = [
                t for t in self.transactions.values()
                if not t.debit_account or not t.credit_account
            ]
            
            # Calculate compliance score
            compliance_score = 0.0
            if total_transactions > 0:
                compliance_score = (validated_transactions / total_transactions) * 100
            
            status = {
                "overview": {
                    "total_transactions": total_transactions,
                    "validated_transactions": validated_transactions,
                    "compliance_score": compliance_score,
                    "status": "compliant" if compliance_score >= 95 else "non_compliant"
                },
                "issues": {
                    "missing_tax_calculations": len(missing_tax),
                    "missing_account_codes": len(missing_accounts)
                },
                "tax_reports": {
                    "total_reports": len(self.tax_reports),
                    "draft_reports": len([r for r in self.tax_reports.values() if r.status == "draft"]),
                    "final_reports": len([r for r in self.tax_reports.values() if r.status == "final"])
                },
                "last_updated": datetime.utcnow().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get compliance status: {str(e)}")
            raise

    async def validate_transaction_compliance(self, transaction_id: str) -> Dict[str, Any]:
        """Validate compliance for specific transaction"""
        try:
            transaction = self.transactions.get(transaction_id)
            if not transaction:
                raise ValueError(f"Transaction {transaction_id} not found")
            
            validation_results = {
                "transaction_id": transaction_id,
                "is_compliant": True,
                "issues": [],
                "warnings": []
            }
            
            # Check required fields
            if not transaction.debit_account:
                validation_results["issues"].append("Missing debit account")
                validation_results["is_compliant"] = False
            
            if not transaction.credit_account:
                validation_results["issues"].append("Missing credit account")
                validation_results["is_compliant"] = False
            
            if not transaction.description:
                validation_results["warnings"].append("Missing transaction description")
            
            # Check tax calculation
            if not transaction.tax_exempt and transaction.tax_amount == Decimal('0.00'):
                validation_results["issues"].append("Missing tax calculation")
                validation_results["is_compliant"] = False
            
            # Check currency and amounts
            if transaction.amount <= 0:
                validation_results["issues"].append("Invalid transaction amount")
                validation_results["is_compliant"] = False
            
            # Update compliance status
            if validation_results["is_compliant"]:
                transaction.compliance_status = "validated"
                transaction.audit_trail.append({
                    "action": "compliance_validated",
                    "timestamp": datetime.utcnow().isoformat(),
                    "user": "system",
                    "details": "Transaction passed compliance validation"
                })
            else:
                transaction.compliance_status = "non_compliant"
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Failed to validate transaction compliance: {str(e)}")
            raise


# Global accounting export instance
_accounting_export = None

def get_accounting_export() -> AccountingExportCompliance:
    """Get global accounting export instance"""
    global _accounting_export
    if _accounting_export is None:
        _accounting_export = AccountingExportCompliance()
    return _accounting_export


async def record_revenue_transaction(
    amount: Decimal,
    currency: str = "EUR",
    description: str = "",
    user_id: Optional[int] = None,
    content_id: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> AccountingTransaction:
    """Record revenue transaction for accounting"""
    accounting = get_accounting_export()
    
    transaction_data = {
        "type": "revenue",
        "amount": float(amount),
        "currency": currency,
        "description": description,
        "user_id": user_id,
        "content_id": content_id,
        "metadata": metadata or {}
    }
    
    return await accounting.record_transaction(transaction_data)


async def export_tax_report(
    jurisdiction: TaxJurisdiction,
    start_date: datetime,
    end_date: datetime,
    export_format: ExportFormat = ExportFormat.JSON
) -> Dict[str, Any]:
    """Generate and export tax report"""
    accounting = get_accounting_export()
    
    # Generate tax report
    report = await accounting.generate_tax_report(jurisdiction, start_date, end_date)
    
    # Export accounting data for the period
    export_result = await accounting.export_accounting_data(
        export_format, start_date, end_date
    )
    
    return {
        "tax_report": {
            "report_id": report.report_id,
            "jurisdiction": report.jurisdiction.value,
            "total_revenue": float(report.total_revenue),
            "total_expenses": float(report.total_expenses),
            "tax_owed": float(report.tax_owed),
            "tax_balance": float(report.tax_balance)
        },
        "export_details": export_result
    }