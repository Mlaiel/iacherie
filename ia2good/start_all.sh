#!/bin/bash
# Script de lancement de tous les services ia2good
# © 2025 iacherie.com

echo "🚀 LANCEMENT DES SERVICES IA2GOOD"
echo "=================================="
echo ""

# Arrêter les anciens processus
pkill -f "ia2good.*main.py" 2>/dev/null
sleep 2

# Créer le dossier logs s'il n'existe pas
mkdir -p /tmp/ia2good_logs

# Lancer Guardian (port 8001)
cd /workspaces/iacherie/ia2good/microservices/guardian
nohup python main.py > /tmp/ia2good_logs/guardian.log 2>&1 &
GUARDIAN_PID=$!
echo "✅ Guardian lancé (PID: $GUARDIAN_PID, Port: 8001)"

# Lancer EduVerify (port 8002)
cd /workspaces/iacherie/ia2good/microservices/eduverify
nohup python main.py > /tmp/ia2good_logs/eduverify.log 2>&1 &
EDUVERIFY_PID=$!
echo "✅ EduVerify lancé (PID: $EDUVERIFY_PID, Port: 8002)"

# Lancer MedCare (port 8004)
cd /workspaces/iacherie/ia2good/microservices/medcare-ai
nohup python main.py > /tmp/ia2good_logs/medcare.log 2>&1 &
MEDCARE_PID=$!
echo "✅ MedCare lancé (PID: $MEDCARE_PID, Port: 8004)"

echo ""
echo "⏳ Attente du démarrage (30 secondes)..."
sleep 30

echo ""
echo "📊 STATUT DES SERVICES"
echo "======================"

# Vérifier les processus
GUARDIAN_RUNNING=$(ps -p $GUARDIAN_PID > /dev/null 2>&1 && echo "✅ Actif" || echo "❌ Arrêté")
EDUVERIFY_RUNNING=$(ps -p $EDUVERIFY_PID > /dev/null 2>&1 && echo "✅ Actif" || echo "❌ Arrêté")
MEDCARE_RUNNING=$(ps -p $MEDCARE_PID > /dev/null 2>&1 && echo "✅ Actif" || echo "❌ Arrêté")

echo "- Guardian  (8001): $GUARDIAN_RUNNING"
echo "- EduVerify (8002): $EDUVERIFY_RUNNING"
echo "- MedCare   (8004): $MEDCARE_RUNNING"

echo ""
echo "🔍 PORTS EN ÉCOUTE"
echo "=================="
ss -tuln | grep -E ":(8001|8002|8004)" | awk '{print $5}' | sort -u || echo "Aucun port ia2good en écoute"

echo ""
echo "📝 LOGS DISPONIBLES"
echo "==================="
echo "  tail -f /tmp/ia2good_logs/guardian.log"
echo "  tail -f /tmp/ia2good_logs/eduverify.log"
echo "  tail -f /tmp/ia2good_logs/medcare.log"
echo ""
echo "✅ Script terminé !"
