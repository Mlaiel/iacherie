"""
Quantum-Ready Encryption Module for Ainflue Platform

This module provides quantum-resistant cryptographic implementations
to protect against future quantum computer attacks. It includes:

- Post-quantum cryptography (lattice-based encryption)
- Quantum key distribution protocols
- True quantum random number generation

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .post_quantum_crypto import PostQuantumCrypto, LatticeBasedEncryption
from .quantum_key_distribution import QuantumKeyDistribution, QKDProtocol
from .quantum_random_generator import QuantumRandomGenerator, TrueRandomSource

__all__ = [
    "PostQuantumCrypto",
    "LatticeBasedEncryption", 
    "QuantumKeyDistribution",
    "QKDProtocol",
    "QuantumRandomGenerator",
    "TrueRandomSource"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"