#!/usr/bin/env python3
"""
🔍 DIAGNOSTIC FREEPIK/FLATICON API
Analyse détaillée des problèmes d'authentification
"""

import os
import sys
import asyncio
import aiohttp
import logging
from pathlib import Path

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv()

async def diagnose_freepik_api():
    """Diagnostic détaillé de l'API Freepik"""
    print("🎨 DIAGNOSTIC API FREEPIK")
    print("=" * 40)
    
    api_key = os.getenv('FREEPIK_API_KEY')
    print(f"🔑 Clé API: {api_key}")
    print(f"📏 Longueur: {len(api_key)} caractères")
    print(f"🎯 Format: {'✅ Valide' if api_key.startswith('FPSX') else '❌ Invalide'}")
    
    # Test d'authentification direct
    headers = {
        'X-Freepik-API-Key': api_key,
        'Content-Type': 'application/json',
        'User-Agent': 'IA Chérie-Platform/1.0'
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test endpoint simple
            url = "https://api.freepik.com/v1/resources"
            params = {'q': 'test', 'limit': 1}
            
            async with session.get(url, headers=headers, params=params) as response:
                print(f"📡 Status Code: {response.status}")
                print(f"📋 Headers Response: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Freepik API: FONCTIONNEL")
                    return True
                elif response.status == 401:
                    error_text = await response.text()
                    print(f"❌ Freepik API: ERREUR 401")
                    print(f"📄 Réponse: {error_text}")
                    return False
                else:
                    print(f"⚠️ Freepik API: Status {response.status}")
                    return False
                    
        except Exception as e:
            print(f"💥 Erreur de connexion Freepik: {e}")
            return False

async def diagnose_flaticon_api():
    """Diagnostic détaillé de l'API Flaticon"""
    print("\n🔷 DIAGNOSTIC API FLATICON")
    print("=" * 40)
    
    api_key = os.getenv('FLATICON_API_KEY')
    print(f"🔑 Clé API: {api_key}")
    print(f"📏 Longueur: {len(api_key)} caractères")
    print(f"🎯 Format: {'✅ Valide' if api_key.startswith('FPSX') else '❌ Invalide'}")
    
    # Test différents formats d'authentification
    print("\n🧪 TEST DIFFÉRENTS FORMATS D'AUTH:")
    
    test_configs = [
        {
            'name': 'Bearer Token',
            'headers': {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'API Key Header',
            'headers': {
                'X-API-Key': api_key,
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'Flaticon Token',
            'headers': {
                'Authorization': f'Token {api_key}',
                'Content-Type': 'application/json'
            }
        },
        {
            'name': 'Query Parameter',
            'headers': {'Content-Type': 'application/json'},
            'params': {'token': api_key}
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        for config in test_configs:
            try:
                print(f"\n🔬 Test: {config['name']}")
                
                url = "https://api.flaticon.com/v3/search/icons"
                params = config.get('params', {})
                params.update({'q': 'test', 'limit': 1})
                
                async with session.get(url, headers=config['headers'], params=params) as response:
                    print(f"   📡 Status: {response.status}")
                    
                    if response.status == 200:
                        print(f"   ✅ {config['name']}: FONCTIONNE!")
                        return True
                    elif response.status == 401:
                        error_text = await response.text()
                        print(f"   ❌ {config['name']}: 401 - {error_text[:100]}...")
                    else:
                        print(f"   ⚠️ {config['name']}: Status {response.status}")
                        
            except Exception as e:
                print(f"   💥 {config['name']}: Erreur - {e}")
    
    return False

async def test_alternative_apis():
    """Test d'APIs alternatives gratuites"""
    print("\n🔄 APIS ALTERNATIVES GRATUITES")
    print("=" * 50)
    
    alternatives = [
        {
            'name': 'Pexels API',
            'url': 'https://api.pexels.com/v1/search',
            'description': 'Photos gratuites haute qualité',
            'auth_header': 'Authorization'
        },
        {
            'name': 'Pixabay API', 
            'url': 'https://pixabay.com/api/',
            'description': 'Images et icônes gratuites',
            'auth_param': 'key'
        },
        {
            'name': 'Icons8 API',
            'url': 'https://api.icons8.com/api/iconsets/v5/search',
            'description': 'Icônes gratuites',
            'auth_param': 'token'
        }
    ]
    
    for alt in alternatives:
        print(f"\n💡 {alt['name']}")
        print(f"   📝 Description: {alt['description']}")
        print(f"   🔗 URL: {alt['url']}")
        print(f"   📋 Auth: {alt.get('auth_header', alt.get('auth_param', 'N/A'))}")

async def main():
    """Diagnostic principal"""
    print("🔍 DIAGNOSTIC COMPLET FREEPIK/FLATICON")
    print("=" * 60)
    
    # Test Freepik
    freepik_ok = await diagnose_freepik_api()
    
    # Test Flaticon
    flaticon_ok = await diagnose_flaticon_api()
    
    # Suggestions d'alternatives
    await test_alternative_apis()
    
    print("\n" + "=" * 60)
    print("🏆 RÉSULTAT FINAL DU DIAGNOSTIC")
    print("=" * 60)
    
    if freepik_ok and flaticon_ok:
        print("✅ Les deux APIs fonctionnent parfaitement")
        status = "100% FONCTIONNEL"
    elif freepik_ok and not flaticon_ok:
        print("🟡 Freepik fonctionne, Flaticon a des problèmes")
        status = "50% FONCTIONNEL"
    elif not freepik_ok and flaticon_ok:
        print("🟡 Flaticon fonctionne, Freepik a des problèmes")  
        status = "50% FONCTIONNEL"
    else:
        print("❌ Les deux APIs ont des problèmes")
        status = "0% FONCTIONNEL"
    
    print(f"📊 Status réel: {status}")
    
    if not flaticon_ok:
        print("\n💡 RECOMMANDATIONS:")
        print("1. Vérifier si la clé Flaticon nécessite un plan payant")
        print("2. Essayer une nouvelle clé API depuis le tableau de bord")
        print("3. Utiliser des alternatives gratuites comme Pexels/Pixabay")
        print("4. Considérer Icons8 pour les icônes")
    
    return freepik_ok and flaticon_ok

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)