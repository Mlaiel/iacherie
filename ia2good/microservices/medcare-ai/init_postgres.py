#!/usr/bin/env python3
"""
Script d'initialisation PostgreSQL pour MedCare-AI
Exécute le schema.sql pour créer toutes les tables
"""

import sys
import os
from pathlib import Path
import psycopg2
from psycopg2 import sql

# Configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "ia2good",
    "user": "ia2good",
    "password": "ia2good_secure_2025"
}

def init_database():
    """Initialise la base de données MedCare PostgreSQL"""
    print("🚀 Initialisation PostgreSQL MedCare-AI...")
    print(f"📡 Connection: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    
    try:
        # Connexion à PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Lire le fichier schema.sql
        schema_path = Path(__file__).parent / "schema.sql"
        print(f"\n📄 Lecture du schema: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Exécuter le schema
        print("\n🔨 Création des tables MedCare...")
        cursor.execute(schema_sql)
        
        # Vérifier les tables créées
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'medcare_%'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        print(f"\n✅ {len(tables)} tables MedCare créées:")
        for table in tables:
            print(f"  • {table}")
        
        # Vérifier les index
        cursor.execute("""
            SELECT indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND tablename LIKE 'medcare_%'
            AND indexname LIKE 'idx_medcare_%'
            ORDER BY indexname;
        """)
        indexes = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 {len(indexes)} index créés pour performance")
        
        # Vérifier les triggers
        cursor.execute("""
            SELECT trigger_name, event_object_table
            FROM information_schema.triggers
            WHERE event_object_schema = 'public'
            AND event_object_table LIKE 'medcare_%'
            ORDER BY event_object_table, trigger_name;
        """)
        triggers = cursor.fetchall()
        
        print(f"\n⚡ {len(triggers)} triggers créés pour updated_at")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Initialisation PostgreSQL MedCare terminée avec succès!")
        print("✅ MedCare-AI database est prête à l'emploi\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'initialisation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
