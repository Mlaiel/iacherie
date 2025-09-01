"""
Ainflue MLOps Module
Complete MLOps pipeline implementation with advanced features

Components:
- Model Versioning & Registry (MLflow-based)
- A/B Testing for AI Models with Business Metrics
- Model Performance Monitoring & Drift Detection  
- Automated Retraining with Intelligent Triggers
- Model Explainability for Compliance & Debugging
- Model Governance with Approval Workflows
- High-Performance Model Serving with Auto-Scaling
- Centralized Feature Store with Versioning

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

from .platform_orchestrator import MLOpsPlatform, MLOpsConfig, create_mlops_platform

__version__ = "1.0.0"
__all__ = ["MLOpsPlatform", "MLOpsConfig", "create_mlops_platform"]