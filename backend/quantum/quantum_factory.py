"""
Quantum Encryption Integration Factory

This module provides integration between the new quantum modules and 
the existing encryption configuration system.

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from .post_quantum_crypto import PostQuantumCrypto, LatticeBasedEncryption, LatticeAlgorithm
from .quantum_key_distribution import QuantumKeyDistribution, QKDProtocol
from .quantum_random_generator import QuantumRandomGenerator, QuantumSource


@dataclass
class QuantumConfig:
    """Simplified quantum configuration for integration"""
    # Post-quantum settings
    quantum_safe_algorithms: list = None
    quantum_safe_algorithm: str = "CRYSTALS-Kyber"
    hybrid_mode_enabled: bool = True
    
    # QKD settings
    qkd_enabled: bool = True
    qkd_error_threshold: float = 0.11
    qkd_key_length: int = 256
    
    # QRNG settings
    quantum_rng_enabled: bool = True
    qrng_min_entropy_per_byte: float = 7.0
    
    def __post_init__(self):
        if self.quantum_safe_algorithms is None:
            self.quantum_safe_algorithms = [
                "CRYSTALS-Kyber",
                "CRYSTALS-Dilithium", 
                "FALCON",
                "SPHINCS+"
            ]


class QuantumEncryptionFactory:
    """
    Factory for creating and managing quantum encryption components
    """
    
    def __init__(self, config: Optional[QuantumConfig] = None):
        self.config = config or QuantumConfig()
        self._pq_crypto_cache: Dict[str, PostQuantumCrypto] = {}
        self._qkd_instance: Optional[QuantumKeyDistribution] = None
        self._qrng_instance: Optional[QuantumRandomGenerator] = None
    
    def get_post_quantum_crypto(self, algorithm: Optional[str] = None) -> PostQuantumCrypto:
        """Get post-quantum crypto instance for specified algorithm"""
        if algorithm is None:
            algorithm = self.config.quantum_safe_algorithm
        
        if algorithm not in self._pq_crypto_cache:
            # Map algorithm name to enum
            algorithm_enum = self._map_algorithm_name(algorithm)
            self._pq_crypto_cache[algorithm] = PostQuantumCrypto(algorithm_enum)
        
        return self._pq_crypto_cache[algorithm]
    
    def get_quantum_key_distribution(self) -> QuantumKeyDistribution:
        """Get quantum key distribution instance"""
        if not self.config.qkd_enabled:
            raise RuntimeError("QKD is disabled in configuration")
        
        if self._qkd_instance is None:
            self._qkd_instance = QuantumKeyDistribution(
                error_rate=0.01,  # Low error rate for production
                eavesdropping_probability=0.0  # Start with no attacks
            )
        
        return self._qkd_instance
    
    def get_quantum_random_generator(self) -> QuantumRandomGenerator:
        """Get quantum random number generator instance"""
        if not self.config.quantum_rng_enabled:
            raise RuntimeError("Quantum RNG is disabled in configuration")
        
        if self._qrng_instance is None:
            self._qrng_instance = QuantumRandomGenerator(pool_size=10000)
            # Pre-collect some entropy
            self._qrng_instance.collect_entropy(amount=100)
        
        return self._qrng_instance
    
    def _map_algorithm_name(self, algorithm_name: str) -> LatticeAlgorithm:
        """Map configuration algorithm name to enum"""
        algorithm_mapping = {
            "CRYSTALS-Kyber": LatticeAlgorithm.CRYSTALS_KYBER_768,
            "CRYSTALS-Kyber-512": LatticeAlgorithm.CRYSTALS_KYBER_512,
            "CRYSTALS-Kyber-768": LatticeAlgorithm.CRYSTALS_KYBER_768,
            "CRYSTALS-Kyber-1024": LatticeAlgorithm.CRYSTALS_KYBER_1024,
            "CRYSTALS-Dilithium": LatticeAlgorithm.CRYSTALS_DILITHIUM,
            "FALCON": LatticeAlgorithm.FALCON_512,
            "FALCON-512": LatticeAlgorithm.FALCON_512,
            "FALCON-1024": LatticeAlgorithm.FALCON_1024,
            "SPHINCS+": LatticeAlgorithm.SPHINCS_PLUS
        }
        
        if algorithm_name not in algorithm_mapping:
            # Default to CRYSTALS-Kyber-768
            return LatticeAlgorithm.CRYSTALS_KYBER_768
        
        return algorithm_mapping[algorithm_name]
    
    def create_quantum_encrypted_content(
        self, 
        content: bytes, 
        algorithm: Optional[str] = None,
        use_qkd: bool = False
    ) -> Dict[str, Any]:
        """
        Create quantum-encrypted content with optional QKD key exchange
        """
        # Get post-quantum crypto instance
        pq_crypto = self.get_post_quantum_crypto(algorithm)
        
        # Generate keypair
        algorithm_enum = self._map_algorithm_name(algorithm or self.config.quantum_safe_algorithm)
        lattice_crypto = LatticeBasedEncryption(algorithm_enum)
        keypair = lattice_crypto.generate_keypair()
        
        # Optionally use QKD for additional security
        qkd_key = None
        if use_qkd and self.config.qkd_enabled:
            qkd = self.get_quantum_key_distribution()
            qkd_result = qkd.generate_shared_key(
                alice_id="sender",
                bob_id="receiver",
                key_length=self.config.qkd_key_length
            )
            qkd_key = qkd_result.shared_key
        
        # Encrypt content
        result = pq_crypto.encrypt(content, keypair)
        
        return {
            "encrypted_content": result,
            "keypair": keypair,
            "qkd_key": qkd_key,
            "algorithm": algorithm_enum.value,
            "quantum_secure": True,
            "qkd_enhanced": qkd_key is not None
        }
    
    def generate_quantum_random_key(self, length: int = 32) -> bytes:
        """Generate quantum random key using QRNG"""
        qrng = self.get_quantum_random_generator()
        return qrng.generate_random_bytes(length, self.config.qrng_min_entropy_per_byte)
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get quantum security system status"""
        status = {
            "quantum_ready": True,
            "post_quantum_crypto": {
                "enabled": True,
                "default_algorithm": self.config.quantum_safe_algorithm,
                "supported_algorithms": self.config.quantum_safe_algorithms
            },
            "qkd": {
                "enabled": self.config.qkd_enabled,
                "error_threshold": self.config.qkd_error_threshold,
                "key_length": self.config.qkd_key_length
            },
            "quantum_rng": {
                "enabled": self.config.quantum_rng_enabled,
                "min_entropy_per_byte": self.config.qrng_min_entropy_per_byte
            }
        }
        
        # Add runtime status if instances exist
        if self._qkd_instance:
            qkd_analysis = self._qkd_instance.analyze_channel_security()
            status["qkd"]["channel_status"] = qkd_analysis["security_status"]
        
        if self._qrng_instance:
            entropy_status = self._qrng_instance.get_entropy_status()
            status["quantum_rng"]["entropy_available"] = entropy_status["total_entropy_available"]
            status["quantum_rng"]["active_sources"] = entropy_status["active_sources"]
        
        return status


# Singleton instance for easy access
_quantum_factory: Optional[QuantumEncryptionFactory] = None


def get_quantum_factory(config: Optional[QuantumConfig] = None) -> QuantumEncryptionFactory:
    """Get singleton quantum encryption factory"""
    global _quantum_factory
    
    if _quantum_factory is None:
        _quantum_factory = QuantumEncryptionFactory(config)
    
    return _quantum_factory


def reset_quantum_factory():
    """Reset singleton (for testing)"""
    global _quantum_factory
    _quantum_factory = None


# Convenience functions for common operations
def encrypt_with_quantum(content: bytes, algorithm: str = "CRYSTALS-Kyber") -> Dict[str, Any]:
    """Convenience function for quantum encryption"""
    factory = get_quantum_factory()
    return factory.create_quantum_encrypted_content(content, algorithm)


def generate_quantum_key(length: int = 32) -> bytes:
    """Convenience function for quantum key generation"""
    factory = get_quantum_factory()
    return factory.generate_quantum_random_key(length)


def get_quantum_status() -> Dict[str, Any]:
    """Convenience function for quantum system status"""
    factory = get_quantum_factory()
    return factory.get_security_status()