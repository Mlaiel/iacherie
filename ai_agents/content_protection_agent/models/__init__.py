"""Protection Models Package - Common data structures for protection agents"""

from .protection_models import (
    ContentType,
    ViolationSeverity,
    ProtectionStatus,
    ProtectionRequest,
    ProtectionResult,
    PlatformConfig,
    ViolationReport,
    FingerprintResult,
    MonitoringSession,
    PlatformScanResult
)

__all__ = [
    "ContentType",
    "ViolationSeverity", 
    "ProtectionStatus",
    "ProtectionRequest",
    "ProtectionResult",
    "PlatformConfig",
    "ViolationReport",
    "FingerprintResult",
    "MonitoringSession",
    "PlatformScanResult"
]