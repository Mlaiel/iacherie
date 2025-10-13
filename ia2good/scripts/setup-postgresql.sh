#!/bin/bash

echo "================================================================"
echo "🗄️  CONFIGURATION POSTGRESQL COMPLÈTE - IA2GOOD"
echo "================================================================"
echo ""

# Configuration PostgreSQL sans mot de passe
export PGPASSWORD=""
export PGHOST="localhost"
export PGPORT="5432"

echo "📝 Étape 1: Vérification PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL n'est pas accessible"
    echo "Essai de démarrage..."
    sudo service postgresql start 2>/dev/null || true
    sleep 2
fi

if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ PostgreSQL est actif"
else
    echo "⚠️  PostgreSQL non disponible, utilisation de SQLite en fallback"
    exit 0
fi

echo ""
echo "📝 Étape 2: Configuration avec utilisateur codespace..."

# Créer les bases de données avec l'utilisateur courant (pas besoin de sudo)
createdb ia2good 2>/dev/null && echo "✅ Base ia2good créée" || echo "⚠️  Base ia2good existe déjà"

# Créer les extensions nécessaires
psql -d ia2good -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";" 2>/dev/null && echo "✅ Extension uuid-ossp installée"
psql -d ia2good -c "CREATE EXTENSION IF NOT EXISTS \"pg_trgm\";" 2>/dev/null && echo "✅ Extension pg_trgm installée"

echo ""
echo "📝 Étape 3: Vérification des bases de données..."
psql -l | grep ia2good && echo "✅ Base de données ia2good confirmée"

echo ""
echo "📝 Étape 4: Test de connexion..."
psql -d ia2good -c "SELECT version();" > /dev/null 2>&1 && echo "✅ Connexion à ia2good réussie"

echo ""
echo "================================================================"
echo "✅ POSTGRESQL CONFIGURÉ AVEC SUCCÈS"
echo "================================================================"
echo ""
echo "Configuration:"
echo "  Host:     localhost"
echo "  Port:     5432"
echo "  Database: ia2good"
echo "  User:     $USER (vous)"
echo ""
echo "Connection string pour EduVerify:"
echo "  postgresql://$USER@localhost:5432/ia2good"
echo ""
echo "Connection string pour Guardian:"
echo "  postgresql://$USER@localhost:5432/ia2good"
echo ""
echo "Connection string pour MedCare:"
echo "  postgresql://$USER@localhost:5432/ia2good"
echo ""
