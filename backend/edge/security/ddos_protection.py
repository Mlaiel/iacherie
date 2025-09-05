"""DDoS Protection Module - simplified version already included in intrusion_detection.py"""

from .intrusion_detection import DDoSProtection, DDoSAttackType, MitigationStrategy, create_ddos_protection

# Re-export for compatibility
AttackType = DDoSAttackType

__all__ = [
    "DDoSProtection",
    "AttackType", 
    "DDoSAttackType",
    "MitigationStrategy",
    "create_ddos_protection"
]