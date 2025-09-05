"""Secure Tunneling Module - simplified version already included in intrusion_detection.py"""

from .intrusion_detection import SecureTunnel, TunnelProtocol, EncryptionMethod, create_secure_tunnel

__all__ = [
    "SecureTunnel",
    "TunnelProtocol",
    "EncryptionMethod", 
    "create_secure_tunnel"
]