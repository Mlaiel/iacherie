"""AI Processing Deployment Module for IA Influencer Agent Platform
================================================================

Enterprise-grade AI processing deployment infrastructure for multi-format content
protection, fingerprinting, and monetization system.

Core Components:
- AI Fingerprinting Engine (audio, video, image, text)
- Vector Database Management (FAISS)
- Content Protection Pipeline
- Real-time Processing Orchestration
- Scalable AI Model Deployment

Author: Fahed Mlaiel <mlaiel@live.de>
Team Specialization: Lead Dev IA + Backend Senior + ML Engineer + DBA + 
                    Security + Microservices + Audio + DevOps + IA Prompt Engineer

⚠️  WARNING: PROPRIETARY CODE
All code, concepts, and implementations in this module are proprietary 
intellectual property of Fahed Mlaiel. Any unauthorized use, copying, 
distribution, or commercial exploitation without explicit written 
permission is strictly prohibited and will result in legal action.

Contact: mlaiel@live.de for licensing inquiries.
"""from .core import AIProcessingDeployment
from .orchestrator import ProcessingOrchestrator
from .pipeline import ProcessingPipeline
from .scheduler import AIProcessingScheduler
from .manager import DeploymentManager

__version__ = "2.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"

__all__ = [
    "AIProcessingDeployment",
    "ProcessingOrchestrator", 
    "ProcessingPipeline",
    "AIProcessingScheduler",
    "DeploymentManager"
]
