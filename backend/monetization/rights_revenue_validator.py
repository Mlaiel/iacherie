"""Rights Revenue Validator - Rights-based Revenue Validation System
===================================================================

Enterprise-grade rights-based revenue validation system providing comprehensive
rights verification, revenue authenticity validation, licensing compliance,
and automated rights-based revenue distribution for content creators.

Architecture: Enterprise Production-Ready (Backend Level 3)
Module: backend/monetization/rights_revenue_validator.py

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
import hashlib

logger = logging.getLogger(__name__)


class RightsType(str, Enum):
    """Types of content rights."""
    COPYRIGHT = "copyright"
    TRADEMARK = "trademark"
    PATENT = "patent"
    PUBLICITY_RIGHTS = "publicity_rights"
    PERFORMANCE_RIGHTS = "performance_rights"
    MECHANICAL_RIGHTS = "mechanical_rights"
    SYNCHRONIZATION_RIGHTS = "synchronization_rights"
    MASTER_RECORDING_RIGHTS = "master_recording_rights"


class ValidationStatus(str, Enum):
    """Rights validation status."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    DISPUTED = "disputed"
    EXPIRED = "expired"
    SUSPENDED = "suspended"


class RevenueSource(str, Enum):
    """Revenue source types."""
    STREAMING = "streaming"
    DOWNLOADS = "downloads"
    LICENSING = "licensing"
    MERCHANDISE = "merchandise"
    LIVE_PERFORMANCE = "live_performance"
    SYNC_LICENSING = "sync_licensing"
    MECHANICAL_ROYALTIES = "mechanical_royalties"
    PERFORMANCE_ROYALTIES = "performance_royalties"


@dataclass
class RightsRecord:
    """Rights ownership record."""
    id: UUID = field(default_factory=uuid4)
    content_id: UUID = None
    rights_holder_id: UUID = None
    rights_type: RightsType = RightsType.COPYRIGHT
    ownership_percentage: Decimal = Decimal('100.00')
    territory: List[str] = field(default_factory=list)
    start_date: datetime = field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    license_terms: Dict[str, Any] = field(default_factory=dict)
    verification_documents: List[str] = field(default_factory=list)
    validation_status: ValidationStatus = ValidationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RevenueTransaction:
    """Revenue transaction record."""
    id: UUID = field(default_factory=uuid4)
    content_id: UUID = None
    revenue_source: RevenueSource = RevenueSource.STREAMING
    gross_amount: Decimal = Decimal('0.00')
    net_amount: Decimal = Decimal('0.00')
    currency: str = "USD"
    transaction_date: datetime = field(default_factory=datetime.utcnow)
    platform: str = ""
    territory: str = ""
    validation_status: ValidationStatus = ValidationStatus.PENDING
    rights_validated: bool = False
    distribution_calculated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Rights validation result."""
    transaction_id: UUID = None
    validation_status: ValidationStatus = ValidationStatus.PENDING
    validated_rights: List[RightsRecord] = field(default_factory=list)
    validation_issues: List[str] = field(default_factory=list)
    revenue_distribution: Dict[UUID, Decimal] = field(default_factory=dict)
    validation_timestamp: datetime = field(default_factory=datetime.utcnow)
    validator_id: Optional[UUID] = None
    confidence_score: float = 0.0


class RightsRevenueValidator:
    """Advanced rights-based revenue validation engine."""
    
    def __init__(self):
        """Initialize rights revenue validator."""
        self.rights_records: Dict[UUID, RightsRecord] = {}
        self.revenue_transactions: Dict[UUID, RevenueTransaction] = {}
        self.validation_results: Dict[UUID, ValidationResult] = {}
        self.validation_rules: Dict[str, Any] = {}
        self._load_validation_rules()
        
    def _load_validation_rules(self) -> None:
        """Load rights validation rules."""
        self.validation_rules = {
            'minimum_ownership_percentage': Decimal('0.01'),  # 0.01%
            'maximum_ownership_percentage': Decimal('100.00'),  # 100%
            'required_documents': {
                RightsType.COPYRIGHT: ['copyright_certificate', 'creation_proof'],
                RightsType.TRADEMARK: ['trademark_registration', 'usage_proof'],
                RightsType.PERFORMANCE_RIGHTS: ['performance_license', 'venue_agreement'],
                RightsType.MECHANICAL_RIGHTS: ['mechanical_license', 'publisher_agreement']
            },
            'territory_validation': {
                'global': ['worldwide', 'global', 'international'],
                'regional': ['US', 'EU', 'UK', 'CA', 'AU', 'JP', 'BR', 'IN'],
                'exclusive_territories': []
            },
            'revenue_thresholds': {
                'micro_transaction': Decimal('0.01'),
                'standard_transaction': Decimal('10.00'),
                'high_value_transaction': Decimal('1000.00'),
                'enterprise_transaction': Decimal('10000.00')
            }
        }
        
    async def register_rights_record(
        self,
        content_id: UUID,
        rights_holder_id: UUID,
        rights_data: Dict[str, Any]
    ) -> RightsRecord:
        """Register new rights record."""
        try:
            rights_record = RightsRecord(
                content_id=content_id,
                rights_holder_id=rights_holder_id,
                rights_type=RightsType(rights_data.get('rights_type', 'copyright')),
                ownership_percentage=Decimal(str(rights_data.get('ownership_percentage', '100.00'))),
                territory=rights_data.get('territory', ['worldwide']),
                start_date=rights_data.get('start_date', datetime.utcnow()),
                end_date=rights_data.get('end_date'),
                license_terms=rights_data.get('license_terms', {}),
                verification_documents=rights_data.get('verification_documents', [])
            )
            
            # Validate rights record
            validation_result = await self._validate_rights_record(rights_record)
            rights_record.validation_status = validation_result['status']
            
            self.rights_records[rights_record.id] = rights_record
            
            logger.info(f"Registered rights record: {rights_record.id}")
            return rights_record
            
        except Exception as e:
            logger.error(f"Error registering rights record: {e}")
            raise
            
    async def _validate_rights_record(self, rights_record: RightsRecord) -> Dict[str, Any]:
        """Validate rights record."""
        try:
            validation_issues = []
            
            # Validate ownership percentage
            if rights_record.ownership_percentage < self.validation_rules['minimum_ownership_percentage']:
                validation_issues.append("Ownership percentage below minimum threshold")
                
            if rights_record.ownership_percentage > self.validation_rules['maximum_ownership_percentage']:
                validation_issues.append("Ownership percentage exceeds maximum")
                
            # Validate required documents
            required_docs = self.validation_rules['required_documents'].get(
                rights_record.rights_type, []
            )
            
            missing_docs = [
                doc for doc in required_docs
                if doc not in rights_record.verification_documents
            ]
            
            if missing_docs:
                validation_issues.append(f"Missing required documents: {', '.join(missing_docs)}")
                
            # Validate territory
            if not rights_record.territory:
                validation_issues.append("Territory not specified")
                
            # Check for overlapping rights
            overlapping_rights = await self._check_overlapping_rights(rights_record)
            if overlapping_rights:
                validation_issues.append("Overlapping rights detected")
                
            # Determine validation status
            if not validation_issues:
                status = ValidationStatus.VERIFIED
            elif len(validation_issues) <= 2:
                status = ValidationStatus.PENDING
            else:
                status = ValidationStatus.REJECTED
                
            return {
                'status': status,
                'issues': validation_issues,
                'confidence': 1.0 - (len(validation_issues) * 0.2)
            }
            
        except Exception as e:
            logger.error(f"Error validating rights record: {e}")
            return {
                'status': ValidationStatus.REJECTED,
                'issues': [f"Validation error: {str(e)}"],
                'confidence': 0.0
            }
            
    async def _check_overlapping_rights(self, rights_record: RightsRecord) -> List[RightsRecord]:
        """Check for overlapping rights records."""
        try:
            overlapping = []
            
            for existing_record in self.rights_records.values():
                if (existing_record.content_id == rights_record.content_id
                    and existing_record.rights_type == rights_record.rights_type
                    and existing_record.validation_status == ValidationStatus.VERIFIED):
                    
                    # Check territory overlap
                    territory_overlap = any(
                        territory in existing_record.territory
                        for territory in rights_record.territory
                    )
                    
                    # Check time overlap
                    time_overlap = self._check_time_overlap(rights_record, existing_record)
                    
                    if territory_overlap and time_overlap:
                        overlapping.append(existing_record)
                        
            return overlapping
            
        except Exception as e:
            logger.error(f"Error checking overlapping rights: {e}")
            return []
            
    def _check_time_overlap(
        self,
        record1: RightsRecord,
        record2: RightsRecord
    ) -> bool:
        """Check if two rights records have time overlap."""
        try:
            start1 = record1.start_date
            end1 = record1.end_date or datetime.max
            start2 = record2.start_date
            end2 = record2.end_date or datetime.max
            
            return start1 < end2 and start2 < end1
            
        except Exception as e:
            logger.error(f"Error checking time overlap: {e}")
            return False
            
    async def validate_revenue_transaction(
        self,
        transaction_data: Dict[str, Any]
    ) -> ValidationResult:
        """Validate revenue transaction against rights records."""
        try:
            # Create revenue transaction
            transaction = RevenueTransaction(
                content_id=UUID(transaction_data['content_id']),
                revenue_source=RevenueSource(transaction_data.get('revenue_source', 'streaming')),
                gross_amount=Decimal(str(transaction_data['gross_amount'])),
                net_amount=Decimal(str(transaction_data.get('net_amount', transaction_data['gross_amount']))),
                currency=transaction_data.get('currency', 'USD'),
                transaction_date=transaction_data.get('transaction_date', datetime.utcnow()),
                platform=transaction_data.get('platform', ''),
                territory=transaction_data.get('territory', ''),
                metadata=transaction_data.get('metadata', {})
            )
            
            self.revenue_transactions[transaction.id] = transaction
            
            # Find applicable rights records
            applicable_rights = await self._find_applicable_rights(transaction)
            
            # Validate rights coverage
            validation_result = await self._validate_rights_coverage(transaction, applicable_rights)
            
            # Calculate revenue distribution
            if validation_result.validation_status == ValidationStatus.VERIFIED:
                revenue_distribution = await self._calculate_revenue_distribution(
                    transaction, applicable_rights
                )
                validation_result.revenue_distribution = revenue_distribution
                transaction.distribution_calculated = True
                
            # Update transaction status
            transaction.validation_status = validation_result.validation_status
            transaction.rights_validated = True
            
            # Store validation result
            self.validation_results[transaction.id] = validation_result
            
            logger.info(f"Validated revenue transaction: {transaction.id}")
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating revenue transaction: {e}")
            
            # Create error validation result
            error_result = ValidationResult(
                transaction_id=transaction.id if 'transaction' in locals() else None,
                validation_status=ValidationStatus.REJECTED,
                validation_issues=[f"Validation error: {str(e)}"],
                confidence_score=0.0
            )
            
            return error_result
            
    async def _find_applicable_rights(
        self,
        transaction: RevenueTransaction
    ) -> List[RightsRecord]:
        """Find rights records applicable to transaction."""
        try:
            applicable_rights = []
            
            for rights_record in self.rights_records.values():
                if (rights_record.content_id == transaction.content_id
                    and rights_record.validation_status == ValidationStatus.VERIFIED):
                    
                    # Check territory applicability
                    territory_applicable = self._check_territory_applicability(
                        rights_record.territory, transaction.territory
                    )
                    
                    # Check time applicability
                    time_applicable = self._check_time_applicability(
                        rights_record, transaction.transaction_date
                    )
                    
                    # Check rights type applicability
                    rights_applicable = self._check_rights_type_applicability(
                        rights_record.rights_type, transaction.revenue_source
                    )
                    
                    if territory_applicable and time_applicable and rights_applicable:
                        applicable_rights.append(rights_record)
                        
            return applicable_rights
            
        except Exception as e:
            logger.error(f"Error finding applicable rights: {e}")
            return []
            
    def _check_territory_applicability(
        self,
        rights_territory: List[str],
        transaction_territory: str
    ) -> bool:
        """Check if rights territory covers transaction territory."""
        try:
            if not transaction_territory:
                return True  # No territory restriction
                
            # Check for global rights
            global_territories = self.validation_rules['territory_validation']['global']
            if any(territory.lower() in global_territories for territory in rights_territory):
                return True
                
            # Check for specific territory match
            return transaction_territory in rights_territory
            
        except Exception as e:
            logger.error(f"Error checking territory applicability: {e}")
            return False
            
    def _check_time_applicability(
        self,
        rights_record: RightsRecord,
        transaction_date: datetime
    ) -> bool:
        """Check if rights are valid at transaction time."""
        try:
            start_date = rights_record.start_date
            end_date = rights_record.end_date or datetime.max
            
            return start_date <= transaction_date <= end_date
            
        except Exception as e:
            logger.error(f"Error checking time applicability: {e}")
            return False
            
    def _check_rights_type_applicability(
        self,
        rights_type: RightsType,
        revenue_source: RevenueSource
    ) -> bool:
        """Check if rights type covers revenue source."""
        try:
            applicability_map = {
                RightsType.COPYRIGHT: [
                    RevenueSource.STREAMING,
                    RevenueSource.DOWNLOADS,
                    RevenueSource.LICENSING
                ],
                RightsType.PERFORMANCE_RIGHTS: [
                    RevenueSource.STREAMING,
                    RevenueSource.LIVE_PERFORMANCE,
                    RevenueSource.PERFORMANCE_ROYALTIES
                ],
                RightsType.MECHANICAL_RIGHTS: [
                    RevenueSource.DOWNLOADS,
                    RevenueSource.MECHANICAL_ROYALTIES
                ],
                RightsType.SYNCHRONIZATION_RIGHTS: [
                    RevenueSource.SYNC_LICENSING
                ],
                RightsType.MASTER_RECORDING_RIGHTS: [
                    RevenueSource.STREAMING,
                    RevenueSource.DOWNLOADS,
                    RevenueSource.LICENSING
                ]
            }
            
            applicable_sources = applicability_map.get(rights_type, [])
            return revenue_source in applicable_sources
            
        except Exception as e:
            logger.error(f"Error checking rights type applicability: {e}")
            return False
            
    async def _validate_rights_coverage(
        self,
        transaction: RevenueTransaction,
        applicable_rights: List[RightsRecord]
    ) -> ValidationResult:
        """Validate that rights provide adequate coverage."""
        try:
            validation_issues = []
            validated_rights = []
            
            if not applicable_rights:
                validation_issues.append("No applicable rights found for transaction")
                
            else:
                # Check total ownership coverage
                total_ownership = sum(
                    rights.ownership_percentage for rights in applicable_rights
                )
                
                if total_ownership < Decimal('100.00'):
                    validation_issues.append(
                        f"Insufficient ownership coverage: {total_ownership}% of 100%"
                    )
                elif total_ownership > Decimal('100.00'):
                    validation_issues.append(
                        f"Over-allocation of ownership: {total_ownership}% exceeds 100%"
                    )
                    
                # Validate individual rights
                for rights_record in applicable_rights:
                    rights_validation = await self._validate_individual_rights(
                        rights_record, transaction
                    )
                    
                    if rights_validation['valid']:
                        validated_rights.append(rights_record)
                    else:
                        validation_issues.extend(rights_validation['issues'])
                        
            # Determine validation status
            if not validation_issues and validated_rights:
                status = ValidationStatus.VERIFIED
                confidence = 1.0
            elif validation_issues and validated_rights:
                status = ValidationStatus.PENDING
                confidence = 0.7
            else:
                status = ValidationStatus.REJECTED
                confidence = 0.0
                
            return ValidationResult(
                transaction_id=transaction.id,
                validation_status=status,
                validated_rights=validated_rights,
                validation_issues=validation_issues,
                confidence_score=confidence
            )
            
        except Exception as e:
            logger.error(f"Error validating rights coverage: {e}")
            return ValidationResult(
                transaction_id=transaction.id,
                validation_status=ValidationStatus.REJECTED,
                validation_issues=[f"Coverage validation error: {str(e)}"],
                confidence_score=0.0
            )
            
    async def _validate_individual_rights(
        self,
        rights_record: RightsRecord,
        transaction: RevenueTransaction
    ) -> Dict[str, Any]:
        """Validate individual rights record."""
        try:
            issues = []
            
            # Check if rights are still valid
            if rights_record.validation_status != ValidationStatus.VERIFIED:
                issues.append(f"Rights record {rights_record.id} not verified")
                
            # Check expiration
            if rights_record.end_date and rights_record.end_date < datetime.utcnow():
                issues.append(f"Rights record {rights_record.id} has expired")
                
            # Check license terms compliance
            if rights_record.license_terms:
                compliance_check = await self._check_license_compliance(
                    rights_record.license_terms, transaction
                )
                if not compliance_check['compliant']:
                    issues.extend(compliance_check['violations'])
                    
            return {
                'valid': len(issues) == 0,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Error validating individual rights: {e}")
            return {
                'valid': False,
                'issues': [f"Individual rights validation error: {str(e)}"]
            }
            
    async def _check_license_compliance(
        self,
        license_terms: Dict[str, Any],
        transaction: RevenueTransaction
    ) -> Dict[str, Any]:
        """Check compliance with license terms."""
        try:
            violations = []
            
            # Check revenue thresholds
            min_revenue = license_terms.get('minimum_revenue')
            if min_revenue and transaction.net_amount < Decimal(str(min_revenue)):
                violations.append(f"Transaction below minimum revenue threshold: {min_revenue}")
                
            max_revenue = license_terms.get('maximum_revenue')
            if max_revenue and transaction.net_amount > Decimal(str(max_revenue)):
                violations.append(f"Transaction exceeds maximum revenue threshold: {max_revenue}")
                
            # Check platform restrictions
            allowed_platforms = license_terms.get('allowed_platforms')
            if allowed_platforms and transaction.platform not in allowed_platforms:
                violations.append(f"Platform {transaction.platform} not allowed")
                
            # Check territory restrictions
            allowed_territories = license_terms.get('allowed_territories')
            if allowed_territories and transaction.territory not in allowed_territories:
                violations.append(f"Territory {transaction.territory} not allowed")
                
            return {
                'compliant': len(violations) == 0,
                'violations': violations
            }
            
        except Exception as e:
            logger.error(f"Error checking license compliance: {e}")
            return {
                'compliant': False,
                'violations': [f"License compliance check error: {str(e)}"]
            }
            
    async def _calculate_revenue_distribution(
        self,
        transaction: RevenueTransaction,
        validated_rights: List[RightsRecord]
    ) -> Dict[UUID, Decimal]:
        """Calculate revenue distribution based on validated rights."""
        try:
            distribution = {}
            
            # Calculate total ownership
            total_ownership = sum(
                rights.ownership_percentage for rights in validated_rights
            )
            
            if total_ownership == Decimal('0.00'):
                return distribution
                
            # Distribute revenue proportionally
            for rights_record in validated_rights:
                ownership_ratio = rights_record.ownership_percentage / total_ownership
                rights_holder_share = transaction.net_amount * ownership_ratio
                
                # Apply any license-specific adjustments
                adjusted_share = await self._apply_license_adjustments(
                    rights_holder_share, rights_record.license_terms
                )
                
                distribution[rights_record.rights_holder_id] = adjusted_share
                
            return distribution
            
        except Exception as e:
            logger.error(f"Error calculating revenue distribution: {e}")
            return {}
            
    async def _apply_license_adjustments(
        self,
        base_amount: Decimal,
        license_terms: Dict[str, Any]
    ) -> Decimal:
        """Apply license-specific adjustments to revenue share."""
        try:
            adjusted_amount = base_amount
            
            # Apply percentage adjustments
            percentage_adjustment = license_terms.get('revenue_percentage_adjustment')
            if percentage_adjustment:
                adjustment_factor = Decimal(str(percentage_adjustment)) / Decimal('100.00')
                adjusted_amount = base_amount * (Decimal('1.00') + adjustment_factor)
                
            # Apply fixed adjustments
            fixed_adjustment = license_terms.get('fixed_revenue_adjustment')
            if fixed_adjustment:
                adjusted_amount += Decimal(str(fixed_adjustment))
                
            # Apply minimum guarantees
            minimum_guarantee = license_terms.get('minimum_guarantee')
            if minimum_guarantee:
                adjusted_amount = max(adjusted_amount, Decimal(str(minimum_guarantee)))
                
            return max(adjusted_amount, Decimal('0.00'))  # Ensure non-negative
            
        except Exception as e:
            logger.error(f"Error applying license adjustments: {e}")
            return base_amount
            
    async def get_validation_summary(
        self,
        content_id: UUID,
        time_period: timedelta = timedelta(days=30)
    ) -> Dict[str, Any]:
        """Get validation summary for content."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - time_period
            
            # Get transactions for content in time period
            transactions = [
                transaction for transaction in self.revenue_transactions.values()
                if transaction.content_id == content_id
                and start_date <= transaction.transaction_date <= end_date
            ]
            
            # Get rights records for content
            rights = [
                rights for rights in self.rights_records.values()
                if rights.content_id == content_id
            ]
            
            # Calculate summary statistics
            total_transactions = len(transactions)
            verified_transactions = len([
                t for t in transactions 
                if t.validation_status == ValidationStatus.VERIFIED
            ])
            
            total_revenue = sum(t.net_amount for t in transactions)
            verified_revenue = sum(
                t.net_amount for t in transactions 
                if t.validation_status == ValidationStatus.VERIFIED
            )
            
            return {
                'content_id': content_id,
                'time_period_days': time_period.days,
                'rights_records': {
                    'total': len(rights),
                    'verified': len([r for r in rights if r.validation_status == ValidationStatus.VERIFIED]),
                    'pending': len([r for r in rights if r.validation_status == ValidationStatus.PENDING]),
                    'rejected': len([r for r in rights if r.validation_status == ValidationStatus.REJECTED])
                },
                'transactions': {
                    'total': total_transactions,
                    'verified': verified_transactions,
                    'verification_rate': verified_transactions / total_transactions if total_transactions > 0 else 0.0
                },
                'revenue': {
                    'total': float(total_revenue),
                    'verified': float(verified_revenue),
                    'verification_coverage': float(verified_revenue / total_revenue) if total_revenue > 0 else 0.0
                },
                'validation_health': {
                    'rights_coverage': len([r for r in rights if r.validation_status == ValidationStatus.VERIFIED]) / len(rights) if rights else 0.0,
                    'transaction_success_rate': verified_transactions / total_transactions if total_transactions > 0 else 0.0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting validation summary: {e}")
            return {'error': str(e)}


# Example usage and testing
async def main():
    """Test rights revenue validation functionality."""
    validator = RightsRevenueValidator()
    
    # Register rights records
    content_id = uuid4()
    creator_id = uuid4()
    
    rights_data = {
        'rights_type': 'copyright',
        'ownership_percentage': '100.00',
        'territory': ['US', 'EU'],
        'verification_documents': ['copyright_certificate', 'creation_proof'],
        'license_terms': {
            'minimum_revenue': '10.00',
            'allowed_platforms': ['spotify', 'youtube', 'apple_music']
        }
    }
    
    rights_record = await validator.register_rights_record(
        content_id, creator_id, rights_data
    )
    print(f"Registered rights record: {rights_record.id}")
    
    # Validate revenue transaction
    transaction_data = {
        'content_id': str(content_id),
        'revenue_source': 'streaming',
        'gross_amount': '50.00',
        'net_amount': '40.00',
        'platform': 'spotify',
        'territory': 'US'
    }
    
    validation_result = await validator.validate_revenue_transaction(transaction_data)
    print(f"Validation result: {validation_result.validation_status}")
    print(f"Revenue distribution: {validation_result.revenue_distribution}")
    
    # Get validation summary
    summary = await validator.get_validation_summary(content_id)
    print(f"Validation summary: {summary}")


if __name__ == "__main__":
    asyncio.run(main())