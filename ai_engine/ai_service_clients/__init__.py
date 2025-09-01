#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IA-Influencer-Agent AI Service Clients
================================================================================
Module: ai_engine/ai_service_clients/__init__.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise AI Service Integration (Level 1)
Created: 2025-01-01
Team: Lead Dev IA + Backend Senior + ML Engineer
================================================================================

⚠️  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL ⚠️
(c) 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Intégration des services IA externes pour génération de contenu
TECHNOLOGIES: OpenAI, DALL-E, Midjourney, Stable Diffusion, WaveNet, MuseNet, AIVA
"""

from .openai_client import OpenAIClient
from .dalle_client import DALLEClient  
from .midjourney_client import MidjourneyClient
from .stable_diffusion_client import StableDiffusionClient
from .wavenet_client import WaveNetClient
from .musenet_client import MuseNetClient
from .aiva_client import AIVAClient

__all__ = [
    "OpenAIClient",
    "DALLEClient", 
    "MidjourneyClient",
    "StableDiffusionClient",
    "WaveNetClient",
    "MuseNetClient",
    "AIVAClient"
]

__version__ = "1.0.0"
__author__ = "Fahed Mlaiel"
__email__ = "mlaiel@live.de"
__copyright__ = "(c) 2025 Fahed Mlaiel. All rights reserved."