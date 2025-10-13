#!/bin/bash
# =================================================================
# 🤖 DOWNLOAD AI MODELS FOR STUDIOS + LIVE STREAMING
# =================================================================
# Télécharge tous les modèles nécessaires pour les Studios
# Auteur: Fahed Mlaiel
# Date: 13 Octobre 2025
# =================================================================

set -e  # Exit on error

echo "🤖 TÉLÉCHARGEMENT DES MODÈLES IA POUR LES STUDIOS"
echo "=================================================="
echo ""

# Créer le répertoire weights
mkdir -p weights
cd weights

# =================================================================
# 1. Real-ESRGAN (Upscaling 4x) - 250MB
# =================================================================
echo "📥 1/3 - Téléchargement Real-ESRGAN (250MB)..."
if [ -f "RealESRGAN_x4plus.pth" ]; then
    echo "   ✅ Déjà téléchargé"
else
    wget https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
    echo "   ✅ Real-ESRGAN téléchargé"
fi
echo ""

# =================================================================
# 2. Wav2Lip (Lip Sync) - 200MB
# =================================================================
echo "📥 2/3 - Téléchargement Wav2Lip (200MB)..."
if [ -f "wav2lip_gan.pth" ]; then
    echo "   ✅ Déjà téléchargé"
else
    # Note: L'URL SharePoint peut nécessiter un navigateur
    echo "   ⚠️  Téléchargement manuel requis pour Wav2Lip"
    echo "   📌 URL: https://iiitaphyd-my.sharepoint.com/:u:/g/personal/radrabha_m_research_iiit_ac_in/Eb3LEzbfuKlJiR600lQWRxgBIY27JZg80f7V9jtMfbNDaQ"
    echo "   💾 Sauvegarder sous: weights/wav2lip_gan.pth"
fi
echo ""

# =================================================================
# 3. Whisper Base (Transcription) - Auto-download
# =================================================================
echo "📥 3/3 - Whisper Base"
echo "   ℹ️  Whisper se télécharge automatiquement au premier usage (~150MB)"
echo ""

# =================================================================
# RÉSUMÉ
# =================================================================
echo "✅ RÉSUMÉ DES TÉLÉCHARGEMENTS"
echo "============================="
echo ""
ls -lh *.pth 2>/dev/null || echo "Aucun fichier .pth trouvé"
echo ""
echo "📊 Espace disque utilisé:"
du -sh . 2>/dev/null || echo "Calcul en cours..."
echo ""
echo "🎯 PROCHAINES ÉTAPES:"
echo "   1. Télécharger manuellement wav2lip_gan.pth si nécessaire"
echo "   2. Whisper se téléchargera automatiquement lors du premier usage"
echo "   3. Les modèles SDXL/Stable Diffusion se téléchargent via diffusers"
echo ""
echo "✅ PRÊT POUR LES TESTS !"
