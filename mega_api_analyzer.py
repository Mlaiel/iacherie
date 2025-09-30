#!/usr/bin/env python3
"""
🔬 IA CHÉRIE - ANALYSEUR COMPLET TOUTES APIs
Scanner automatique de TOUTES les APIs configurées
Auteur: Fahed Mlaiel (mlaiel@live.de)
"""

import asyncio
import aiohttp
import json
import time
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any, Tuple
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IACherieMegaAPIAnalyzer:
    """Analyseur MEGA complet de TOUTES les APIs IA Chérie"""
    
    def __init__(self):
        load_dotenv()
        self.results = {}
        self.api_categories = {
            'AI_ML': [],
            'SOCIAL_MEDIA': [],
            'PAYMENTS': [],
            'STORAGE_CDN': [],
            'COMMUNICATION': [],
            'MEDIA_PROCESSING': [],
            'ANALYTICS': [],
            'DEVELOPMENT': [],
            'OTHERS': []
        }
        
    def scan_all_apis(self):
        """Scanne automatiquement TOUTES les APIs du .env"""
        logger.info("🔍 Scanning TOUTES les APIs dans .env...")
        
        # Patterns pour identifier les APIs
        api_patterns = [
            r'.*_API_KEY$',
            r'.*_TOKEN$', 
            r'.*_SECRET$',
            r'.*_ACCESS_KEY$',
            r'.*_CLIENT_ID$',
            r'.*_APP_ID$',
            r'.*_WEBHOOK$',
            r'.*_ENDPOINT$'
        ]
        
        all_apis = {}
        
        # Scanner toutes les variables d'environnement
        for key, value in os.environ.items():
            if any(re.match(pattern, key) for pattern in api_patterns):
                if value and not self.is_placeholder(value):
                    category = self.categorize_api(key)
                    all_apis[key] = {
                        'value': value,
                        'category': category,
                        'preview': f"{value[:15]}..." if len(value) > 15 else value
                    }
        
        return all_apis
    
    def categorize_api(self, api_name: str) -> str:
        """Catégorise automatiquement les APIs"""
        name_lower = api_name.lower()
        
        # AI/ML
        if any(term in name_lower for term in ['openai', 'huggingface', 'gemini', 'anthropic', 'cohere', 'elevenlabs', 'replicate']):
            return 'AI_ML'
        
        # Social Media
        if any(term in name_lower for term in ['facebook', 'instagram', 'twitter', 'discord', 'youtube', 'tiktok', 'linkedin', 'pinterest']):
            return 'SOCIAL_MEDIA'
        
        # Payments
        if any(term in name_lower for term in ['stripe', 'paypal', 'wise', 'crypto', 'blockchain']):
            return 'PAYMENTS'
        
        # Storage/CDN
        if any(term in name_lower for term in ['aws', 'google_cloud', 'azure', 'cloudinary', 'firebase']):
            return 'STORAGE_CDN'
        
        # Communication
        if any(term in name_lower for term in ['twilio', 'email', 'sms', 'sendgrid', 'mailgun']):
            return 'COMMUNICATION'
        
        # Media Processing
        if any(term in name_lower for term in ['unsplash', 'freesound', 'pexels', 'shutterstock', 'runway']):
            return 'MEDIA_PROCESSING'
        
        # Analytics
        if any(term in name_lower for term in ['google_analytics', 'mixpanel', 'amplitude', 'segment']):
            return 'ANALYTICS'
        
        # Development
        if any(term in name_lower for term in ['github', 'gitlab', 'vercel', 'netlify']):
            return 'DEVELOPMENT'
        
        return 'OTHERS'
    
    def is_placeholder(self, value: str) -> bool:
        """Détecte si une valeur est un placeholder"""
        placeholders = [
            'your_', 'YOUR_', 'votre_', 'sk-proj-',
            'placeholder', 'PLACEHOLDER', 'xxxxxxxx',
            'ACxxxxxxxx', '+1xxxxxxxxxx', 'todo', 'TODO'
        ]
        return any(placeholder in value for placeholder in placeholders)
    
    async def test_critical_apis(self, session: aiohttp.ClientSession, all_apis: Dict):
        """Test les APIs critiques avec des endpoints réels"""
        
        critical_tests = {
            'OPENAI_API_KEY': self.test_openai,
            'HUGGINGFACE_API_KEY': self.test_huggingface,
            'GOOGLE_GEMINI_API_KEY': self.test_gemini,
            'ELEVENLABS_API_KEY': self.test_elevenlabs,
            'FREESOUND_API_KEY': self.test_freesound,
            'UNSPLASH_ACCESS_KEY': self.test_unsplash,
            'DISCORD_BOT_TOKEN': self.test_discord,
            'FACEBOOK_ACCESS_TOKEN': self.test_facebook,
            'STRIPE_SECRET_KEY': self.test_stripe,
            'AWS_ACCESS_KEY_ID': self.test_aws
        }
        
        tested_apis = {}
        
        for api_key, test_func in critical_tests.items():
            if api_key in all_apis:
                try:
                    start_time = time.time()
                    result = await test_func(session, all_apis[api_key]['value'])
                    test_time = round(time.time() - start_time, 2)
                    
                    tested_apis[api_key] = {
                        **result,
                        'time': test_time,
                        'category': all_apis[api_key]['category']
                    }
                except Exception as e:
                    tested_apis[api_key] = {
                        'status': 'error',
                        'message': f'❌ Erreur test: {str(e)[:50]}',
                        'time': 0,
                        'category': all_apis[api_key]['category']
                    }
        
        return tested_apis
    
    # Fonctions de test (reprises de l'analyseur précédent)
    async def test_openai(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        headers = {'Authorization': f'Bearer {api_key}'}
        async with session.get('https://api.openai.com/v1/models', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                models = [m['id'] for m in data.get('data', [])]
                return {'status': 'success', 'message': f'✅ {len(models)} modèles OpenAI'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_huggingface(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        headers = {'Authorization': f'Bearer {api_key}'}
        async with session.get('https://huggingface.co/api/models?limit=1', headers=headers) as response:
            if response.status == 200:
                return {'status': 'success', 'message': '✅ Hugging Face accessible'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_gemini(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        url = f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}'
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {'status': 'success', 'message': f'✅ {len(data.get("models", []))} modèles Gemini'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_elevenlabs(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        headers = {'xi-api-key': api_key}
        async with session.get('https://api.elevenlabs.io/v1/user/subscription', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {'status': 'success', 'message': f'✅ ElevenLabs {data.get("tier", "active")}'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_freesound(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        params = {'token': api_key, 'query': 'test', 'page_size': 1}
        async with session.get('https://freesound.org/apiv2/search/text/', params=params) as response:
            if response.status == 200:
                data = await response.json()
                return {'status': 'success', 'message': f'✅ {data.get("count", 0)} sons Freesound'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_unsplash(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        headers = {'Authorization': f'Client-ID {api_key}'}
        async with session.get('https://api.unsplash.com/photos/random?count=1', headers=headers) as response:
            if response.status == 200:
                return {'status': 'success', 'message': '✅ Photos Unsplash OK'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_discord(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        headers = {'Authorization': f'Bot {api_key}'}
        async with session.get('https://discord.com/api/v10/applications/@me', headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                return {'status': 'success', 'message': f'✅ Bot Discord: {data.get("name", "OK")}'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_facebook(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        params = {'access_token': api_key}
        async with session.get('https://graph.facebook.com/me', params=params) as response:
            if response.status == 200:
                data = await response.json()
                return {'status': 'success', 'message': f'✅ Facebook: {data.get("name", "OK")}'}
            return {'status': 'error', 'message': f'❌ HTTP {response.status}'}
    
    async def test_stripe(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        # Stripe nécessite une approche différente
        return {'status': 'configured', 'message': '⚙️ Stripe configuré (non testé)'}
    
    async def test_aws(self, session: aiohttp.ClientSession, api_key: str) -> Dict:
        # AWS nécessite une approche différente  
        return {'status': 'configured', 'message': '⚙️ AWS configuré (non testé)'}
    
    async def analyze_all(self):
        """Lance l'analyse MEGA complète"""
        logger.info("🔬 Démarrage de l'analyse MEGA IA Chérie...")
        
        # 1. Scanner toutes les APIs
        all_apis = self.scan_all_apis()
        
        # 2. Catégoriser
        for api_name, api_info in all_apis.items():
            category = api_info['category']
            self.api_categories[category].append({
                'name': api_name,
                'preview': api_info['preview']
            })
        
        # 3. Tester les APIs critiques
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            tested_apis = await self.test_critical_apis(session, all_apis)
        
        # 4. Générer le rapport MEGA
        self.generate_mega_report(all_apis, tested_apis)
    
    def generate_mega_report(self, all_apis: Dict, tested_apis: Dict):
        """Génère le rapport MEGA complet"""
        
        total_apis = len(all_apis)
        tested_count = len(tested_apis)
        working_apis = sum(1 for api in tested_apis.values() if api['status'] == 'success')
        
        print("\n" + "="*80)
        print("🔬 IA CHÉRIE - ANALYSE MEGA COMPLÈTE")
        print("="*80)
        print(f"📅 Timestamp: {datetime.now().isoformat()}")
        print(f"🏆 APIs totales détectées: {total_apis}")
        print(f"🧪 APIs testées: {tested_count}")
        print(f"✅ APIs fonctionnelles: {working_apis}")
        print(f"📊 Taux de succès des tests: {round((working_apis/max(tested_count, 1))*100, 1)}%")
        
        # Rapport par catégorie
        print(f"\n📋 RÉPARTITION PAR CATÉGORIE:")
        for category, apis in self.api_categories.items():
            if apis:
                print(f"   📁 {category:20} {len(apis):3} APIs")
        
        # Détails des tests
        print(f"\n🧪 RÉSULTATS DES TESTS CRITIQUES:")
        for api_name, result in tested_apis.items():
            status_icon = "✅" if result['status'] == 'success' else "❌" if result['status'] == 'error' else "⚙️"
            print(f"   {status_icon} {api_name:25} {result['message']:40} ({result['time']}s)")
        
        # APIs non testées mais configurées
        non_tested = set(all_apis.keys()) - set(tested_apis.keys())
        if non_tested:
            print(f"\n⚙️ APIS CONFIGURÉES (non testées): {len(non_tested)}")
            for api_name in sorted(non_tested):
                category = all_apis[api_name]['category']
                preview = all_apis[api_name]['preview']
                print(f"   📝 {api_name:25} {category:15} {preview}")
        
        # Sauvegarde
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_apis': total_apis,
                'tested_apis': tested_count,
                'working_apis': working_apis,
                'categories': {cat: len(apis) for cat, apis in self.api_categories.items() if apis}
            },
            'tested_results': tested_apis,
            'all_apis_by_category': self.api_categories
        }
        
        with open('ia_cherie_mega_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Rapport MEGA sauvegardé: ia_cherie_mega_analysis.json")
        print("✅ Analyse MEGA terminée!")

async def main():
    """Fonction principale"""
    analyzer = IACherieMegaAPIAnalyzer()
    await analyzer.analyze_all()

if __name__ == "__main__":
    asyncio.run(main())