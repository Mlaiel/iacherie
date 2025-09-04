# GDPR Service Module

## Overview

The GDPR Service (`backend/services/gdpr.py`) is a unified module that implements the three required GDPR compliance features for the Ainflue platform:

1. **Gestion consentements** (Consent Management)
2. **Export/suppression données** (Data Export/Deletion)
3. **Audit conformité** (Compliance Audit)

## Features

### 1. Consent Management (Gestion consentements)

Comprehensive consent management system providing:

- **Consent Collection**: `collect_consent(request: ConsentRequest)`
  - Granular consent for multiple purposes
  - IP address and user agent tracking
  - Configurable expiration periods
  
- **Consent Withdrawal**: `withdraw_consent(user_id, purposes, reason)`
  - Easy consent withdrawal process
  - Audit trail for all withdrawals
  - Automatic data processing updates

- **Consent Status Checking**: `check_consent_status(user_id, purpose)`
  - Real-time consent status validation
  - Purpose-specific consent checking
  - GDPR-compliant consent tracking

### 2. Data Export/Deletion (Export/suppression données)

Full data subject rights implementation:

- **Data Export**: `export_user_data(request: DataExportRequest)`
  - Multiple format support (JSON, CSV, XML)
  - Selective data export by type
  - Metadata inclusion options
  - Secure download mechanisms

- **Data Deletion**: `delete_user_data(request: DataDeletionRequest)`
  - Complete or selective data erasure
  - Retention exception handling
  - Legal compliance tracking
  - 30-day processing timeline

- **Request Status Tracking**: `get_gdpr_request_status(request_id)`
  - Real-time status updates
  - Progress monitoring
  - Completion notifications

### 3. Compliance Audit (Audit conformité)

Comprehensive GDPR compliance monitoring:

- **Compliance Auditing**: `run_compliance_audit()`
  - Automated compliance scoring
  - Multi-category assessment
  - Risk level evaluation
  - Actionable recommendations

- **Compliance Reporting**: `get_compliance_report()`
  - Detailed compliance reports
  - Executive summary views
  - Historical trend analysis
  - Regulatory requirement mapping

## Usage

### Basic Service Creation

```python
from backend.services.gdpr import create_gdpr_service, ConsentRequest

# Create service with configuration
service = create_gdpr_service({
    'encryption_enabled': True,
    'automated_erasure': True,
    'data_retention_days': 2555,  # 7 years
    'consent_expiry_days': 730    # 2 years
})
```

### Consent Management Example

```python
# Collect user consent
consent_request = ConsentRequest(
    user_id="user-123",
    purposes=["analytics", "marketing"],
    consent_values={"analytics": True, "marketing": False},
    collection_context={"method": "web", "ip_address": "192.168.1.1"}
)

result = await service.collect_consent(consent_request)
```

### Data Export Example

```python
from backend.services.gdpr import DataExportRequest

# Export user data
export_request = DataExportRequest(
    user_id="user-123",
    export_format="json",
    include_metadata=True
)

result = await service.export_user_data(export_request)
```

### Compliance Audit Example

```python
# Run compliance audit
audit_result = await service.run_compliance_audit()
print(f"Compliance Score: {audit_result.compliance_score}%")
print(f"Status: {audit_result.status}")
```

## Integration

The GDPR Service integrates with existing platform components:

- **GDPRComplianceManager**: For enterprise-level GDPR operations
- **ConsentManager**: For granular consent management
- **Audit Systems**: For compliance monitoring and reporting

## Configuration

The service supports comprehensive configuration:

```python
config = {
    'encryption_enabled': True,          # Enable data encryption
    'automated_erasure': True,           # Auto-delete expired data
    'data_retention_days': 2555,         # Default retention period
    'consent_expiry_days': 730,          # Consent validity period
    'audit_retention_days': 365,         # Audit log retention
    'enable_compliance_monitoring': True  # Real-time monitoring
}
```

## Testing

Run the test suite:

```bash
python backend/tests/test_services/test_gdpr_service.py
```

The test suite covers:
- Service initialization and configuration
- All three GDPR feature interfaces
- Integration with existing components
- Async functionality testing

## API Reference

### Service Methods

- `get_service_status()`: Get service health and status
- `collect_consent(request)`: Collect user consent
- `withdraw_consent(user_id, purposes, reason)`: Withdraw consent
- `check_consent_status(user_id, purpose)`: Check consent status
- `export_user_data(request)`: Export user data
- `delete_user_data(request)`: Delete user data
- `get_gdpr_request_status(request_id)`: Get request status
- `run_compliance_audit()`: Run compliance audit
- `get_compliance_report()`: Generate compliance report

### Data Models

- `ConsentRequest`: Consent collection request
- `DataExportRequest`: Data export request
- `DataDeletionRequest`: Data deletion request
- `ComplianceAuditResult`: Audit result data
- `GDPRServiceConfig`: Service configuration

## Error Handling

The service provides specific exception types:

- `GDPRServiceError`: Base GDPR service exception
- `ConsentManagementError`: Consent operation errors
- `DataExportError`: Data export/deletion errors
- `ComplianceAuditError`: Audit operation errors

## Security

The GDPR Service implements enterprise-grade security:

- End-to-end encryption for personal data
- Secure audit trails for all operations
- IP address and user agent tracking
- Automated security compliance checking

## Compliance

The service ensures full GDPR compliance:

- Article 7: Consent management
- Article 15: Right of access (data export)
- Article 17: Right to erasure (data deletion)
- Article 18: Right to restriction of processing
- Article 20: Right to data portability
- Article 30: Records of processing activities

## Author

**Fahed Mlaiel** <mlaiel@live.de>  
Copyright (c) 2025 IA Influencer Agent Platform  
All Rights Reserved