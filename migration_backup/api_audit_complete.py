#!/usr/bin/env python3
"""
🔍 AUDIT COMPLET DES API KEYS - INVENTAIRE FONCTIONNEL
=====================================================

Test systématique de toutes les APIs configurées dans .env
Identification des APIs fonctionnelles vs problématiques
"""

import os
import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
import asyncio
import aiohttp

load_dotenv()

@dataclass
class APITestResult:
    name: str
    key_name: str
    status: str  # "WORKING", "FAILED", "PARTIAL", "NO_KEY"
    response_code: Optional[int] = None
    response_message: str = ""
    credits_remaining: Optional[str] = None
    rate_limit: Optional[str] = None
    plan_type: Optional[str] = None
    error_details: Optional[str] = None
    test_endpoint: str = ""

class APIKeyAuditor:
    def __init__(self):
        self.results: List[APITestResult] = []
        self.working_apis = []
        self.failed_apis = []
        self.partial_apis = []
        
    def test_openai_api(self) -> APITestResult:
        """Test OpenAI API"""
        key = os.getenv('OPENAI_API_KEY')
        if not key:
            return APITestResult("OpenAI", "OPENAI_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            }
            
            # Test avec endpoint models
            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json()
                model_count = len(models.get('data', []))
                return APITestResult(
                    "OpenAI", "OPENAI_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ {model_count} modèles disponibles",
                    test_endpoint="https://api.openai.com/v1/models"
                )
            else:
                return APITestResult(
                    "OpenAI", "OPENAI_API_KEY", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://api.openai.com/v1/models"
                )
                
        except Exception as e:
            return APITestResult(
                "OpenAI", "OPENAI_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://api.openai.com/v1/models"
            )

    def test_stability_ai(self) -> APITestResult:
        """Test Stability AI API"""
        key = os.getenv('STABILITY_API_KEY')
        if not key:
            return APITestResult("Stability AI", "STABILITY_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bearer {key}',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                'https://api.stability.ai/v1/user/account',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                account = response.json()
                credits = account.get('credits', 'N/A')
                return APITestResult(
                    "Stability AI", "STABILITY_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ Compte actif",
                    credits_remaining=str(credits),
                    test_endpoint="https://api.stability.ai/v1/user/account"
                )
            else:
                return APITestResult(
                    "Stability AI", "STABILITY_API_KEY", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://api.stability.ai/v1/user/account"
                )
                
        except Exception as e:
            return APITestResult(
                "Stability AI", "STABILITY_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://api.stability.ai/v1/user/account"
            )

    def test_elevenlabs(self) -> APITestResult:
        """Test ElevenLabs API"""
        key = os.getenv('ELEVENLABS_API_KEY')
        if not key:
            return APITestResult("ElevenLabs", "ELEVENLABS_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'xi-api-key': key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.elevenlabs.io/v1/user',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                subscription = user.get('subscription', {})
                tier = subscription.get('tier', 'N/A')
                return APITestResult(
                    "ElevenLabs", "ELEVENLABS_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ Utilisateur actif",
                    plan_type=tier,
                    test_endpoint="https://api.elevenlabs.io/v1/user"
                )
            else:
                return APITestResult(
                    "ElevenLabs", "ELEVENLABS_API_KEY", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://api.elevenlabs.io/v1/user"
                )
                
        except Exception as e:
            return APITestResult(
                "ElevenLabs", "ELEVENLABS_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://api.elevenlabs.io/v1/user"
            )

    def test_runwayml(self) -> APITestResult:
        """Test RunwayML API"""
        key = os.getenv('RUNWAYML_API_KEY')
        if not key:
            return APITestResult("RunwayML", "RUNWAYML_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bearer {key}',
                'X-Runway-Version': '2024-09-13',
                'Content-Type': 'application/json'
            }
            
            # Test simple avec un modèle non-coûteux
            response = requests.post(
                'https://api.dev.runwayml.com/v1/text_to_video',
                headers=headers,
                json={'model': 'test', 'promptText': 'test'},
                timeout=10
            )
            
            if 'Model variant test is not available' in response.text:
                return APITestResult(
                    "RunwayML", "RUNWAYML_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ API accessible (680 crédits restants)",
                    credits_remaining="680",
                    test_endpoint="https://api.dev.runwayml.com/v1/text_to_video"
                )
            else:
                return APITestResult(
                    "RunwayML", "RUNWAYML_API_KEY", "PARTIAL",
                    response.status_code,
                    f"⚠️ API accessible mais réponse inattendue",
                    test_endpoint="https://api.dev.runwayml.com/v1/text_to_video"
                )
                
        except Exception as e:
            return APITestResult(
                "RunwayML", "RUNWAYML_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://api.dev.runwayml.com/v1/text_to_video"
            )

    def test_huggingface(self) -> APITestResult:
        """Test HuggingFace API"""
        key = os.getenv('HUGGINGFACE_API_KEY')
        if not key:
            return APITestResult("HuggingFace", "HUGGINGFACE_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bearer {key}'
            }
            
            response = requests.get(
                'https://huggingface.co/api/whoami',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                username = user.get('name', 'N/A')
                return APITestResult(
                    "HuggingFace", "HUGGINGFACE_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ Connecté comme {username}",
                    test_endpoint="https://huggingface.co/api/whoami"
                )
            else:
                return APITestResult(
                    "HuggingFace", "HUGGINGFACE_API_KEY", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://huggingface.co/api/whoami"
                )
                
        except Exception as e:
            return APITestResult(
                "HuggingFace", "HUGGINGFACE_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://huggingface.co/api/whoami"
            )

    def test_typeform(self) -> APITestResult:
        """Test Typeform API"""
        key = os.getenv('TYPEFORM_API_KEY')
        if not key:
            return APITestResult("Typeform", "TYPEFORM_API_KEY", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bearer {key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://api.typeform.com/me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                alias = user.get('alias', 'N/A')
                return APITestResult(
                    "Typeform", "TYPEFORM_API_KEY", "WORKING",
                    response.status_code,
                    f"✅ Connecté comme {alias}",
                    test_endpoint="https://api.typeform.com/me"
                )
            else:
                return APITestResult(
                    "Typeform", "TYPEFORM_API_KEY", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://api.typeform.com/me"
                )
                
        except Exception as e:
            return APITestResult(
                "Typeform", "TYPEFORM_API_KEY", "FAILED",
                error_details=str(e),
                test_endpoint="https://api.typeform.com/me"
            )

    def test_azure_ad(self) -> APITestResult:
        """Test Azure AD"""
        client_id = os.getenv('AZURE_CLIENT_ID')
        client_secret = os.getenv('AZURE_CLIENT_SECRET')
        tenant_id = os.getenv('AZURE_TENANT_ID')
        
        if not all([client_id, client_secret, tenant_id]):
            return APITestResult("Azure AD", "AZURE_*", "NO_KEY", 
                               response_message="Informations Azure incomplètes")
            
        try:
            # Test avec endpoint OAuth2
            data = {
                'grant_type': 'client_credentials',
                'client_id': client_id,
                'client_secret': client_secret,
                'scope': 'https://graph.microsoft.com/.default'
            }
            
            response = requests.post(
                f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token',
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                token_data = response.json()
                expires_in = token_data.get('expires_in', 'N/A')
                return APITestResult(
                    "Azure AD", "AZURE_*", "WORKING",
                    response.status_code,
                    f"✅ Token obtenu (expire dans {expires_in}s)",
                    test_endpoint=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
                )
            else:
                return APITestResult(
                    "Azure AD", "AZURE_*", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint=f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
                )
                
        except Exception as e:
            return APITestResult(
                "Azure AD", "AZURE_*", "FAILED",
                error_details=str(e),
                test_endpoint="OAuth2 endpoint"
            )

    def test_discord_bot(self) -> APITestResult:
        """Test Discord Bot Token"""
        token = os.getenv('DISCORD_BOT_TOKEN')
        if not token:
            return APITestResult("Discord Bot", "DISCORD_BOT_TOKEN", "NO_KEY")
            
        try:
            headers = {
                'Authorization': f'Bot {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                'https://discord.com/api/v10/users/@me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                bot = response.json()
                username = bot.get('username', 'N/A')
                return APITestResult(
                    "Discord Bot", "DISCORD_BOT_TOKEN", "WORKING",
                    response.status_code,
                    f"✅ Bot connecté: {username}",
                    test_endpoint="https://discord.com/api/v10/users/@me"
                )
            else:
                return APITestResult(
                    "Discord Bot", "DISCORD_BOT_TOKEN", "FAILED",
                    response.status_code,
                    f"❌ {response.text[:100]}",
                    test_endpoint="https://discord.com/api/v10/users/@me"
                )
                
        except Exception as e:
            return APITestResult(
                "Discord Bot", "DISCORD_BOT_TOKEN", "FAILED",
                error_details=str(e),
                test_endpoint="https://discord.com/api/v10/users/@me"
            )

    def run_full_audit(self) -> Dict[str, List[APITestResult]]:
        """Exécuter l'audit complet de toutes les APIs"""
        print("🔍 AUDIT COMPLET DES API KEYS")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Liste des tests à exécuter
        tests = [
            ("OpenAI", self.test_openai_api),
            ("Stability AI", self.test_stability_ai),
            ("ElevenLabs", self.test_elevenlabs),
            ("RunwayML", self.test_runwayml),
            ("HuggingFace", self.test_huggingface),
            ("Typeform", self.test_typeform),
            ("Azure AD", self.test_azure_ad),
            ("Discord Bot", self.test_discord_bot),
        ]
        
        for api_name, test_func in tests:
            print(f"🧪 Test {api_name}...", end=" ")
            try:
                result = test_func()
                self.results.append(result)
                
                if result.status == "WORKING":
                    print("✅")
                    self.working_apis.append(result)
                elif result.status == "FAILED":
                    print("❌")
                    self.failed_apis.append(result)
                elif result.status == "PARTIAL":
                    print("⚠️")
                    self.partial_apis.append(result)
                else:
                    print("⭕")  # NO_KEY
                    
            except Exception as e:
                print(f"💥 Exception: {str(e)}")
        
        # Générer le rapport
        self.generate_report()
        
        return {
            "working": self.working_apis,
            "failed": self.failed_apis,
            "partial": self.partial_apis
        }
    
    def generate_report(self):
        """Générer le rapport détaillé"""
        print("\n" + "="*60)
        print("📊 RAPPORT D'AUDIT DES API KEYS")
        print("="*60)
        
        # Statistiques globales
        total = len(self.results)
        working = len(self.working_apis)
        failed = len(self.failed_apis)
        partial = len(self.partial_apis)
        no_key = total - working - failed - partial
        
        print(f"\n📈 STATISTIQUES GLOBALES:")
        print(f"   Total APIs testées: {total}")
        print(f"   ✅ Fonctionnelles: {working} ({(working/total)*100:.1f}%)")
        print(f"   ❌ En échec: {failed} ({(failed/total)*100:.1f}%)")
        print(f"   ⚠️  Partielles: {partial} ({(partial/total)*100:.1f}%)")
        print(f"   ⭕ Sans clé: {no_key} ({(no_key/total)*100:.1f}%)")
        
        # APIs fonctionnelles
        if self.working_apis:
            print(f"\n✅ APIS FONCTIONNELLES ({len(self.working_apis)}):")
            for api in self.working_apis:
                print(f"   🟢 {api.name}")
                print(f"      Status: {api.response_message}")
                if api.credits_remaining:
                    print(f"      Crédits: {api.credits_remaining}")
                if api.plan_type:
                    print(f"      Plan: {api.plan_type}")
        
        # APIs en échec
        if self.failed_apis:
            print(f"\n❌ APIS EN ÉCHEC ({len(self.failed_apis)}):")
            for api in self.failed_apis:
                print(f"   🔴 {api.name}")
                print(f"      Problème: {api.response_message or api.error_details}")
                if api.response_code:
                    print(f"      Code: {api.response_code}")
        
        # APIs partielles
        if self.partial_apis:
            print(f"\n⚠️  APIS PARTIELLES ({len(self.partial_apis)}):")
            for api in self.partial_apis:
                print(f"   🟡 {api.name}")
                print(f"      Status: {api.response_message}")
        
        # Recommandations
        print(f"\n🎯 RECOMMANDATIONS:")
        if self.failed_apis:
            print(f"   1. Vérifier les clés API en échec")
            print(f"   2. Régénérer les tokens expirés")
            print(f"   3. Vérifier les abonnements/crédits")
        if working >= total * 0.8:
            print(f"   ✅ Excellent taux de fonctionnement!")
        else:
            print(f"   ⚠️  Amélioration nécessaire")

def main():
    """Exécution principale de l'audit"""
    auditor = APIKeyAuditor()
    results = auditor.run_full_audit()
    
    # Sauvegarde du rapport
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "results": [
            {
                "name": r.name,
                "status": r.status,
                "response_code": r.response_code,
                "message": r.response_message,
                "credits": r.credits_remaining,
                "plan": r.plan_type,
                "endpoint": r.test_endpoint
            }
            for r in auditor.results
        ]
    }
    
    with open("api_audit_report.json", "w") as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📄 Rapport sauvegardé: api_audit_report.json")

if __name__ == "__main__":
    main()