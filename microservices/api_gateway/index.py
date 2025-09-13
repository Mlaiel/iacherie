"""
🔗 API GATEWAY MODULE - POINT D'ENTRÉE
Module API Gateway enterprise avec sécurité avancée

Services disponibles:
- API Gateway Service (routage principal)
- API Management Service (gestion API)
- Gateway Authentication (OAuth2/OIDC/JWT)
- Gateway Authorization (RBAC)
- Gateway Rate Limiting (protection DDoS)
- + 11 autres services enterprise

Author: Fahed Mlaiel <mlaiel@live.de>
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any

from . import *

logger = logging.getLogger(__name__)

async def main():
    """Point d'entrée du module API Gateway"""
    print("🔗 API GATEWAY MODULE - AINFLUE ENTERPRISE")
    print("=" * 50)
    
    # Initialisation du module
    gateway_module = get_api_gateway()
    await gateway_module.initialize()
    
    # Affichage des informations
    info = gateway_module.get_services_info()
    print(f"Module: {info['module']}")
    print(f"Status: {info['status']}")
    print(f"Services Count: {info['services_count']}")
    
    print("\nCapabilities:")
    for capability in info['capabilities']:
        print(f"  ✅ {capability}")
    
    print("\n🚀 API Gateway Module ready for enterprise deployment!")

if __name__ == "__main__":
    asyncio.run(main())