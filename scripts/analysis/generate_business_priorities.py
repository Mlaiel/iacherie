#!/usr/bin/env python3
"""🎯 Générateur de priorités business actionables
Author: Fahed Mlaiel <mlaiel@live.de>

Extrait les insights business critiques de l'analyse TODO et génère
des recommandations d'actions concrètes par impact métier.
"""import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime

def load_analysis_data() -> Dict:
    """Charger les données d'analyse"""    try:
        with open("todo_business_impact_analysis.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def extract_critical_business_actions(data: Dict) -> Dict:
    """Extraire les actions critiques pour le business"""    
    if not data or 'detailed_analysis' not in data:
        return {}
    
    detailed = data['detailed_analysis']
    
    # Fichiers critiques avec actions spécifiques
    critical_files = [
        item for item in detailed 
        if item['business_impact'] == 'critical'
    ]
    
    # Fichiers high-impact business
    high_impact_files = [
        item for item in detailed
        if item['business_impact'] == 'high'
    ]
    
    # Actions par domaine métier
    business_domains = {
        'platform_integration': [],
        'ai_engines': [],
        'data_collection': [],
        'monetization': [],
        'security': [],
        'infrastructure': []
    }
    
    # Classifier par domaine métier
    for item in detailed:
        file_path = item['file_path'].lower()
        
        if any(keyword in file_path for keyword in ['platform', 'mastodon', 'spotify', 'youtube']):
            business_domains['platform_integration'].append(item)
        elif any(keyword in file_path for keyword in ['ai_engine', 'agent', 'ai_']):
            business_domains['ai_engines'].append(item)
        elif any(keyword in file_path for keyword in ['crawler', 'data', 'collection']):
            business_domains['data_collection'].append(item)
        elif any(keyword in file_path for keyword in ['monetization', 'billing', 'revenue']):
            business_domains['monetization'].append(item)
        elif any(keyword in file_path for keyword in ['security', 'auth', 'protection']):
            business_domains['security'].append(item)
        elif any(keyword in file_path for keyword in ['infrastructure', 'monitoring', 'docker']):
            business_domains['infrastructure'].append(item)
    
    # Générer des actions spécifiques
    action_plan = {
        'sprint_1_critical': _generate_sprint_actions(critical_files, 'critical'),
        'sprint_2_high_impact': _generate_sprint_actions(high_impact_files, 'high'),
        'business_domains': {
            domain: _analyze_domain_priority(files)
            for domain, files in business_domains.items() if files
        },
        'implementation_roadmap': _create_implementation_roadmap(detailed),
        'roi_impact_analysis': _calculate_roi_impact(data)
    }
    
    return action_plan

def _generate_sprint_actions(files: List[Dict], priority_level: str) -> Dict:
    """Générer des actions de sprint spécifiques"""    
    if not files:
        return {}
    
    # Trier par score de priorité
    sorted_files = sorted(files, key=lambda x: x['priority_score'], reverse=True)
    
    actions = []
    total_effort = 0
    
    for file_item in sorted_files:
        # Estimer l'effort basé sur les gaps
        effort_days = _estimate_implementation_effort(file_item)
        total_effort += effort_days
        
        action = {
            'file': file_item['file_path'],
            'priority_score': file_item['priority_score'],
            'business_impact': file_item['business_impact'],
            'implementation_percentage': file_item['implementation_percentage'],
            'gaps': {
                'todos': file_item['todo_count'],
                'empty_methods': file_item['empty_methods'],
                'not_implemented': file_item['not_implemented_errors']
            },
            'estimated_effort_days': effort_days,
            'critical_methods': file_item['critical_methods'][:3],  # Top 3
            'external_apis': file_item['external_apis'][:3],  # Top 3
            'business_rationale': _generate_business_rationale(file_item),
            'success_criteria': _generate_success_criteria(file_item)
        }
        actions.append(action)
    
    return {
        'priority_level': priority_level,
        'total_files': len(files),
        'estimated_total_effort_days': total_effort,
        'actions': actions
    }

def _analyze_domain_priority(files: List[Dict]) -> Dict:
    """Analyser la priorité d'un domaine métier"""    
    if not files:
        return {}
    
    total_files = len(files)
    avg_priority = sum(f['priority_score'] for f in files) / total_files
    total_gaps = sum(f['todo_count'] + f['empty_methods'] + f['not_implemented_errors'] for f in files)
    avg_implementation = sum(f['implementation_percentage'] for f in files) / total_files
    
    # Identifier le fichier le plus critique
    most_critical = max(files, key=lambda x: x['priority_score'])
    
    return {
        'total_files': total_files,
        'average_priority_score': round(avg_priority, 1),
        'total_implementation_gaps': total_gaps,
        'average_implementation_percentage': round(avg_implementation, 1),
        'most_critical_file': {
            'path': most_critical['file_path'],
            'score': most_critical['priority_score'],
            'rationale': _generate_business_rationale(most_critical)
        },
        'business_impact_assessment': _assess_domain_business_impact(files)
    }

def _estimate_implementation_effort(file_item: Dict) -> float:
    """Estimer l'effort d'implémentation en jours"""    
    # Facteurs d'effort
    base_effort = 0.5  # Minimum 0.5 jour par fichier
    
    # Effort basé sur les gaps
    todo_effort = file_item['todo_count'] * 0.1  # 0.1 jour par TODO
    empty_method_effort = file_item['empty_methods'] * 0.3  # 0.3 jour par méthode vide
    not_impl_effort = file_item['not_implemented_errors'] * 0.5  # 0.5 jour par NotImplemented
    
    # Multiplicateur de complexité
    complexity_multiplier = 1.0
    if file_item['external_apis']:
        complexity_multiplier += len(file_item['external_apis']) * 0.2
    if file_item['critical_methods']:
        complexity_multiplier += len(file_item['critical_methods']) * 0.1
    
    # Multiplicateur d'impact business
    impact_multiplier = {
        'critical': 1.5,
        'high': 1.2,
        'medium': 1.0,
        'low': 0.8,
        'minimal': 0.5
    }.get(file_item['business_impact'], 1.0)
    
    total_effort = (base_effort + todo_effort + empty_method_effort + not_impl_effort) * complexity_multiplier * impact_multiplier
    
    return round(total_effort, 1)

def _generate_business_rationale(file_item: Dict) -> str:
    """Générer la justification business pour un fichier"""    
    file_path = file_item['file_path'].lower()
    impact = file_item['business_impact']
    
    if 'platform' in file_path and 'mastodon' in file_path:
        return "Intégration plateforme Mastodon critique pour expansion multi-réseaux sociaux"
    elif 'ai_engine' in file_path:
        return "Moteur IA central - cœur de l'intelligence artificielle de la plateforme"
    elif 'monetization' in file_path:
        return "Système de monétisation - génération directe de revenus"
    elif 'crawler' in file_path:
        return "Collecte de données automatisée - alimenter les analyses IA"
    elif 'security' in file_path:
        return "Protection et conformité - critiques pour confiance utilisateurs"
    elif 'platform' in file_path:
        return "Architecture multi-plateforme - évolutivité business"
    elif impact == 'critical':
        return "Composant critique pour fonctionnalité business core"
    elif impact == 'high':
        return "Fonctionnalité à fort impact sur valeur ajoutée business"
    else:
        return "Support aux fonctionnalités principales"

def _generate_success_criteria(file_item: Dict) -> List[str]:
    """Générer les critères de succès pour un fichier"""    
    criteria = []
    file_path = file_item['file_path'].lower()
    
    # Critères génériques
    criteria.append(f"100% des TODOs implémentés ({file_item['todo_count']} items)")
    
    if file_item['empty_methods'] > 0:
        criteria.append(f"Toutes les méthodes vides complétées ({file_item['empty_methods']} méthodes)")
    
    # Critères spécifiques par type
    if 'platform' in file_path:
        criteria.append("Connexion API fonctionnelle avec authentification")
        criteria.append("Tests d'intégration passants avec plateforme réelle")
    elif 'ai_engine' in file_path:
        criteria.append("Algorithmes IA optimisés et testés")
        criteria.append("Performance < 2s pour requêtes standards")
    elif 'crawler' in file_path:
        criteria.append("Collecte de données sans erreurs sur 24h")
        criteria.append("Respect des limites de taux API")
    elif 'monetization' in file_path:
        criteria.append("Calculs de revenus précis et vérifiés")
        criteria.append("Intégration avec systèmes de paiement")
    
    # Critères techniques
    if file_item['external_apis']:
        criteria.append("Gestion d'erreurs API robuste avec retry")
    
    criteria.append("Tests unitaires avec 80%+ coverage")
    
    return criteria

def _assess_domain_business_impact(files: List[Dict]) -> str:
    """Évaluer l'impact business d'un domaine"""    
    if not files:
        return "Impact minimal"
    
    avg_priority = sum(f['priority_score'] for f in files) / len(files)
    
    if avg_priority >= 60:
        return "Impact critique - Bloquant pour fonctionnalités core business"
    elif avg_priority >= 50:
        return "Impact élevé - Fonctionnalités business importantes"
    elif avg_priority >= 40:
        return "Impact modéré - Support aux fonctionnalités principales"
    elif avg_priority >= 30:
        return "Impact faible - Améliorations et optimisations"
    else:
        return "Impact minimal - Utilitaires et maintenance"

def _create_implementation_roadmap(detailed: List[Dict]) -> Dict:
    """Créer une roadmap d'implémentation"""    
    # Classifier par phases
    phases = {
        'phase_1_foundations': [],  # Critical files
        'phase_2_business_features': [],  # High impact files
        'phase_3_enhancements': [],  # Medium/Low impact files
        'phase_4_optimization': []  # Minimal impact files
    }
    
    for item in detailed:
        impact = item['business_impact']
        if impact == 'critical':
            phases['phase_1_foundations'].append(item)
        elif impact == 'high':
            phases['phase_2_business_features'].append(item)
        elif impact in ['medium', 'low']:
            phases['phase_3_enhancements'].append(item)
        else:
            phases['phase_4_optimization'].append(item)
    
    roadmap = {}
    for phase, files in phases.items():
        if files:
            total_effort = sum(_estimate_implementation_effort(f) for f in files)
            roadmap[phase] = {
                'total_files': len(files),
                'estimated_effort_days': round(total_effort, 1),
                'estimated_weeks': round(total_effort / 5, 1),  # 5 jours par semaine
                'top_files': sorted(files, key=lambda x: x['priority_score'], reverse=True)[:5]
            }
    
    return roadmap

def _calculate_roi_impact(data: Dict) -> Dict:
    """Calculer l'impact ROI de l'implémentation"""    
    if not data or 'summary' not in data:
        return {}
    
    stats = data['summary']['statistics']
    
    # Métriques de base
    total_files = stats['total_files_with_gaps']
    total_gaps = stats['total_implementation_gaps']
    
    # Estimation des bénéfices
    critical_files = data['summary']['by_business_impact'].get('critical', {}).get('count', 0)
    high_files = data['summary']['by_business_impact'].get('high', {}).get('count', 0)
    
    # Estimation d'effort total
    all_files = data['detailed_analysis']
    total_effort_days = sum(_estimate_implementation_effort(f) for f in all_files)
    
    return {
        'current_completion_rate': round(((5908 - total_files) / 5908) * 100, 1),
        'remaining_implementation_effort_days': round(total_effort_days, 1),
        'estimated_weeks_to_completion': round(total_effort_days / 5, 1),
        'business_critical_files_percentage': round((critical_files / total_files) * 100, 1),
        'high_impact_business_files_percentage': round((high_files / total_files) * 100, 1),
        'expected_business_value': {
            'time_to_market_acceleration': "4-6 semaines",
            'production_readiness': "100% fonctionnalités core business",
            'platform_coverage': "Multi-plateforme (Spotify, YouTube, Instagram, etc.)",
            'revenue_generation': "Monétisation et licensing opérationnels",
            'user_protection': "Sécurité et protection de contenu actives"
        }
    }

def main():
    """Générer le rapport d'actions business"""    print("🎯 Génération des priorités business actionables...")
    
    # Charger les données
    data = load_analysis_data()
    if not data:
        print("❌ Données d'analyse non trouvées")
        return
    
    # Extraire les actions business
    actions = extract_critical_business_actions(data)
    
    # Sauvegarder le rapport d'actions
    output_file = "business_actionable_priorities.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(actions, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rapport d'actions sauvegardé: {output_file}")
    
    # Afficher le résumé
    if 'sprint_1_critical' in actions:
        critical = actions['sprint_1_critical']
        print(f"🔴 Actions critiques: {critical['total_files']} fichiers, {critical['estimated_total_effort_days']} jours")
    
    if 'sprint_2_high_impact' in actions:
        high = actions['sprint_2_high_impact']
        print(f"🟠 Actions high-impact: {high['total_files']} fichiers, {high['estimated_total_effort_days']} jours")
    
    if 'roi_impact_analysis' in actions:
        roi = actions['roi_impact_analysis']
        print(f"📊 Effort total estimé: {roi['remaining_implementation_effort_days']} jours ({roi['estimated_weeks_to_completion']} semaines)")

if __name__ == "__main__":
    main()