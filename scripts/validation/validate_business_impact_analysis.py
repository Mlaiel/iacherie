#!/usr/bin/env python3
"""🧪 Validation des résultats d'analyse Business Impact
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Script de validation pour vérifier la précision de l'analyse des TODOs par impact métier.
"""
import json
import sys
from pathlib import Path
from typing import List, Dict

def load_analysis_results(json_file: str = "todo_business_impact_analysis.json") -> Dict:
    """Charger les résultats d'analyse JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier d'analyse non trouvé: {json_file}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return {}

def validate_critical_files(analysis_data: Dict) -> bool:
    """Valider l'identification des fichiers critiques"""
    print("🔍 Validation des fichiers critiques...")
    
    if not analysis_data or 'detailed_analysis' not in analysis_data:
        print("❌ Données d'analyse manquantes")
        return False
    
    critical_files = [
        item for item in analysis_data['detailed_analysis']
        if item['business_impact'] == 'critical'
    ]
    
    print(f"📊 Fichiers critiques identifiés: {len(critical_files)}")
    
    # Vérifier la présence de fichiers business core critiques attendus
    expected_critical_patterns = [
        'main.py', 'config.py', 'business_logic', 'core',
        'monetization', 'licensing', 'ai_engine'
    ]
    
    found_patterns = []
    for pattern in expected_critical_patterns:
        for file_item in critical_files:
            if pattern in file_item['file_path'].lower():
                found_patterns.append(pattern)
                break
    
    print(f"✅ Patterns critiques trouvés: {found_patterns}")
    
    # Au moins 50% des patterns critiques doivent être trouvés
    return len(found_patterns) >= len(expected_critical_patterns) * 0.5

def validate_business_categorization(analysis_data: Dict) -> bool:
    """Valider la catégorisation par type de business"""
    print("\n🏗️ Validation de la catégorisation business...")
    
    if 'summary' not in analysis_data or 'by_code_type' not in analysis_data['summary']:
        print("❌ Données de catégorisation manquantes")
        return False
    
    by_code_type = analysis_data['summary']['by_code_type']
    
    # Vérifier la présence des types de code attendus
    expected_types = [
        'business_core', 'ai_agents', 'api_external', 'crawlers',
        'security', 'utilities', 'tests'
    ]
    
    found_types = [t for t in expected_types if t in by_code_type]
    print(f"📊 Types de code identifiés: {len(found_types)}/{len(expected_types)}")
    print(f"✅ Types trouvés: {found_types}")
    
    # Vérifier que business_core a une priorité élevée
    if 'business_core' in by_code_type:
        business_priority = by_code_type['business_core']['avg_priority']
        print(f"💼 Priorité Business Core: {business_priority:.1f}/100")
        
        if business_priority > 50:
            print("✅ Business Core correctement priorisé (>50)")
            return True
        else:
            print("⚠️ Business Core sous-priorisé (<50)")
            return False
    
    return len(found_types) >= len(expected_types) * 0.7

def validate_priority_scoring(analysis_data: Dict) -> bool:
    """Valider le système de scoring de priorité"""
    print("\n🎯 Validation du scoring de priorité...")
    
    if 'detailed_analysis' not in analysis_data:
        print("❌ Données détaillées manquantes")
        return False
    
    detailed = analysis_data['detailed_analysis']
    
    # Analyser la distribution des scores
    scores = [item['priority_score'] for item in detailed]
    avg_score = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    
    print(f"📊 Scores de priorité:")
    print(f"   - Moyenne: {avg_score:.1f}")
    print(f"   - Maximum: {max_score:.1f}")
    print(f"   - Minimum: {min_score:.1f}")
    
    # Vérifier que les scores critiques sont plus élevés
    critical_scores = [
        item['priority_score'] for item in detailed
        if item['business_impact'] == 'critical'
    ]
    
    non_critical_scores = [
        item['priority_score'] for item in detailed
        if item['business_impact'] != 'critical'
    ]
    
    if critical_scores and non_critical_scores:
        avg_critical = sum(critical_scores) / len(critical_scores)
        avg_non_critical = sum(non_critical_scores) / len(non_critical_scores)
        
        print(f"🔴 Score moyen critique: {avg_critical:.1f}")
        print(f"🔵 Score moyen non-critique: {avg_non_critical:.1f}")
        
        if avg_critical > avg_non_critical:
            print("✅ Scoring critique correctement plus élevé")
            return True
        else:
            print("⚠️ Scoring critique pas assez différencié")
            return False
    
    return True

def validate_api_detection(analysis_data: Dict) -> bool:
    """Valider la détection des APIs externes"""
    print("\n🌐 Validation de la détection d'APIs externes...")
    
    if 'detailed_analysis' not in analysis_data:
        print("❌ Données détaillées manquantes")
        return False
    
    detailed = analysis_data['detailed_analysis']
    
    # Compter les fichiers avec APIs externes détectées
    files_with_apis = [
        item for item in detailed
        if item['external_apis'] and len(item['external_apis']) > 0
    ]
    
    print(f"📊 Fichiers avec APIs externes: {len(files_with_apis)}")
    
    # Afficher quelques exemples
    if files_with_apis:
        print("🔍 Exemples d'APIs détectées:")
        for i, item in enumerate(files_with_apis[:3]):
            print(f"   - {item['file_path']}: {item['external_apis'][:3]}")
    
    # Au moins quelques APIs doivent être détectées dans un projet de cette taille
    return len(files_with_apis) > 0

def validate_implementation_percentage(analysis_data: Dict) -> bool:
    """Valider le calcul des pourcentages d'implémentation"""
    print("\n📈 Validation des pourcentages d'implémentation...")
    
    if 'detailed_analysis' not in analysis_data:
        print("❌ Données détaillées manquantes")
        return False
    
    detailed = analysis_data['detailed_analysis']
    
    # Analyser la distribution des pourcentages d'implémentation
    impl_percentages = [item['implementation_percentage'] for item in detailed]
    avg_impl = sum(impl_percentages) / len(impl_percentages)
    
    print(f"📊 Implémentation moyenne: {avg_impl:.1f}%")
    
    # Vérifier que les pourcentages sont dans des plages réalistes
    valid_percentages = [p for p in impl_percentages if 0 <= p <= 100]
    
    print(f"✅ Pourcentages valides: {len(valid_percentages)}/{len(impl_percentages)}")
    
    # Afficher quelques fichiers avec faible implémentation
    low_impl = [
        item for item in detailed
        if item['implementation_percentage'] < 80
    ]
    
    if low_impl:
        print(f"⚠️ Fichiers avec implémentation < 80%: {len(low_impl)}")
        for item in low_impl[:3]:
            print(f"   - {item['file_path']}: {item['implementation_percentage']:.1f}%")
    
    return len(valid_percentages) == len(impl_percentages) and avg_impl > 50

def generate_validation_summary(analysis_data: Dict) -> Dict:
    """Générer un résumé de validation"""
    if not analysis_data or 'summary' not in analysis_data:
        return {}
    
    summary = analysis_data['summary']
    
    return {
        "total_files_analyzed": summary['statistics']['total_files_with_gaps'],
        "total_implementation_gaps": summary['statistics']['total_implementation_gaps'],
        "code_types_identified": len(summary['by_code_type']),
        "business_impact_levels": len(summary['by_business_impact']),
        "top_priority_files": len(summary.get('top_priorities', [])),
        "critical_files_count": summary['by_business_impact'].get('critical', {}).get('count', 0),
        "validation_timestamp": analysis_data['summary']['scan_date']
    }

def main():
    """Point d'entrée principal de validation"""
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