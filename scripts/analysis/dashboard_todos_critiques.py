#!/usr/bin/env python3
"""🎯 DASHBOARD TODOs CRITIQUES - MONITORING TEMPS RÉEL
Script de surveillance des TODOs par impact métier pour priorisation

Usage: python dashboard_todos_critiques.py
Output: Rapport priorité business + fichiers critiques
"""
import json
import os
from pathlib import Path

def load_audit_report():
    """Charge le rapport d'audit existant"""
    report_file = "AUDIT_CODE_BUSINESS_IMPACT_REPORT.json"
    
    if not os.path.exists(report_file):
        print(f"❌ Rapport d'audit non trouvé: {report_file}")
        print("🔄 Exécutez d'abord: python AUDIT_CODE_BUSINESS_IMPACT.py")
        return None
        
    with open(report_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_critical_todos(report):
    """Extrait les TODOs les plus critiques pour action immédiate"""
    
    critical_files = []
    
    # Analyser les fichiers critiques avec issues
    for file_analysis in report.get('critical_issues_analysis', []):
        if file_analysis['business_value_score'] >= 90:  # Ultra-critique
            critical_files.append({
                'file': file_analysis['file_path'],
                'score': file_analysis['business_value_score'],
                'impact': file_analysis['business_impact'],
                'type': file_analysis['code_type'],
                'issues': file_analysis['issue_count'],
                'revenue_impact': file_analysis['revenue_impact']
            })
    
    return sorted(critical_files, key=lambda x: (x['score'], x['issues']), reverse=True)

def display_dashboard(report):
    """Affiche le dashboard de monitoring"""
    
    print("=" * 80)
    print("🚨 DASHBOARD TODOs CRITIQUES - MONITORING TEMPS RÉEL")
    print("=" * 80)
    
    # Résumé global
    summary = report['summary']
    print(f"\n📊 ÉTAT GLOBAL:")
    print(f"   📁 Fichiers analysés: {summary['total_files_analyzed']:,}")
    print(f"   ⚠️  Issues totales: {summary['total_issues_found']:,}")
    print(f"   🔴 Fichiers critiques avec issues: {summary['critical_files_with_issues']:,}")
    
    # Impact revenus
    revenue = report['revenue_impact_summary']
    print(f"\n💰 IMPACT REVENUS:")
    print(f"   🔴 Modules critiques: {revenue['critical_modules']['estimated_hourly_revenue_impact']}/heure")
    print(f"   📈 Valeur plateforme estimée: {revenue['total_estimated_platform_value']}")
    
    # TOP 10 fichiers à traiter en urgence
    critical_todos = extract_critical_todos(report)
    
    print(f"\n🎯 TOP 10 FICHIERS ULTRA-CRITIQUES À TRAITER:")
    print("-" * 80)
    
    for i, file_info in enumerate(critical_todos[:10], 1):
        print(f"{i:2d}. 📄 {file_info['file']}")
        print(f"    💯 Score métier: {file_info['score']}/100")
        print(f"    🏷️  Type: {file_info['type']} | Impact: {file_info['impact']}")
        print(f"    ⚠️  Issues: {file_info['issues']} | 💰 {file_info['revenue_impact']}")
        print()
    
    # Distribution par modules business
    print("📊 DISTRIBUTION MODULES BUSINESS:")
    print("-" * 50)
    
    business_dist = report['business_impact_distribution']
    for impact, data in business_dist.items():
        if impact in ['CRITIQUE', 'ÉLEVÉ']:  # Focus sur business critique
            percentage = data['percentage']
            files_with_issues = data['files_with_issues']
            total_files = data['file_count']
            issue_rate = (files_with_issues / total_files * 100) if total_files > 0 else 0
            
            print(f"🔴 {impact}: {total_files:,} fichiers ({percentage}%)")
            print(f"   ⚠️  {files_with_issues:,} avec issues ({issue_rate:.1f}%)")
            print()
    
    # Top recommandations
    print("🎯 ACTIONS PRIORITAIRES:")
    print("-" * 50)
    
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"{i}. {rec['priority']} {rec['title']}")
        print(f"   → {rec['action']}")
        print(f"   💰 {rec['business_impact']}")
        print(f"   ⏱️  {rec['estimated_effort']}")
        print()
    
    # Quick action commands
    print("🚀 COMMANDES RAPIDES:")
    print("-" * 50)
    print("1. Lister TODOs monétisation:")
    print("   grep -r 'TODO\\|FIXME' business/commission/ monetization/")
    print()
    print("2. Compter NotImplementedError critiques:")
    print("   grep -r 'NotImplementedError\\|NotImplemented' business/ monetization/ protection/")
    print()
    print("3. Analyser fichiers vides (pass):")
    print("   grep -r '^\\s*pass\\s*$' business/ ai_agents/ | wc -l")
    print()
    print("4. Prochaine exécution complète:")
    print("   python AUDIT_CODE_BUSINESS_IMPACT.py")
    
    print("\n" + "=" * 80)
    print("📊 Dashboard généré avec succès!")
    print("🔄 Pour mise à jour: relancer le script")
    print("📧 Contact: mlaiel@live.de")
    print("=" * 80)

def generate_quick_action_list(critical_todos):
    """Génère une liste d'actions rapides pour les développeurs"""
    
    action_file = "QUICK_ACTIONS_TODOS_CRITIQUES.md"
    
    with open(action_file, 'w', encoding='utf-8') as f:
        f.write("# 🚀 ACTIONS RAPIDES - TODOs CRITIQUES\n\n")
        f.write("**Généré automatiquement** - Liste priorité business\n\n")
        
        f.write("## 🔴 URGENCE ABSOLUE (Première journée)\n\n")
        
        urgency_count = 0
        for file_info in critical_todos:
            if file_info['score'] >= 95 and file_info['issues'] >= 3:  # Ultra critique
                urgency_count += 1
                f.write(f"### {urgency_count}. {file_info['file']}\n")
                f.write(f"- **Score métier:** {file_info['score']}/100\n")
                f.write(f"- **Issues:** {file_info['issues']}\n")
                f.write(f"- **Impact:** {file_info['revenue_impact']}\n")
                f.write(f"- **Action:** Ouvrir fichier et corriger TODOs/FIXMEs\n")
                f.write(f"- **Commande:** `code {file_info['file']}`\n\n")
                
                if urgency_count >= 5:  # Limiter à 5 fichiers ultra-urgents
                    break
        
        f.write("## 🟡 IMPORTANTE (Première semaine)\n\n")
        
        important_count = 0
        for file_info in critical_todos[5:]:  # Après les 5 ultra-urgents
            if file_info['score'] >= 90:
                important_count += 1
                f.write(f"### {important_count}. {file_info['file']}\n")
                f.write(f"- **Score:** {file_info['score']}/100 | **Issues:** {file_info['issues']}\n")
                f.write(f"- **Type:** {file_info['type']}\n\n")
                
                if important_count >= 10:  # Limiter à 10 fichiers importants
                    break
        
        f.write("## 📋 COMMANDES UTILES\n\n")
        f.write("```bash\n")
        f.write("# Chercher tous les TODOs dans modules critiques\n")
        f.write("grep -r 'TODO\\|FIXME\\|XXX' business/ monetization/ protection/ ai_agents/\n\n")
        f.write("# Compter NotImplementedError\n") 
        f.write("find . -name '*.py' -exec grep -l 'NotImplementedError\\|NotImplemented' {} \\; | wc -l\n\n")
        f.write("# Analyser méthodes vides\n")
        f.write("grep -r '^\\s*pass\\s*$' business/ | head -20\n")
        f.write("```\n\n")
        f.write("---\n")
        f.write("*Généré automatiquement par dashboard_todos_critiques.py*\n")
    
    print(f"✅ Liste d'actions générée: {action_file}")

def main():
    """Fonction principale du dashboard"""
    
    # Charger le rapport d'audit
    report = load_audit_report()
    if not report:
        return
    
    # Afficher le dashboard
    display_dashboard(report)
    
    # Générer liste d'actions rapides
    critical_todos = extract_critical_todos(report)
    generate_quick_action_list(critical_todos)

if __name__ == "__main__":
    main()