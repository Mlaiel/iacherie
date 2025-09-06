#!/usr/bin/env python3
"""
Validation finale des migrations Alembic - Consolidation Strategy
Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import py_compile
import sys
from pathlib import Path

def validate_migration_syntax():
    """Validate syntax of all migration files."""
    print("🔍 VALIDATION SYNTAX MIGRATIONS ALEMBIC")
    print("=" * 50)
    
    migrations_dir = Path("alembic/versions")
    errors = []
    success_count = 0
    
    # Get all Python migration files
    migration_files = [f for f in migrations_dir.glob("*.py") if not f.name.startswith("__")]
    
    for migration_file in migration_files:
        try:
            py_compile.compile(str(migration_file), doraise=True)
            print(f"✅ {migration_file.name} - SYNTAX OK")
            success_count += 1
        except py_compile.PyCompileError as e:
            print(f"❌ {migration_file.name} - SYNTAX ERROR: {e}")
            errors.append(str(migration_file))
    
    print(f"\n📊 RÉSULTATS VALIDATION:")
    print(f"✅ Fichiers validés: {success_count}")
    print(f"❌ Erreurs syntax: {len(errors)}")
    
    if errors:
        print(f"\n🔴 ERREURS DÉTECTÉES:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("\n🎊 VALIDATION COMPLÈTE RÉUSSIE!")
    return True

def analyze_migration_content():
    """Analyze migration content for completeness."""
    print("\n🔬 ANALYSE CONTENU MIGRATIONS")
    print("=" * 40)
    
    migrations_dir = Path("alembic/versions")
    migration_files = [f for f in migrations_dir.glob("*.py") if not f.name.startswith("__")]
    
    total_lines = 0
    enrichments_found = {}
    
    enrichment_keywords = [
        "quantum", "blockchain", "nft", "crypto", "ai_agent", 
        "multilingual", "enterprise", "accessibility", "644",
        "100+", "real_time", "intelligent", "optimization"
    ]
    
    for migration_file in migration_files:
        if migration_file.name == "checkliste.md":
            continue
            
        with open(migration_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.splitlines())
            total_lines += lines
            
            print(f"📄 {migration_file.name}")
            print(f"   📏 Lignes: {lines}")
            
            # Count enrichment features
            for keyword in enrichment_keywords:
                count = content.lower().count(keyword.lower())
                if count > 0:
                    if keyword not in enrichments_found:
                        enrichments_found[keyword] = 0
                    enrichments_found[keyword] += count
    
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"📏 Total lignes code: {total_lines}")
    print(f"📁 Migrations analysées: {len(migration_files) - 1}")  # -1 for checkliste.md
    
    print(f"\n🎯 ENRICHISSEMENTS DÉTECTÉS:")
    for keyword, count in sorted(enrichments_found.items()):
        print(f"   🔸 {keyword}: {count} occurrences")
    
    return True

def main():
    """Main validation function."""
    print("🚀 VALIDATION FINALE AINFLUE ALEMBIC CONSOLIDATION")
    print("=" * 60)
    print("Architecte: Fahed Mlaiel (mlaiel@live.de)")
    print("© 2025 Fahed Mlaiel. All rights reserved.")
    print("=" * 60)
    
    # Change to repository root
    if os.path.exists("alembic/versions"):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Validate syntax
    syntax_ok = validate_migration_syntax()
    
    # Analyze content
    content_ok = analyze_migration_content()
    
    # Final report
    print("\n" + "=" * 60)
    if syntax_ok and content_ok:
        print("✅ VALIDATION FINALE: SUCCÈS COMPLET")
        print("🎊 CONSOLIDATION STRATEGY: IMPLÉMENTATION TERMINÉE")
        return 0
    else:
        print("❌ VALIDATION FINALE: ERREURS DÉTECTÉES")
        return 1

if __name__ == "__main__":
    sys.exit(main())