"""Backend Edge Computing Services
Edge computing modules for local inference and 5G MEC integration

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .local_inference import LocalInferenceEngine, ModelType, InferenceBackend

# Import from 5g_mec.py using a valid Python import name
import importlib
_mec_module = importlib.import_module('backend.edge.5g_mec')
MECOrchestrator = _mec_module.MECOrchestrator
EdgeNode = _mec_module.EdgeNode
ServiceType = _mec_module.ServiceType

__all__ = [
    "LocalInferenceEngine",
    "ModelType", 
    "InferenceBackend",
    "MECOrchestrator",
    "EdgeNode",
    "ServiceType"
]