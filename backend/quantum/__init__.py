"""
Quantum-Ready Encryption Module for Ainflue Platform

This module provides quantum-resistant cryptographic implementations
to protect against future quantum computer attacks. It includes:

- Post-quantum cryptography (lattice-based encryption)
- Quantum key distribution protocols
- True quantum random number generation
- Integration factory for existing systems

Author: Fahed Mlaiel <mlaiel@live.de>
Team: Lead Dev IA + Backend + Security Experts

⚠️ COPYRIGHT WARNING:
This code is proprietary and belongs to Fahed Mlaiel.
Any unauthorized use, copying, or distribution without explicit 
written permission from Fahed Mlaiel is strictly prohibited.
Contact: mlaiel@live.de for licensing inquiries.
"""

from .post_quantum_crypto import PostQuantumCrypto, LatticeBasedEncryption, LatticeAlgorithm
from .quantum_key_distribution import QuantumKeyDistribution, QKDProtocol
from .quantum_random_generator import QuantumRandomGenerator, TrueRandomSource
from .quantum_factory import (
    QuantumEncryptionFactory, 
    QuantumConfig,
    get_quantum_factory,
    encrypt_with_quantum,
    generate_quantum_key,
    get_quantum_status
)

# Quantum Business Logic Components
from .quantum_business_logic_orchestrator import (
    QuantumBusinessLogicOrchestrator,
    QuantumProcessingRequest,
    QuantumProcessingResult,
    QuantumBusinessStage,
    QuantumAlgorithmType,
    get_quantum_orchestrator,
    process_creator_quantum_enhancement,
    get_quantum_business_status
)
from .quantum_business_enhancement_layer import (
    QuantumBusinessEnhancementLayer,
    QuantumEnhancementRequest,
    QuantumEnhancementResult,
    QuantumEnhancementType,
    BusinessProcessType,
    get_quantum_enhancement_layer,
    enhance_content_processing,
    enhance_ai_analysis
)
from .classical_quantum_hybrid_layer import (
    ClassicalQuantumHybridLayer,
    HybridProcessingRequest,
    HybridProcessingResult,
    ProcessingMode,
    WorkloadType,
    get_hybrid_layer,
    process_optimization_hybrid,
    process_ml_hybrid
)
from .creator_quantum_enhancement_engine import (
    CreatorQuantumEnhancementEngine,
    CreatorQuantumRequest,
    CreatorQuantumResult,
    CreatorType,
    ContentFormat,
    QuantumEnhancementLevel,
    get_creator_enhancement_engine,
    enhance_musician_content,
    enhance_blogger_content
)

__all__ = [
    # Quantum Cryptography Components
    "PostQuantumCrypto",
    "LatticeBasedEncryption", 
    "LatticeAlgorithm",
    "QuantumKeyDistribution",
    "QKDProtocol",
    "QuantumRandomGenerator",
    "TrueRandomSource",
    "QuantumEncryptionFactory",
    "QuantumConfig",
    "get_quantum_factory",
    "encrypt_with_quantum",
    "generate_quantum_key",
    "get_quantum_status",
    
    # Quantum Business Logic Components
    "QuantumBusinessLogicOrchestrator",
    "QuantumProcessingRequest",
    "QuantumProcessingResult",
    "QuantumBusinessStage",
    "QuantumAlgorithmType",
    "get_quantum_orchestrator",
    "process_creator_quantum_enhancement",
    "get_quantum_business_status",
    
    # Quantum Enhancement Layer
    "QuantumBusinessEnhancementLayer",
    "QuantumEnhancementRequest",
    "QuantumEnhancementResult",
    "QuantumEnhancementType",
    "BusinessProcessType",
    "get_quantum_enhancement_layer",
    "enhance_content_processing",
    "enhance_ai_analysis",
    
    # Classical-Quantum Hybrid Layer
    "ClassicalQuantumHybridLayer",
    "HybridProcessingRequest",
    "HybridProcessingResult",
    "ProcessingMode",
    "WorkloadType",
    "get_hybrid_layer",
    "process_optimization_hybrid",
    "process_ml_hybrid",
    
    # Creator Quantum Enhancement
    "CreatorQuantumEnhancementEngine",
    "CreatorQuantumRequest",
    "CreatorQuantumResult",
    "CreatorType",
    "ContentFormat",
    "QuantumEnhancementLevel",
    "get_creator_enhancement_engine",
    "enhance_musician_content",
    "enhance_blogger_content"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"