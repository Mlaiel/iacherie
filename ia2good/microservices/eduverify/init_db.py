#!/usr/bin/env python3
"""
Initialize EduVerify Database with SQLite
Creates all tables and prepares the database
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from eduverify_database import Base
from config import settings

print("=" * 60)
print("🗄️  EDUVERIFY DATABASE INITIALIZATION")
print("=" * 60)
print()

# Force SQLite pour dev
DATABASE_URL = "sqlite:///./eduverify.db"
print(f"Database URL: {DATABASE_URL}")
print()

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

print("📝 Creating database tables...")
try:
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")
    print()
    
    # Lister les tables créées
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ))
        tables = [row[0] for row in result]
        
    print(f"📊 Created {len(tables)} tables:")
    for table in tables:
        if not table.startswith('sqlite_'):
            print(f"   ✅ {table}")
    print()
    
    # Test la connexion
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    session.execute(text("SELECT 1"))
    session.close()
    
    print("🎉 Database initialized successfully!")
    print()
    print("Database file: eduverify.db")
    print("Ready to start EduVerify service!")
    
except Exception as e:
    print(f"❌ Error initializing database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
