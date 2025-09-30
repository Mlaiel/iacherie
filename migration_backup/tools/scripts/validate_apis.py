#!/usr/bin/env python3
"""
🧪 VALIDATEUR D'APIs GRATUITES - AINFLUENCER
Teste la connectivité et fonctionnement des APIs gratuites
"""

import os
import requests
import json
from datetime import datetime

def load_env_testing():
    """Charge le fichier .env.testing"""
    env_vars = {}
    try:
        with open('.env.testing', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    if not value.startswith('REMPLACEZ'):
                        env_vars[key] = value
        return env_vars
    except FileNotFoundError:
        print("❌ Fichier .env.testing non trouvé!")
        return {}

def test_huggingface_api(api_key):
    """Test Hugging Face API"""
    if not api_key or api_key.startswith('REMPLACEZ'):
        return "❌ Clé manquante"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        if response.status_code == 200:
            return "✅ Connecté"
        else:
            return f"❌ Erreur {response.status_code}"
    except Exception as e:
        return f"❌ Erreur: {str(e)[:30]}"

def test_youtube_api(api_key):
    """Test YouTube Data API"""
    if not api_key or api_key.startswith('REMPLACEZ'):
        return "❌ Clé manquante"
    
    try:
        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=test&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            return "✅ API fonctionnelle"
        else:
            return f"❌ Erreur {response.status_code}"
    except Exception as e:
        return f"❌ Erreur: {str(e)[:30]}"

def test_stripe_api(secret_key):
    """Test Stripe API"""
    if not secret_key or secret_key.startswith('REMPLACEZ'):
        return "❌ Clé manquante"
        
    headers = {"Authorization": f"Bearer {secret_key}"}
    try:
        response = requests.get("https://api.stripe.com/v1/customers?limit=1", headers=headers)
        if response.status_code == 200:
            return "✅ Mode test actif"
        else:
            return f"❌ Erreur {response.status_code}"
    except Exception as e:
        return f"❌ Erreur: {str(e)[:30]}"

def main():
    print("🧪 VALIDATION DES APIs GRATUITES - AINFLUENCER")
    print("=" * 50)
    print(f"📅 Test exécuté le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    env_vars = load_env_testing()
    
    if not env_vars:
        print("❌ Aucune variable d'environnement configurée")
        return
    
    tests = [
        ("🤖 Hugging Face", "HUGGINGFACE_API_KEY", test_huggingface_api),
        ("📺 YouTube API", "YOUTUBE_API_KEY", test_youtube_api), 
        ("💳 Stripe Test", "STRIPE_SECRET_KEY", test_stripe_api),
    ]
    
    print("🔍 RÉSULTATS DES TESTS:")
    print("-" * 30)
    
    success_count = 0
    total_tests = len(tests)
    
    for name, env_key, test_func in tests:
        api_key = env_vars.get(env_key, "REMPLACEZ")
        result = test_func(api_key)
        print(f"{name}: {result}")
        
        if result.startswith("✅"):
            success_count += 1
    
    print()
    print(f"📊 BILAN: {success_count}/{total_tests} APIs configurées et fonctionnelles")
    
    if success_count == total_tests:
        print("🏆 Toutes les APIs sont prêtes pour les tests!")
    elif success_count > 0:
        print("⚠️  Certaines APIs nécessitent une configuration")
    else:
        print("❌ Veuillez configurer vos clés d'API dans .env.testing")

if __name__ == "__main__":
    main()
