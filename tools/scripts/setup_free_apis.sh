#!/bin/bash

# 🆓 SETUP APIS GRATUITES POUR AINFLUENCER
# Auteur: Multi-Expert Team
# Date: 24 septembre 2025

set -e

echo "🚀 SETUP APIS GRATUITES POUR TESTS RÉELS - AINFLUENCER"
echo "="
echo ""

# Créer le fichier .env.testing
echo "📝 Création du fichier .env.testing avec APIs gratuites..."

cat > .env.testing << 'EOF'
# 🆓 APIs GRATUITES POUR TESTS AINFLUENCER
# Date: 24 septembre 2025

# =============================================================================
# 🤖 INTELLIGENCE ARTIFICIELLE (100% GRATUIT)
# =============================================================================

# Hugging Face (30,000 requests/mois gratuit)
HUGGINGFACE_API_KEY=hf_REMPLACEZ_PAR_VOTRE_CLE
HUGGINGFACE_MODEL=gpt2-large

# Google Gemini Pro (1M tokens/jour gratuit)
GOOGLE_GEMINI_API_KEY=AIzaSy_REMPLACEZ_PAR_VOTRE_CLE
GOOGLE_GEMINI_MODEL=gemini-pro

# Cohere (1000 requests/mois gratuit)
COHERE_API_KEY=REMPLACEZ_PAR_VOTRE_CLE

# =============================================================================
# 📱 RÉSEAUX SOCIAUX (GRATUIT/FREEMIUM)
# =============================================================================

# YouTube Data API v3 (10,000 quota/jour gratuit)
YOUTUBE_API_KEY=AIzaSy_REMPLACEZ_PAR_VOTRE_CLE
YOUTUBE_CLIENT_ID=REMPLACEZ.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=REMPLACEZ_PAR_VOTRE_SECRET

# TikTok API (Basic access gratuit)
TIKTOK_CLIENT_KEY=REMPLACEZ_PAR_VOTRE_CLE
TIKTOK_CLIENT_SECRET=REMPLACEZ_PAR_VOTRE_SECRET

# Twitter API v2 (500k tweets/mois gratuit en lecture)
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAA_REMPLACEZ
TWITTER_API_KEY=REMPLACEZ_PAR_VOTRE_CLE

# =============================================================================
# 💳 PAIEMENTS TEST (100% GRATUIT EN SANDBOX)
# =============================================================================

# Stripe Test Mode (Illimité gratuit)
STRIPE_PUBLISHABLE_KEY=pk_test_REMPLACEZ_PAR_VOTRE_CLE
STRIPE_SECRET_KEY=sk_test_REMPLACEZ_PAR_VOTRE_CLE
STRIPE_WEBHOOK_SECRET=whsec_REMPLACEZ_PAR_VOTRE_SECRET
STRIPE_API_VERSION=2023-10-16

# PayPal Sandbox (100% gratuit)
PAYPAL_CLIENT_ID=REMPLACEZ_PAR_VOTRE_CLIENT_ID
PAYPAL_CLIENT_SECRET=REMPLACEZ_PAR_VOTRE_SECRET
PAYPAL_MODE=sandbox

# Square Sandbox (Gratuit)
SQUARE_ACCESS_TOKEN=EAAAl_REMPLACEZ_PAR_VOTRE_TOKEN
SQUARE_APPLICATION_ID=sandbox-sq0idb-REMPLACEZ

# =============================================================================
# 📧 EMAIL & SMS (GRATUIT)
# =============================================================================

# Resend (3,000 emails/mois gratuit)
RESEND_API_KEY=re_REMPLACEZ_PAR_VOTRE_CLE

# SendGrid (100 emails/jour gratuit)
SENDGRID_API_KEY=SG.REMPLACEZ_PAR_VOTRE_CLE

# Twilio Trial ($15.50 crédit gratuit)
TWILIO_ACCOUNT_SID=AC_REMPLACEZ_PAR_VOTRE_SID
TWILIO_AUTH_TOKEN=REMPLACEZ_PAR_VOTRE_TOKEN
TWILIO_PHONE_NUMBER=+1_VOTRE_NUMERO_TEST

# =============================================================================
# 🗄️ BASE DE DONNÉES (GRATUIT)  
# =============================================================================

# Supabase (500MB gratuit)
SUPABASE_URL=https://VOTRE_PROJET.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.REMPLACEZ
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.REMPLACEZ

# PlanetScale (5GB gratuit)
PLANETSCALE_DB_URL=mysql://user:pass@host.planetscale.sh:3306/db

# MongoDB Atlas (512MB gratuit)
MONGODB_URI=mongodb+srv://user:pass@cluster0.xxxxx.mongodb.net/database

# =============================================================================
# 📊 ANALYTICS & MONITORING (GRATUIT)
# =============================================================================

# Google Analytics 4 (100% gratuit)
GOOGLE_ANALYTICS_MEASUREMENT_ID=G-XXXXXXXXXX
GOOGLE_ANALYTICS_API_SECRET=REMPLACEZ_PAR_VOTRE_SECRET

# Sentry (5,000 errors/mois gratuit)
SENTRY_DSN=https://VOTRE_KEY@o000000.ingest.sentry.io/0000000

# LogRocket (1,000 sessions/mois gratuit)
LOGROCKET_APP_ID=VOTRE_APP_ID/project-name

# =============================================================================
# 🔍 RECHERCHE & DONNÉES (GRATUIT)
# =============================================================================

# Algolia (10,000 requests/mois gratuit)
ALGOLIA_APPLICATION_ID=VOTRE_APP_ID
ALGOLIA_API_KEY=REMPLACEZ_PAR_VOTRE_CLE

# Pinecone (1M vectors gratuit)
PINECONE_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-west1-gcp

# =============================================================================
# 🌍 AUTRES SERVICES UTILES (GRATUIT)
# =============================================================================

# Cloudinary (25 crédits/mois gratuit)
CLOUDINARY_CLOUD_NAME=VOTRE_CLOUD_NAME
CLOUDINARY_API_KEY=VOTRE_API_KEY
CLOUDINARY_API_SECRET=VOTRE_API_SECRET

# Redis Cloud (30MB gratuit)
REDIS_URL=redis://default:password@host:port

# Webhooks.site (Tests webhooks gratuit)
WEBHOOK_TEST_URL=https://webhook.site/VOTRE_UUID

EOF

echo "✅ Fichier .env.testing créé!"
echo ""

# Créer un script de validation
echo "🔧 Création du script de validation des APIs..."

cat > validate_apis.py << 'EOF'
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
EOF

chmod +x validate_apis.py

echo "✅ Script de validation créé!"
echo ""

# Instructions finales
echo "📋 PROCHAINES ÉTAPES:"
echo "1️⃣  Éditez le fichier .env.testing avec vos vraies clés d'API"
echo "2️⃣  Lancez: python validate_apis.py pour tester"
echo "3️⃣  Chargez les variables: export \$(cat .env.testing | xargs)"
echo "4️⃣  Démarrez Ainfluencer avec les APIs gratuites!"
echo ""

echo "🔗 LIENS D'INSCRIPTION RAPIDE:"
echo "• Hugging Face: https://huggingface.co/join"  
echo "• YouTube API: https://console.cloud.google.com/apis/library/youtube.googleapis.com"
echo "• Stripe Test: https://stripe.com/"
echo "• Resend: https://resend.com/"
echo "• Supabase: https://supabase.com/"
echo ""

echo "🎯 TEMPS ESTIMÉ D'INSCRIPTION: 15-30 minutes pour toutes les APIs!"
echo "💰 COÛT TOTAL: 0€ - 100% GRATUIT pour les tests!"

echo ""
echo "✅ Setup terminé! Vous pouvez maintenant tester Ainfluencer avec de vraies APIs gratuites! 🚀"