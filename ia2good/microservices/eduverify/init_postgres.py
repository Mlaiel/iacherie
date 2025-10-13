#!/usr/bin/env python3
"""
Script d'initialisation PostgreSQL pour EduVerify
Crée toutes les tables et extensions nécessaires
"""

import sys
import os
from pathlib import Path

# Ajouter le chemin du module
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from database import Base, engine
from config import settings

def init_database():
    """Initialise la base de données PostgreSQL"""
    print("🚀 Initialisation PostgreSQL EduVerify...")
    print(f"📡 Connection: {settings.DATABASE_URL.split('@')[1]}")  # Masquer credentials
    
    try:
        # 1. Créer les extensions PostgreSQL nécessaires
        print("\n📦 Installation des extensions PostgreSQL...")
        with engine.connect() as conn:
            # uuid-ossp pour génération UUID
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            print("  ✅ uuid-ossp installée")
            
            # pg_trgm pour recherche texte full-text
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "pg_trgm";'))
            print("  ✅ pg_trgm installée")
            
            conn.commit()
        
        # 2. Créer toutes les tables
        print("\n🔨 Création des tables...")
        Base.metadata.create_all(bind=engine)
        
        # 3. Vérifier les tables créées
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'eduverify_%'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
            print(f"\n✅ {len(tables)} tables créées:")
            for table in tables:
                print(f"  • {table}")
        
        # 4. Créer index pour performance
        print("\n📊 Création des index supplémentaires...")
        with engine.connect() as conn:
            # Index pour recherche full-text sur content_text
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_text_search 
                ON eduverify_content 
                USING gin (to_tsvector('french', content_text));
            """))
            print("  ✅ Index full-text sur content_text")
            
            # Index pour recherche dans les messages chat
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_chat_message_search 
                ON eduverify_chat_messages 
                USING gin (to_tsvector('french', content));
            """))
            print("  ✅ Index full-text sur chat messages")
            
            conn.commit()
        
        print("\n🎉 Initialisation PostgreSQL terminée avec succès!")
        print("✅ EduVerify database est prête à l'emploi\n")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors de l'initialisation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
