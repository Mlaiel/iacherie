#!/usr/bin/env python3
"""
🔬 IA CHÉRIE - ANALYSE PROFESSIONNELLE APIs
Analyse approfondie et fiable des APIs configurées
Auteur: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any, Tuple
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IACheriAPIAnalyzer:
    """Analyseur professionnel d'APIs pour IA Chérie"""
    
    def __init__(self):
        load_dotenv()
        self.results = {}
        self.total_apis = 0
        self.working_apis = 0
        self.failed_apis = 0
        self.placeholders = 0
        
    async def analyze_all_apis(self):
        """Lance l'analyse complète de toutes les APIs"""
        logger.info("🔬 Démarrage de l'analyse professionnelle IA Chérie...")
        
        # APIs critiques à analyser
        apis_to_test = {
            'OpenAI': {
                'key': 'OPENAI_API_KEY',
                'test_func': self.test_openai
            },
            'Hugging Face': {
                'key': 'HUGGINGFACE_API_KEY', 
                'test_func': self.test_huggingface
            },
            'Google Gemini': {
                'key': 'GOOGLE_GEMINI_API_KEY',
                'test_func': self.test_gemini
            },
            'ElevenLabs': {
                'key': 'ELEVENLABS_API_KEY',
                'test_func': self.test_elevenlabs
            },
            'Freesound': {
                'key': 'FREESOUND_API_KEY',
                'test_func': self.test_freesound
            },
            'Unsplash': {
                'key': 'UNSPLASH_ACCESS_KEY',
                'test_func': self.test_unsplash
            },
            'Discord Bot': {
                'key': 'DISCORD_BOT_TOKEN',
                'test_func': self.test_discord
            },
            'Facebook/Meta': {
                'key': 'FACEBOOK_ACCESS_TOKEN',
                'test_func': self.test_facebook
            },
            'Instagram': {
                'key': 'INSTAGRAM_APP_SECRET',
                'test_func': self.test_instagram_config
            }
        }
        
        # Analyse de chaque API
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for api_name, config in apis_to_test.items():
                await self.analyze_single_api(session, api_name, config)
        
        # Analyse des placeholders
        self.analyze_placeholders()
        
        # Génération du rapport
        self.generate_report()
    
    async def analyze_single_api(self, session: aiohttp.ClientSession, api_name: str, config: Dict):
        """Analyse une API individuelle"""
        try:
            api_key = os.getenv(config['key'])
            if not api_key:
                self.results[api_name] = {
                    'status': 'missing',
                    'message': '❌ Clé API manquante',
                    'time': 0
                }
                self.failed_apis += 1
                return
            
            # Test de placeholder
            if self.is_placeholder(api_key):
                self.results[api_name] = {
                    'status': 'placeholder',
                    'message': '⚠️ Token placeholder détecté',
                    'key_preview': f"{api_key[:10]}...",
                    'time': 0
                }
                self.placeholders += 1
                return
            
            # Test fonctionnel
            start_time = time.time()
            result = await config['test_func'](session, api_key)
            test_time = round(time.time() - start_time, 2)
            
            self.results[api_name] = {
                'status': result['status'],
                'message': result['message'],
                'details': result.get('details', {}),
                'time': test_time
            }
            
            if result['status'] == 'success':
                self.working_apis += 1
            else:
                self.failed_apis += 1
                
        except Exception as e:
            self.results[api_name] = {
                'status': 'error',
                'message': f'❌ Erreur: {str(e)[:100]}',
                'time': 0
            }
            self.failed_apis += 1
        
        self.total_apis += 1
    
    def is_placeholder(self, value: str) -> bool:
        """Détecte si une valeur est un placeholder"""
        placeholders = [
            'your_', 'YOUR_', 'votre_', 'sk-proj-',
            'placeholder', 'PLACEHOLDER', 'xxxxxxxx',
            'ACxxxxxxxx', '+1xxxxxxxxxx'
        ]
        return any(placeholder in value for placeholder in placeholders)
    
    async def test_openai(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test OpenAI API"""
        headers = {'Authorization': f'Bearer {api_key}'}
        async with session.get('https://api.openai.com/v1/models', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                models = [m['id'] for m in data.get('data', [])]
                return {
                    'status': 'success',
                    'message': f'✅ {len(models)} modèles disponibles',
                    'details': {'models_count': len(models), 'sample_models': models[:3]}
                }
            else:
                error_text = await response.text()
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}: {error_text[:100]}'
                }
    
    async def test_huggingface(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Hugging Face API"""
        headers = {'Authorization': f'Bearer {api_key}'}
        async with session.get('https://huggingface.co/api/models?limit=1', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                models_count = len(data) if isinstance(data, list) else 0
                return {
                    'status': 'success',
                    'message': f'✅ {models_count} modèles accessibles',
                    'details': {'models_accessible': models_count, 'api_working': True}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_gemini(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Google Gemini API"""
        url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                models = data.get('models', [])
                return {
                    'status': 'success',
                    'message': f'✅ {len(models)} modèles Gemini',
                    'details': {'models_count': len(models)}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_elevenlabs(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test ElevenLabs API"""
        headers = {'xi-api-key': api_key}
        async with session.get('https://api.elevenlabs.io/v1/user/subscription', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': 'success',
                    'message': f'✅ Subscription: {data.get("tier", "unknown")}',
                    'details': {'tier': data.get('tier'), 'status': data.get('status')}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_freesound(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Freesound API"""
        params = {'token': api_key, 'query': 'test', 'page_size': 1}
        async with session.get('https://freesound.org/apiv2/search/text/', params=params) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': 'success',
                    'message': f'✅ {data.get("count", 0)} sons disponibles',
                    'details': {'total_sounds': data.get('count')}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_unsplash(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Unsplash API"""
        headers = {'Authorization': f'Client-ID {api_key}'}
        async with session.get('https://api.unsplash.com/photos/random?count=1', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                photo_id = data[0].get('id') if isinstance(data, list) and data else 'unknown'
                return {
                    'status': 'success',
                    'message': f'✅ Photo obtenue: {photo_id}',
                    'details': {'photo_id': photo_id}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_discord(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Discord Bot API"""
        headers = {'Authorization': f'Bot {api_key}'}
        async with session.get('https://discord.com/api/v10/applications/@me', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': 'success',
                    'message': f'✅ Bot: {data.get("name", "Unknown")}',
                    'details': {'bot_name': data.get('name'), 'id': data.get('id')}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_facebook(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test Facebook/Meta API"""
        params = {'access_token': api_key}
        async with session.get('https://graph.facebook.com/me', params=params) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': 'success',
                    'message': f'✅ Utilisateur: {data.get("name", "Unknown")}',
                    'details': {'user': data.get('name'), 'id': data.get('id')}
                }
            else:
                return {
                    'status': 'error',
                    'message': f'❌ HTTP {response.status}'
                }
    
    async def test_instagram_config(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        """Test configuration Instagram"""
        app_id = os.getenv('INSTAGRAM_APP_ID')
        if app_id and api_key and not self.is_placeholder(app_id):
            return {
                'status': 'success',
                'message': f'✅ App configurée: {app_id}',
                'details': {'app_id': app_id, 'secret_configured': True}
            }
        else:
            return {
                'status': 'error',
                'message': '❌ Configuration incomplète'
            }
    
    def analyze_placeholders(self):
        """Analyse les tokens placeholder restants"""
        placeholder_vars = [
            'TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER',
            'STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY',
            'YOUTUBE_API_KEY', 'SPOTIFY_CLIENT_SECRET'
        ]
        
        for var in placeholder_vars:
            value = os.getenv(var)
            if value and self.is_placeholder(value):
                self.placeholders += 1
    
    def generate_report(self):
        """Génère le rapport final"""
        success_rate = round((self.working_apis / max(self.total_apis, 1)) * 100, 1)
        
        print("\n" + "="*70)
        print("🔬 IA CHÉRIE - ANALYSE PROFESSIONNELLE APIs")
        print("="*70)
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print(f"🏆 Score global: {success_rate}% ({self.working_apis}/{self.total_apis})")
        print(f"✅ APIs fonctionnelles: {self.working_apis}")
        print(f"❌ APIs en erreur: {self.failed_apis}")
        print(f"⚠️ Placeholders détectés: {self.placeholders}")
        
        print(f"\n🧪 DÉTAILS DES TESTS:")
        for api_name, result in self.results.items():
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⚠️"
            print(f"   {status_icon} {api_name:15} {result['message']:50} ({result['time']}s)")
        
        # Sauvegarde JSON
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_apis': self.total_apis,
                'working_apis': self.working_apis,
                'failed_apis': self.failed_apis,
                'placeholders': self.placeholders,
                'success_rate': success_rate
            },
            'results': self.results
        }
        
        with open('ia_cherie_api_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Rapport sauvegardé: ia_cherie_api_analysis.json")
        print("✅ Analyse terminée!")

async def main():
    """Fonction principale"""
    analyzer = IACheriAPIAnalyzer()
    await analyzer.analyze_all_apis()

if __name__ == "__main__":
    asyncio.run(main())