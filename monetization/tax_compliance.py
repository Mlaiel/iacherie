"""Tax Compliance and Accounting Export System
Comprehensive tax calculation, compliance reporting, and accounting integration
for multi-jurisdiction financial operations.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import asyncio
import csv
import json
import logging
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import io

logger = logging.getLogger(__name__)


class TaxJurisdiction(Enum):
    """Tax jurisdictions"""
    GERMANY = "DE"
    FRANCE = "FR"
    UNITED_KINGDOM = "GB"
    UNITED_STATES = "US"
    CANADA = "CA"
    AUSTRALIA = "AU"
    NETHERLANDS = "NL"
    SWEDEN = "SE"
    NORWAY = "NO"
    SWITZERLAND = "CH"
    AUSTRIA = "AT"
    BELGIUM = "BE"
    SPAIN = "ES"
    ITALY = "IT"


class TaxType(Enum):
    """Tax types"""
    VAT = "vat"
    GST = "gst"
    SALES_TAX = "sales_tax"
    INCOME_TAX = "income_tax"
    CORPORATE_TAX = "corporate_tax"
    WITHHOLDING_TAX = "withholding_tax"


class ReportFormat(Enum):
    """Export formats"""
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    XLSX = "xlsx"
    PDF = "pdf"
    QUICKBOOKS = "quickbooks"
    XERO = "xero"
    SAP = "sap"


@dataclass
class TaxRule:
    """Tax calculation rule"""
    id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    rate: Decimal
    threshold: Optional[Decimal] = None
    description: str = ""
    effective_date: datetime = None
    expiry_date: Optional[datetime] = None
    conditions: Optional[Dict] = None


@dataclass
class TaxCalculation:
    """Tax calculation result"""
    transaction_id: str
    jurisdiction: TaxJurisdiction
    tax_type: TaxType
    taxable_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    currency: str
    calculation_date: datetime
    rules_applied: List[str]
    metadata: Optional[Dict] = None


@dataclass
class TaxReport:
    """Tax report data"""
    id: str
    jurisdiction: TaxJurisdiction
    period_start: date
    period_end: date
    total_sales: Decimal
    total_tax_collected: Decimal
    total_tax_paid: Decimal
    currency: str
    transactions_count: int
    generated_at: datetime
    status: str = "draft"


@dataclass
class AccountingEntry:
    """Accounting entry for export"""
    id: str
    date: datetime
    account_code: str
    account_name: str
    debit_amount: Decimal
    credit_amount: Decimal
    description: str
    reference: str
    currency: str
    tax_code: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Dict] = None


class TaxComplianceEngine:
    """Comprehensive tax compliance and accounting system"""
    
    # VAT rates by country (simplified)
    VAT_RATES = {
        TaxJurisdiction.GERMANY: {
            "standard": Decimal("19.0"),
            "reduced": Decimal("7.0"),
            "threshold": Decimal("22000")
        },
        TaxJurisdiction.FRANCE: {
            "standard": Decimal("20.0"),
            "reduced": Decimal("5.5"),
            "threshold": Decimal("34400")
        },
        TaxJurisdiction.UNITED_KINGDOM: {
            "standard": Decimal("20.0"),
            "reduced": Decimal("5.0"),
            "threshold": Decimal("85000")
        },
        TaxJurisdiction.NETHERLANDS: {
            "standard": Decimal("21.0"),
            "reduced": Decimal("9.0"),
            "threshold": Decimal("20000")
        },
        TaxJurisdiction.SWEDEN: {
            "standard": Decimal("25.0"),
            "reduced": Decimal("12.0"),
            "threshold": Decimal("30000")
        }
    }
    
    # Chart of accounts for different accounting systems
    CHART_OF_ACCOUNTS = {
        "revenue": {
            "code": "4000",
            "name": "Sales Revenue",
            "type": "credit"
        },
        "vat_output": {
            "code": "2200",
            "name": "VAT Output Tax",
            "type": "credit"
        },
        "accounts_receivable": {
            "code": "1200",
            "name": "Accounts Receivable",
            "type": "debit"
        },
        "bank": {
            "code": "1000",
            "name": "Bank Account",
            "type": "debit"
        },
        "payment_fees": {
            "code": "6100",
            "name": "Payment Processing Fees",
            "type": "debit"
        }
    }
    
    def __init__(self):
        self.tax_rules = {}
        self.tax_calculations = {}
        self.tax_reports = {}
        self.accounting_entries = {}
        self._initialize_default_tax_rules()
        
    def _initialize_default_tax_rules(self):
        """Initialize default tax rules for major jurisdictions"""
        for jurisdiction, rates in self.VAT_RATES.items():
            rule_id = str(uuid.uuid4())
            
            tax_rule = TaxRule(
                id=rule_id,
                jurisdiction=jurisdiction,
                tax_type=TaxType.VAT,
                rate=rates["standard"],
                threshold=rates.get("threshold"),
                description=f"Standard VAT rate for {jurisdiction.value}",
                effective_date=datetime(2024, 1, 1)
            )
            
            self.tax_rules[rule_id] = tax_rule
            
    async def calculate_tax(
        self,
        transaction_id: str,
        amount: Decimal,
        currency: str,
        customer_jurisdiction: TaxJurisdiction,
        supplier_jurisdiction: TaxJurisdiction,
        transaction_type: str = "b2c",
        product_category: str = "digital_services"
    ) -> TaxCalculation:
        """Calculate tax for transaction"""
        try:
            # Determine applicable jurisdiction
            applicable_jurisdiction = self._determine_tax_jurisdiction(
                customer_jurisdiction,
                supplier_jurisdiction,
                transaction_type,
                product_category
            )
            
            # Get applicable tax rules
            applicable_rules = self._get_applicable_tax_rules(
                applicable_jurisdiction,
                amount,
                transaction_type,
                product_category
            )
            
            if not applicable_rules:
                # No tax applicable
                return TaxCalculation(
                    transaction_id=transaction_id,
                    jurisdiction=applicable_jurisdiction,
                    tax_type=TaxType.VAT,
                    taxable_amount=amount,
                    tax_rate=Decimal('0'),
                    tax_amount=Decimal('0'),
                    currency=currency,
                    calculation_date=datetime.now(),
                    rules_applied=[]
                )
                
            # Apply tax rules
            total_tax = Decimal('0')
            rules_applied = []
            
            for rule in applicable_rules:
                if self._should_apply_rule(rule, amount, transaction_type):
                    tax_amount = self._calculate_rule_tax(rule, amount)
                    total_tax += tax_amount
                    rules_applied.append(rule.id)
                    
            calculation = TaxCalculation(
                transaction_id=transaction_id,
                jurisdiction=applicable_jurisdiction,
                tax_type=applicable_rules[0].tax_type,
                taxable_amount=amount,
                tax_rate=applicable_rules[0].rate,
                tax_amount=total_tax,
                currency=currency,
                calculation_date=datetime.now(),
                rules_applied=rules_applied,
                metadata={
                    "customer_jurisdiction": customer_jurisdiction.value,
                    "supplier_jurisdiction": supplier_jurisdiction.value,
                    "transaction_type": transaction_type,
                    "product_category": product_category
                }
            )
            
            self.tax_calculations[transaction_id] = calculation
            
            logger.info(f"Tax calculated for transaction {transaction_id}: {total_tax} {currency}")
            return calculation
            
        except Exception as e:
            logger.error(f"Error calculating tax: {str(e)}")
            raise
            
    async def generate_tax_report(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: date,
        period_end: date,
        currency: str = "EUR"
    ) -> TaxReport:
        """Generate tax report for period"""
        try:
            report_id = str(uuid.uuid4())
            
            # Filter calculations for period and jurisdiction
            period_calculations = [
                calc for calc in self.tax_calculations.values()
                if (calc.jurisdiction == jurisdiction and
                    period_start <= calc.calculation_date.date() <= period_end and
                    calc.currency == currency)
            ]
            
            # Calculate totals
            total_sales = sum(calc.taxable_amount for calc in period_calculations)
            total_tax_collected = sum(calc.tax_amount for calc in period_calculations)
            
            # Calculate tax paid (simplified - would include input tax in real system)
            total_tax_paid = total_tax_collected * Decimal('0.1')  # Assume 10% input tax
            
            report = TaxReport(
                id=report_id,
                jurisdiction=jurisdiction,
                period_start=period_start,
                period_end=period_end,
                total_sales=total_sales,
                total_tax_collected=total_tax_collected,
                total_tax_paid=total_tax_paid,
                currency=currency,
                transactions_count=len(period_calculations),
                generated_at=datetime.now()
            )
            
            self.tax_reports[report_id] = report
            
            logger.info(f"Tax report generated: {report_id} for {jurisdiction.value}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating tax report: {str(e)}")
            raise
            
    async def create_accounting_entries(
        self,
        transaction_id: str,
        amount: Decimal,
        tax_amount: Decimal,
        currency: str,
        customer_id: str,
        description: str,
        payment_received: bool = False
    ) -> List[AccountingEntry]:
        """Create double-entry accounting entries"""
        try:
            entries = []
            entry_date = datetime.now()
            
            # Revenue entry (credit)
            revenue_entry = AccountingEntry(
                id=str(uuid.uuid4()),
                date=entry_date,
                account_code=self.CHART_OF_ACCOUNTS["revenue"]["code"],
                account_name=self.CHART_OF_ACCOUNTS["revenue"]["name"],
                debit_amount=Decimal('0'),
                credit_amount=amount,
                description=f"Revenue: {description}",
                reference=transaction_id,
                currency=currency,
                customer_id=customer_id
            )
            entries.append(revenue_entry)
            
            # VAT entry (credit) if applicable
            if tax_amount > 0:
                vat_entry = AccountingEntry(
                    id=str(uuid.uuid4()),
                    date=entry_date,
                    account_code=self.CHART_OF_ACCOUNTS["vat_output"]["code"],
                    account_name=self.CHART_OF_ACCOUNTS["vat_output"]["name"],
                    debit_amount=Decimal('0'),
                    credit_amount=tax_amount,
                    description=f"VAT Output: {description}",
                    reference=transaction_id,
                    currency=currency,
                    tax_code="VAT_OUT",
                    customer_id=customer_id
                )
                entries.append(vat_entry)
                
            # Accounts receivable or bank entry (debit)
            total_amount = amount + tax_amount
            
            if payment_received:
                # Payment received - bank account
                bank_entry = AccountingEntry(
                    id=str(uuid.uuid4()),
                    date=entry_date,
                    account_code=self.CHART_OF_ACCOUNTS["bank"]["code"],
                    account_name=self.CHART_OF_ACCOUNTS["bank"]["name"],
                    debit_amount=total_amount,
                    credit_amount=Decimal('0'),
                    description=f"Payment received: {description}",
                    reference=transaction_id,
                    currency=currency,
                    customer_id=customer_id
                )
            else:
                # Invoice issued - accounts receivable
                bank_entry = AccountingEntry(
                    id=str(uuid.uuid4()),
                    date=entry_date,
                    account_code=self.CHART_OF_ACCOUNTS["accounts_receivable"]["code"],
                    account_name=self.CHART_OF_ACCOUNTS["accounts_receivable"]["name"],
                    debit_amount=total_amount,
                    credit_amount=Decimal('0'),
                    description=f"Invoice: {description}",
                    reference=transaction_id,
                    currency=currency,
                    customer_id=customer_id
                )
                
            entries.append(bank_entry)
            
            # Store entries
            for entry in entries:
                self.accounting_entries[entry.id] = entry
                
            logger.info(f"Accounting entries created for transaction {transaction_id}: {len(entries)} entries")
            return entries
            
        except Exception as e:
            logger.error(f"Error creating accounting entries: {str(e)}")
            return []
            
    async def export_accounting_data(
        self,
        period_start: date,
        period_end: date,
        format_type: ReportFormat,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Export accounting data in specified format"""
        try:
            # Filter entries for period
            period_entries = [
                entry for entry in self.accounting_entries.values()
                if (period_start <= entry.date.date() <= period_end and
                    entry.currency == currency)
            ]
            
            if format_type == ReportFormat.CSV:
                return await self._export_csv(period_entries)
            elif format_type == ReportFormat.JSON:
                return await self._export_json(period_entries)
            elif format_type == ReportFormat.XML:
                return await self._export_xml(period_entries)
            elif format_type == ReportFormat.QUICKBOOKS:
                return await self._export_quickbooks(period_entries)
            elif format_type == ReportFormat.XERO:
                return await self._export_xero(period_entries)
            else:
                raise ValueError(f"Unsupported export format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error exporting accounting data: {str(e)}")
            return {"error": str(e)}
            
    async def calculate_vat_return(
        self,
        jurisdiction: TaxJurisdiction,
        period_start: date,
        period_end: date,
        currency: str = "EUR"
    ) -> Dict[str, Any]:
        """Calculate VAT return for submission"""
        try:
            # Get calculations for period
            period_calculations = [
                calc for calc in self.tax_calculations.values()
                if (calc.jurisdiction == jurisdiction and
                    period_start <= calc.calculation_date.date() <= period_end and
                    calc.currency == currency)
            ]
            
            # Calculate VAT totals
            total_output_vat = sum(calc.tax_amount for calc in period_calculations)
            total_net_sales = sum(calc.taxable_amount for calc in period_calculations)
            total_gross_sales = total_net_sales + total_output_vat
            
            # Calculate input VAT (simplified)
            total_input_vat = total_output_vat * Decimal('0.15')  # Assume 15% input VAT
            
            # Net VAT due
            net_vat_due = total_output_vat - total_input_vat
            
            vat_return = {
                "jurisdiction": jurisdiction.value,
                "period": {
                    "start": period_start.isoformat(),
                    "end": period_end.isoformat()
                },
                "currency": currency,
                "vat_summary": {
                    "total_net_sales": float(total_net_sales),
                    "total_gross_sales": float(total_gross_sales),
                    "total_output_vat": float(total_output_vat),
                    "total_input_vat": float(total_input_vat),
                    "net_vat_due": float(net_vat_due)
                },
                "transaction_summary": {
                    "total_transactions": len(period_calculations),
                    "average_transaction_value": float(total_net_sales / len(period_calculations)) if period_calculations else 0
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return vat_return
            
        except Exception as e:
            logger.error(f"Error calculating VAT return: {str(e)}")
            return {"error": str(e)}
            
    async def generate_audit_trail(
        self,
        transaction_id: str
    ) -> Dict[str, Any]:
        """Generate audit trail for transaction"""
        try:
            # Get tax calculation
            tax_calc = self.tax_calculations.get(transaction_id)
            if not tax_calc:
                return {"error": "Transaction not found"}
                
            # Get accounting entries
            related_entries = [
                entry for entry in self.accounting_entries.values()
                if entry.reference == transaction_id
            ]
            
            audit_trail = {
                "transaction_id": transaction_id,
                "tax_calculation": {
                    "jurisdiction": tax_calc.jurisdiction.value,
                    "tax_type": tax_calc.tax_type.value,
                    "taxable_amount": float(tax_calc.taxable_amount),
                    "tax_rate": float(tax_calc.tax_rate),
                    "tax_amount": float(tax_calc.tax_amount),
                    "calculation_date": tax_calc.calculation_date.isoformat(),
                    "rules_applied": tax_calc.rules_applied
                },
                "accounting_entries": [
                    {
                        "id": entry.id,
                        "date": entry.date.isoformat(),
                        "account_code": entry.account_code,
                        "account_name": entry.account_name,
                        "debit_amount": float(entry.debit_amount),
                        "credit_amount": float(entry.credit_amount),
                        "description": entry.description
                    }
                    for entry in related_entries
                ],
                "compliance_status": self._check_compliance_status(tax_calc),
                "generated_at": datetime.now().isoformat()
            }
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Error generating audit trail: {str(e)}")
            return {"error": str(e)}
            
    def _determine_tax_jurisdiction(
        self,
        customer_jurisdiction: TaxJurisdiction,
        supplier_jurisdiction: TaxJurisdiction,
        transaction_type: str,
        product_category: str
    ) -> TaxJurisdiction:
        """Determine applicable tax jurisdiction"""
        
        # EU VAT rules for digital services
        if (customer_jurisdiction in [TaxJurisdiction.GERMANY, TaxJurisdiction.FRANCE, 
                                    TaxJurisdiction.NETHERLANDS, TaxJurisdiction.SWEDEN] and
            product_category == "digital_services"):
            
            if transaction_type == "b2c":
                # B2C digital services - customer jurisdiction
                return customer_jurisdiction
            else:
                # B2B - supplier jurisdiction (with reverse charge)
                return supplier_jurisdiction
        
        # Default to supplier jurisdiction
        return supplier_jurisdiction
        
    def _get_applicable_tax_rules(
        self,
        jurisdiction: TaxJurisdiction,
        amount: Decimal,
        transaction_type: str,
        product_category: str
    ) -> List[TaxRule]:
        """Get applicable tax rules for transaction"""
        
        applicable_rules = []
        
        for rule in self.tax_rules.values():
            if (rule.jurisdiction == jurisdiction and
                (not rule.threshold or amount >= rule.threshold) and
                (not rule.expiry_date or datetime.now() <= rule.expiry_date)):
                applicable_rules.append(rule)
                
        return applicable_rules
        
    def _should_apply_rule(self, rule: TaxRule, amount: Decimal, transaction_type: str) -> bool:
        """Check if tax rule should be applied"""
        
        # Check threshold
        if rule.threshold and amount < rule.threshold:
            return False
            
        # Check conditions
        if rule.conditions:
            # Apply any specific conditions
            pass
            
        return True
        
    def _calculate_rule_tax(self, rule: TaxRule, amount: Decimal) -> Decimal:
        """Calculate tax amount for rule"""
        
        tax_amount = amount * (rule.rate / 100)
        return tax_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    def _check_compliance_status(self, tax_calc: TaxCalculation) -> str:
        """Check compliance status of tax calculation"""
        
        # Perform compliance checks
        if tax_calc.tax_amount >= 0:
            return "compliant"
        else:
            return "non_compliant"
            
    async def _export_csv(self, entries: List[AccountingEntry]) -> Dict[str, Any]:
        """Export entries to CSV format"""
        try:
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers
            writer.writerow([
                'Date', 'Account Code', 'Account Name', 'Description',
                'Debit Amount', 'Credit Amount', 'Reference', 'Currency', 'Customer ID'
            ])
            
            # Data rows
            for entry in entries:
                writer.writerow([
                    entry.date.strftime('%Y-%m-%d'),
                    entry.account_code,
                    entry.account_name,
                    entry.description,
                    float(entry.debit_amount),
                    float(entry.credit_amount),
                    entry.reference,
                    entry.currency,
                    entry.customer_id or ''
                ])
                
            return {
                "format": "csv",
                "content": output.getvalue(),
                "filename": f"accounting_export_{datetime.now().strftime('%Y%m%d')}.csv",
                "entries_count": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            return {"error": str(e)}
            
    async def _export_json(self, entries: List[AccountingEntry]) -> Dict[str, Any]:
        """Export entries to JSON format"""
        try:
            data = {
                "export_date": datetime.now().isoformat(),
                "entries_count": len(entries),
                "entries": [
                    {
                        "id": entry.id,
                        "date": entry.date.isoformat(),
                        "account_code": entry.account_code,
                        "account_name": entry.account_name,
                        "description": entry.description,
                        "debit_amount": float(entry.debit_amount),
                        "credit_amount": float(entry.credit_amount),
                        "reference": entry.reference,
                        "currency": entry.currency,
                        "customer_id": entry.customer_id,
                        "tax_code": entry.tax_code
                    }
                    for entry in entries
                ]
            }
            
            return {
                "format": "json",
                "content": json.dumps(data, indent=2),
                "filename": f"accounting_export_{datetime.now().strftime('%Y%m%d')}.json",
                "entries_count": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            return {"error": str(e)}
            
    async def _export_xml(self, entries: List[AccountingEntry]) -> Dict[str, Any]:
        """Export entries to XML format"""
        try:
            root = ET.Element("AccountingExport")
            root.set("exportDate", datetime.now().isoformat())
            root.set("entriesCount", str(len(entries)))
            
            for entry in entries:
                entry_elem = ET.SubElement(root, "Entry")
                entry_elem.set("id", entry.id)
                
                ET.SubElement(entry_elem, "Date").text = entry.date.isoformat()
                ET.SubElement(entry_elem, "AccountCode").text = entry.account_code
                ET.SubElement(entry_elem, "AccountName").text = entry.account_name
                ET.SubElement(entry_elem, "Description").text = entry.description
                ET.SubElement(entry_elem, "DebitAmount").text = str(entry.debit_amount)
                ET.SubElement(entry_elem, "CreditAmount").text = str(entry.credit_amount)
                ET.SubElement(entry_elem, "Reference").text = entry.reference
                ET.SubElement(entry_elem, "Currency").text = entry.currency
                
                if entry.customer_id:
                    ET.SubElement(entry_elem, "CustomerId").text = entry.customer_id
                if entry.tax_code:
                    ET.SubElement(entry_elem, "TaxCode").text = entry.tax_code
                    
            xml_string = ET.tostring(root, encoding='unicode')
            
            return {
                "format": "xml",
                "content": xml_string,
                "filename": f"accounting_export_{datetime.now().strftime('%Y%m%d')}.xml",
                "entries_count": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error exporting XML: {str(e)}")
            return {"error": str(e)}
            
    async def _export_quickbooks(self, entries: List[AccountingEntry]) -> Dict[str, Any]:
        """Export entries in QuickBooks format"""
        try:
            # QuickBooks IIF format
            output = io.StringIO()
            
            # Header
            output.write("!HDR\tPROD\tVER\tREL\tIIFVER\tDATE\tTIME\tACCNT\n")
            output.write(f"HDR\tAinflue\t2025\tR1\t1\t{datetime.now().strftime('%m/%d/%Y')}\t{datetime.now().strftime('%H:%M:%S')}\tN\n")
            
            # Accounts (if needed)
            output.write("!ACCNT\tNAME\tACCNTTYPE\n")
            for account in self.CHART_OF_ACCOUNTS.values():
                output.write(f"ACCNT\t{account['name']}\t{account['type'].upper()}\n")
                
            # Transactions
            output.write("!TRNS\tTRNSTYPE\tDATE\tACCNT\tNAME\tAMOUNT\tDOCNUM\tMEMO\n")
            
            # Group entries by reference (transaction)
            transactions = {}
            for entry in entries:
                if entry.reference not in transactions:
                    transactions[entry.reference] = []
                transactions[entry.reference].append(entry)
                
            for ref, trans_entries in transactions.items():
                for entry in trans_entries:
                    amount = float(entry.credit_amount - entry.debit_amount)
                    output.write(f"TRNS\tGENERAL JOURNAL\t{entry.date.strftime('%m/%d/%Y')}\t{entry.account_name}\t\t{amount}\t{ref}\t{entry.description}\n")
                    
            return {
                "format": "quickbooks_iif",
                "content": output.getvalue(),
                "filename": f"quickbooks_export_{datetime.now().strftime('%Y%m%d')}.iif",
                "entries_count": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error exporting QuickBooks format: {str(e)}")
            return {"error": str(e)}
            
    async def _export_xero(self, entries: List[AccountingEntry]) -> Dict[str, Any]:
        """Export entries in Xero format"""
        try:
            # Xero CSV format
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Headers for Xero
            writer.writerow([
                '*ContactName', '*InvoiceNumber', '*InvoiceDate', '*DueDate',
                '*Description', '*Quantity', '*UnitAmount', '*AccountCode',
                '*TaxType', '*Currency'
            ])
            
            # Convert entries to Xero format
            for entry in entries:
                if entry.credit_amount > 0:  # Revenue entries
                    writer.writerow([
                        entry.customer_id or 'Unknown Customer',
                        entry.reference,
                        entry.date.strftime('%d/%m/%Y'),
                        (entry.date + timedelta(days=30)).strftime('%d/%m/%Y'),
                        entry.description,
                        1,
                        float(entry.credit_amount),
                        entry.account_code,
                        entry.tax_code or 'Tax',
                        entry.currency
                    ])
                    
            return {
                "format": "xero_csv",
                "content": output.getvalue(),
                "filename": f"xero_export_{datetime.now().strftime('%Y%m%d')}.csv",
                "entries_count": len(entries)
            }
            
        except Exception as e:
            logger.error(f"Error exporting Xero format: {str(e)}")
            return {"error": str(e)}


# Global tax engine instance
tax_engine = TaxComplianceEngine()


async def calculate_transaction_tax(
    transaction_id: str,
    amount: Decimal,
    currency: str,
    customer_country: str,
    supplier_country: str = "DE"
) -> TaxCalculation:
    """Global function to calculate tax for transaction"""
    customer_jurisdiction = TaxJurisdiction(customer_country)
    supplier_jurisdiction = TaxJurisdiction(supplier_country)
    
    return await tax_engine.calculate_tax(
        transaction_id=transaction_id,
        amount=amount,
        currency=currency,
        customer_jurisdiction=customer_jurisdiction,
        supplier_jurisdiction=supplier_jurisdiction
    )


async def export_financial_data(
    start_date: date,
    end_date: date,
    format_type: str,
    currency: str = "EUR"
) -> Dict[str, Any]:
    """Global function to export financial data"""
    return await tax_engine.export_accounting_data(
        period_start=start_date,
        period_end=end_date,
        format_type=ReportFormat(format_type),
        currency=currency
    )