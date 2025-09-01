#!/usr/bin/env python3
"""🧪 Validation des résultats d'analyse Business Impact.

Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Script de validation pour vérifier la précision de l'analyse des TODOs par impact métier.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

def load_analysis_results(json_file: str = "todo_business_impact_analysis.json") -> Dict:
    """Charger les résultats d'analyse JSON."""
    print("🧪 VALIDATION DE L'ANALYSE BUSINESS IMPACT")
    print("=" * 50)
    
    # Charger les résultats d'analyse
    analysis_data = load_analysis_results()
    
    if not analysis_data:
        print("❌ Impossible de charger les données d'analyse")
        sys.exit(1)
    
    # Exécuter les validations
    validations = [
        ("Fichiers critiques", validate_critical_files),
        ("Catégorisation business", validate_business_categorization),
        ("Scoring de priorité", validate_priority_scoring),
        ("Détection d'APIs", validate_api_detection),
        ("Pourcentages d'implémentation", validate_implementation_percentage)
    ]
    
    results = []
    for name, validation_func in validations:
        try:
            result = validation_func(analysis_data)
            results.append((name, result))
            status = "✅" if result else "❌"
            print(f"\n{status} {name}: {'PASSÉ' if result else 'ÉCHEC'}")
        except Exception as e:
            results.append((name, False))
            print(f"\n❌ {name}: ERREUR - {e}")
    
    # Résumé final
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DE VALIDATION")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"✅ Tests passés: {passed}/{total}")
    print(f"📈 Taux de succès: {(passed/total)*100:.1f}%")
    
    # Afficher le résumé des données
    validation_summary = generate_validation_summary(analysis_data)
    if validation_summary:
        print(f"\n📋 RÉSUMÉ DES DONNÉES ANALYSÉES:")
        for key, value in validation_summary.items():
            print(f"   - {key}: {value}")
    
    # Déterminer le statut final
    if passed >= total * 0.8:  # 80% de réussite requis
        print(f"\n🎉 VALIDATION RÉUSSIE - L'analyse est fiable!")
        sys.exit(0)
    else:
        print(f"\n⚠️ VALIDATION PARTIELLE - Améliorations nécessaires")
        sys.exit(1)

if __name__ == "__main__":
    main()