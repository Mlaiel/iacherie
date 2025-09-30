#!/bin/bash

# Script de Configuration des APIs Externes
# ========================================

echo "🚀 Configuration des APIs Externes pour Ainfluencer"
echo "=================================================="

# Fonction pour demander une clé API
ask_for_api_key() {
    local service_name=$1
    local env_var_name=$2
    local current_value=$(grep "^$env_var_name=" .env.production | cut -d'=' -f2-)
    
    echo ""
    echo "📋 Configuration de $service_name"
    echo "Variable: $env_var_name"
    
    if [[ $current_value && $current_value != "REMPLACEZ_PAR_VOTRE_CLE"* ]]; then
        echo "✅ Déjà configuré: ${current_value:0:10}..."
        read -p "Voulez-vous le changer? (y/N): " change
        if [[ $change != "y" && $change != "Y" ]]; then
            return
        fi
    fi
    
    read -p "Entrez votre clé API $service_name (ou appuyez sur Entrée pour ignorer): " new_key
    
    if [[ $new_key ]]; then
        # Remplacer dans le fichier .env.production
        if grep -q "^$env_var_name=" .env.production; then
            sed -i "s|^$env_var_name=.*|$env_var_name=$new_key|" .env.production
        else
            echo "$env_var_name=$new_key" >> .env.production
        fi
        echo "✅ $service_name configuré!"
    else
        echo "⏭️  $service_name ignoré"
    fi
}

# Créer une sauvegarde
cp .env.production .env.production.backup.$(date +%Y%m%d_%H%M%S)
echo "💾 Sauvegarde créée: .env.production.backup.$(date +%Y%m%d_%H%M%S)"

echo ""
echo "🔑 Configuration des Services API:"
echo ""
echo "1. OpenAI (DALL-E, GPT, TTS) - Premium mais haute qualité"
echo "2. Stability AI (Images) - Excellent pour les images"
echo "3. Hugging Face (Gratuit) - Bon démarrage, modèles open source"
echo "4. Cohere (Texte) - Alternative à GPT"
echo "5. ElevenLabs (Audio) - Meilleure qualité vocale"
echo ""

# Configuration des APIs principales
ask_for_api_key "OpenAI" "OPENAI_API_KEY"
ask_for_api_key "Stability AI" "STABILITY_API_KEY"
ask_for_api_key "Hugging Face" "HUGGINGFACE_API_KEY"
ask_for_api_key "Cohere" "COHERE_API_KEY"
ask_for_api_key "ElevenLabs" "ELEVENLABS_API_KEY"

echo ""
echo "🎯 APIs Optionnelles:"
ask_for_api_key "Google Gemini" "GOOGLE_GEMINI_API_KEY"
ask_for_api_key "Anthropic Claude" "ANTHROPIC_API_KEY"
ask_for_api_key "Replicate" "REPLICATE_API_TOKEN"

echo ""
echo "✅ Configuration terminée!"
echo ""
echo "📊 Récapitulatif des APIs configurées:"
echo "======================================"

# Vérifier quelles APIs sont configurées
configured_apis=()
if grep -q "^OPENAI_API_KEY=sk-" .env.production; then
    configured_apis+=("✅ OpenAI")
else
    configured_apis+=("❌ OpenAI")
fi

if grep -q "^STABILITY_API_KEY=[^R]" .env.production; then
    configured_apis+=("✅ Stability AI")
else
    configured_apis+=("❌ Stability AI")
fi

if grep -q "^HUGGINGFACE_API_KEY=hf_" .env.production; then
    configured_apis+=("✅ Hugging Face")
else
    configured_apis+=("❌ Hugging Face")
fi

if grep -q "^COHERE_API_KEY=[^R]" .env.production; then
    configured_apis+=("✅ Cohere")
else
    configured_apis+=("❌ Cohere")
fi

if grep -q "^ELEVENLABS_API_KEY=[^R]" .env.production; then
    configured_apis+=("✅ ElevenLabs")
else
    configured_apis+=("❌ ElevenLabs")
fi

for api in "${configured_apis[@]}"; do
    echo "$api"
done

echo ""
echo "🚀 Actions suivantes:"
echo "1. Testez vos APIs: python test_apis.py"
echo "2. Démarrez le serveur: python main.py"
echo "3. Visitez: http://localhost:8000"
echo ""
echo "💡 Conseils:"
echo "- OpenAI: Le plus cher mais meilleure qualité"
echo "- Hugging Face: Gratuit pour commencer (limité)"
echo "- Stability AI: Excellent rapport qualité/prix pour les images"
echo ""
echo "🔒 Sécurité: Ne commitez jamais le fichier .env.production sur Git!"