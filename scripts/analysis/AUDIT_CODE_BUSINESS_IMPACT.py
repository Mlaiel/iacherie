#!/usr/bin/env python3
"""🔍 AUDIT CODE BUSINESS vs UTILITAIRES - ANALYSER IMPACT MÉTIER
Outil d'audit professionnel pour classifier et prioriser le code par impact métier

Author: Fahed Mlaiel (mlaiel@live.de)
(c) 2025 Fahed Mlaiel. All rights reserved.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import datetime

class BusinessImpact(Enum):
    """
Classification d'impact métier"""

    CRITICAL = "CRITIQUE"           # Impact direct sur revenus/core business
    HIGH = "ÉLEVÉ"                 # Important pour fonctionnalités principales
    MEDIUM = "MOYEN"               # Support aux fonctionnalités business
    LOW = "FAIBLE"                 # Infrastructure/utilitaires
    UNKNOWN = "INCONNU"            # Non classifié

class CodeType(Enum):
    """Type de code identifié"""

    BUSINESS_LOGIC = "LOGIQUE_MÉTIER"
    AI_AGENT = "AGENT_IA"
    MONETIZATION = "MONÉTISATION"
    PROTECTION = "PROTECTION"
    CRAWLER = "CRAWLER"
    API_ENDPOINT = "API_ENDPOINT"
    UTILITY = "UTILITAIRE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    TEST = "TEST"
    CONFIG = "CONFIGURATION"

@dataclass
class CodeIssue:
    """Problème de code identifié"""
    type: str  # TODO, FIXME, HACK, etc.
    line_number: int
    content: str
    severity: str

@dataclass
class FileAnalysis:
    """
Analyse d'un fichier"""
    file_path: str
    business_impact: BusinessImpact
    code_type: CodeType
    line_count: int
    issues: List[CodeIssue]
    business_value_score: int  # 1-100
    complexity_score: int      # 1-100
    revenue_impact: str        # Description impact revenus

class CodeAuditor:
    """
Auditeur de code professionnel"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.files_analyzed = 0
        self.total_issues = 0
        
        # Configuration des patterns de classification
        self.business_patterns = {
            # Modules Business Critical
            r'.*/business/.*': (BusinessImpact.CRITICAL, CodeType.BUSINESS_LOGIC),
            r'.*/monetization/.*': (BusinessImpact.CRITICAL, CodeType.MONETIZATION),
            r'.*/ai_agents/.*': (BusinessImpact.CRITICAL, CodeType.AI_AGENT),
            r'.*/protection/.*': (BusinessImpact.CRITICAL, CodeType.PROTECTION),
            r'.*/crawlers/.*': (BusinessImpact.HIGH, CodeType.CRAWLER),
            
            # APIs (impact élevé car interface business)
            r'.*/api/(?!utils).*': (BusinessImpact.HIGH, CodeType.API_ENDPOINT),
            
            # Infrastructure critique
            r'.*/security/.*': (BusinessImpact.HIGH, CodeType.INFRASTRUCTURE),
            r'.*/payment/.*': (BusinessImpact.CRITICAL, CodeType.MONETIZATION),
            
            # Utilitaires
            r'.*/utils/.*': (BusinessImpact.MEDIUM, CodeType.UTILITY),
            r'.*/api/utils/.*': (BusinessImpact.MEDIUM, CodeType.UTILITY),
            r'.*/config/.*': (BusinessImpact.LOW, CodeType.CONFIG),
            r'.*/monitoring/.*': (BusinessImpact.MEDIUM, CodeType.INFRASTRUCTURE),
            
            # Tests
            r'.*/tests?/.*': (BusinessImpact.LOW, CodeType.TEST),
            r'.*test.*\.py$': (BusinessImpact.LOW, CodeType.TEST),
        }
        
        # Patterns pour détection d'issues critiques
        self.issue_patterns = {
            r'\bTODO\b': 'TODO',
            r'\bFIXME\b': 'FIXME', 
            r'\bHACK\b': 'HACK',
            r'\bXXX\b': 'XXX',
            r'\bBUG\b': 'BUG',
            r'\bWARNING\b': 'WARNING',
            r'pass\s*$': 'EMPTY_IMPLEMENTATION',
            r'raise\s+NotImplementedError': 'NOT_IMPLEMENTED',
            r'raise\s+NotImplemented': 'NOT_IMPLEMENTED',
        }
        
    def classify_file(self, file_path: str) -> Tuple[BusinessImpact, CodeType]:
        """
Classifie un fichier selon son impact métier"""
        relative_path = file_path.replace(str(self.repo_path), '')
        
        for pattern, (impact, code_type) in self.business_patterns.items():
            if re.match(pattern, relative_path, re.IGNORECASE):
                return impact, code_type
                
        return BusinessImpact.UNKNOWN, CodeType.UTILITY
    
    def calculate_business_value_score(self, file_path: str, impact: BusinessImpact, 
                                     code_type: CodeType, content: str) -> int:
        """
Calcule un score de valeur métier (1-100)"""
        base_scores = {
            BusinessImpact.CRITICAL: 90,
            BusinessImpact.HIGH: 70,
            BusinessImpact.MEDIUM: 50,
            BusinessImpact.LOW: 20,
            BusinessImpact.UNKNOWN: 10
        }
        
        score = base_scores[impact]
        
        # Bonus pour certains types de code
        type_bonus = {
            CodeType.MONETIZATION: 20,
            CodeType.AI_AGENT: 15,
            CodeType.PROTECTION: 15,
            CodeType.BUSINESS_LOGIC: 10,
            CodeType.API_ENDPOINT: 5,
        }
        
        score += type_bonus.get(code_type, 0)
        
        # Bonus pour contenu riche
        if len(content) > 5000:  # Gros fichiers = plus de logique
            score += 5
        if 'class' in content and 'def' in content:  # Code structuré
            score += 5
            
        return min(100, score)
    
    def analyze_file_content(self, file_path: str) -> Tuple[str, List[CodeIssue], int]:
        """
Analyse le contenu d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            issues = []
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in self.issue_patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = "HIGH" if issue_type in ['BUG', 'FIXME', 'NOT_IMPLEMENTED'] else "MEDIUM"
                        issues.append(CodeIssue(
                            type=issue_type,
                            line_number=line_num,
                            content=line.strip()[:100],  # Limiter à 100 chars
                            severity=severity
                        ))
            
            complexity = self.calculate_complexity(content)
            return content, issues, complexity
            
        except Exception as e:
            print(f"Erreur lecture {file_path}: {e}")
            return "", [], 0
    
    def calculate_complexity(self, content: str) -> int:
        """Calcule un score de complexité basique"""
        if not content:
            return 0
            
        # Compteurs de complexité
        class_count = len(re.findall(r'^\s*class\s+', content, re.MULTILINE))
        function_count = len(re.findall(r'^\s*def\s+', content, re.MULTILINE))
        import_count = len(re.findall(r'^\s*(?:import|from)\s+', content, re.MULTILINE))
        lines = len(content.split('\n'))
        
        # Score basé sur la structure
        complexity = min(100, (class_count * 10 + function_count * 3 + 
                              import_count * 2 + lines // 50))
        
        return complexity
    
    def get_revenue_impact_description(self, impact: BusinessImpact, code_type: CodeType) -> str:
        """
Génère une description de l'impact sur les revenus"""
        descriptions = {
            (BusinessImpact.CRITICAL, CodeType.MONETIZATION): "Impact direct: gestion paiements/revenus créateurs",
            (BusinessImpact.CRITICAL, CodeType.AI_AGENT): "Différenciateur métier: IA unique pour créateurs",
            (BusinessImpact.CRITICAL, CodeType.PROTECTION): "Valeur core: protection contenu = rétention clients",
            (BusinessImpact.CRITICAL, CodeType.BUSINESS_LOGIC): "Logique métier centrale: cœur platform",
            (BusinessImpact.HIGH, CodeType.CRAWLER): "Acquisition données: essentiel pour services IA",
            (BusinessImpact.HIGH, CodeType.API_ENDPOINT): "Interface business: accès services payants",
            (BusinessImpact.MEDIUM, CodeType.UTILITY): "Support: optimisation expérience utilisateur",
            (BusinessImpact.LOW, CodeType.CONFIG): "Infrastructure: pas d'impact direct revenus",
            (BusinessImpact.LOW, CodeType.TEST): "Qualité: impact indirect via fiabilité",
        }
        
        key = (impact, code_type)
        return descriptions.get(key, f"Impact {impact.value.lower()}: {code_type.value.lower()}")
    
    def scan_repository(self) -> List[FileAnalysis]:
        """Scanne tout le repository"""
        print(f"🔍 Début audit repository: {self.repo_path}")
        results = []
        
        # Trouver tous les fichiers Python
        python_files = list(self.repo_path.rglob("*.py"))
        total_files = len(python_files)
        
        print(f"📁 {total_files} fichiers Python trouvés")
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"⏳ Analyse: {i}/{total_files} fichiers...")
                
            # Classifier le fichier
            impact, code_type = self.classify_file(str(file_path))
            
            # Analyser le contenu
            content, issues, complexity = self.analyze_file_content(file_path)
            
            # Calculer scores
            business_score = self.calculate_business_value_score(str(file_path), impact, code_type, content)
            revenue_impact = self.get_revenue_impact_description(impact, code_type)
            
            analysis = FileAnalysis(
                file_path=str(file_path.relative_to(self.repo_path)),
                business_impact=impact,
                code_type=code_type,
                line_count=len(content.split('\n')) if content else 0,
                issues=issues,
                business_value_score=business_score,
                complexity_score=complexity,
                revenue_impact=revenue_impact
            )
            
            results.append(analysis)
            self.files_analyzed += 1
            self.total_issues += len(issues)
        
        print(f"✅ Audit terminé: {self.files_analyzed} fichiers analysés")
        return results
    
    def generate_report(self, analyses: List[FileAnalysis]) -> Dict:
        """Génère un rapport complet d'audit"""
        
        # Statistiques globales
        total_files = len(analyses)
        total_lines = sum(a.line_count for a in analyses)
        files_with_issues = sum(1 for a in analyses if a.issues)
        
        # Groupement par impact métier
        by_impact = {}
        for impact in BusinessImpact:
            by_impact[impact.value] = [a for a in analyses if a.business_impact == impact]
        
        # Groupement par type de code
        by_type = {}
        for code_type in CodeType:
            by_type[code_type.value] = [a for a in analyses if a.code_type == code_type]
        
        # Top fichiers critiques avec issues
        critical_issues = [a for a in analyses 
                          if a.business_impact == BusinessImpact.CRITICAL and a.issues]
        critical_issues.sort(key=lambda x: len(x.issues), reverse=True)
        
        # Top fichiers par valeur métier
        top_business_value = sorted(analyses, key=lambda x: x.business_value_score, reverse=True)[:20]
        
        # Issues par type
        all_issues = [issue for a in analyses for issue in a.issues]
        issues_by_type = {}
        for issue in all_issues:
            issues_by_type[issue.type] = issues_by_type.get(issue.type, 0) + 1
        
        # Calcul impact revenus estimé
        revenue_impact_summary = self.calculate_revenue_impact_summary(analyses)
        
        report = {
            "metadata": {
                "audit_date": datetime.datetime.now().isoformat(),
                "repository_path": str(self.repo_path),
                "auditor": "AUDIT_CODE_BUSINESS_IMPACT.py v1.0",
                "author": "Fahed Mlaiel (mlaiel@live.de)"
            },
            "summary": {
                "total_files_analyzed": total_files,
                "total_lines_of_code": total_lines,
                "files_with_issues": files_with_issues,
                "total_issues_found": len(all_issues),
                "critical_files_with_issues": len(critical_issues)
            },
            "business_impact_distribution": {
                impact: {
                    "file_count": len(files),
                    "percentage": round(len(files) / total_files * 100, 1),
                    "total_lines": sum(f.line_count for f in files),
                    "files_with_issues": sum(1 for f in files if f.issues)
                }
                for impact, files in by_impact.items()
            },
            "code_type_distribution": {
                code_type: {
                    "file_count": len(files),
                    "percentage": round(len(files) / total_files * 100, 1),
                    "average_business_score": round(sum(f.business_value_score for f in files) / len(files), 1) if files else 0
                }
                for code_type, files in by_type.items()
            },
            "critical_issues_analysis": [
                {
                    "file_path": a.file_path,
                    "business_impact": a.business_impact.value,
                    "code_type": a.code_type.value,
                    "business_value_score": a.business_value_score,
                    "issue_count": len(a.issues),
                    "revenue_impact": a.revenue_impact,
                    "issues": [asdict(issue) for issue in a.issues[:5]]  # Limiter à 5 issues par fichier
                }
                for a in critical_issues[:10]  # Top 10 fichiers critiques
            ],
            "top_business_value_files": [
                {
                    "file_path": a.file_path,
                    "business_value_score": a.business_value_score,
                    "business_impact": a.business_impact.value,
                    "code_type": a.code_type.value,
                    "line_count": a.line_count,
                    "issue_count": len(a.issues),
                    "revenue_impact": a.revenue_impact
                }
                for a in top_business_value[:10]
            ],
            "issues_by_type": issues_by_type,
            "revenue_impact_summary": revenue_impact_summary,
            "recommendations": self.generate_recommendations(analyses)
        }
        
        return report
    
    def calculate_revenue_impact_summary(self, analyses: List[FileAnalysis]) -> Dict:
        """Calcule un résumé d'impact sur les revenus"""
        
        critical_files = [a for a in analyses if a.business_impact == BusinessImpact.CRITICAL]
        high_files = [a for a in analyses if a.business_impact == BusinessImpact.HIGH]
        
        # Estimation impact based on business logic from disaster recovery document
        critical_downtime_cost = len(critical_files) * 100  # €100/fichier/heure estimé
        high_downtime_cost = len(high_files) * 50           # €50/fichier/heure estimé
        
        return {
            "critical_modules": {
                "file_count": len(critical_files),
                "estimated_hourly_revenue_impact": f"€{critical_downtime_cost:,}",
                "categories": list(set(f.code_type.value for f in critical_files))
            },
            "high_priority_modules": {
                "file_count": len(high_files),
                "estimated_hourly_revenue_impact": f"€{high_downtime_cost:,}",
                "categories": list(set(f.code_type.value for f in high_files))
            },
            "total_estimated_platform_value": f"€{(critical_downtime_cost + high_downtime_cost) * 24 * 365:,}/an"
        }
    
    def generate_recommendations(self, analyses: List[FileAnalysis]) -> List[Dict]:
        """Génère des recommandations priorisées"""
        
        recommendations = []
        
        # 1. Fichiers critiques avec issues
        critical_with_issues = [a for a in analyses 
                               if a.business_impact == BusinessImpact.CRITICAL and a.issues]
        
        if critical_with_issues:
            recommendations.append({
                "priority": "🔴 URGENCE",
                "title": "Résoudre issues dans modules business critiques",
                "description": f"{len(critical_with_issues)} fichiers critiques ont des issues",
                "action": "Corriger TODOs/FIXMEs dans modules monétisation/IA/protection",
                "business_impact": "Risque dysfonctionnement revenus et services core",
                "estimated_effort": "2-5 jours",
                "files": [f.file_path for f in critical_with_issues[:5]]
            })
        
        # 2. Modules avec forte valeur métier mais faible qualité
        low_quality_high_value = [a for a in analyses 
                                 if a.business_value_score > 80 and len(a.issues) > 3]
        
        if low_quality_high_value:
            recommendations.append({
                "priority": "🟡 IMPORTANTE",
                "title": "Améliorer qualité modules haute valeur",
                "description": f"{len(low_quality_high_value)} modules haute valeur avec qualité dégradée",
                "action": "Refactoring et tests pour modules à forte valeur métier",
                "business_impact": "Optimisation ROI développement",
                "estimated_effort": "1-2 semaines",
                "files": [f.file_path for f in low_quality_high_value[:5]]
            })
        
        # 3. Code non-implémenté critique
        not_implemented = [a for a in analyses 
                          if any(issue.type == 'NOT_IMPLEMENTED' for issue in a.issues)
                          and a.business_impact in [BusinessImpact.CRITICAL, BusinessImpact.HIGH]]
        
        if not_implemented:
            recommendations.append({
                "priority": "🟠 MOYENNE",
                "title": "Compléter implémentations manquantes",
                "description": f"{len(not_implemented)} fichiers avec NotImplementedError",
                "action": "Implémenter fonctionnalités marquées NotImplemented",
                "business_impact": "Fonctionnalités non disponibles pour utilisateurs",
                "estimated_effort": "3-7 jours",
                "files": [f.file_path for f in not_implemented[:5]]
            })
        
        # 4. Optimisation architecture
        recommendations.append({
            "priority": "🔵 OPTIMISATION",
            "title": "Surveillance continue qualité code",
            "description": "Mettre en place monitoring automatique qualité",
            "action": "CI/CD avec contrôles qualité automatiques",
            "business_impact": "Prévention dégradation qualité future",
            "estimated_effort": "1 semaine",
            "files": []
        })
        
        return recommendations

def main():
    """Fonction principale d'audit"""
    
    print("🔍 AUDIT CODE BUSINESS vs UTILITAIRES - DÉMARRAGE")
    print("=" * 60)
    
    # Initialiser l'auditeur
    repo_path = "/home/runner/work/Ainflue/Ainflue"
    auditor = CodeAuditor(repo_path)
    
    # Scanner le repository
    analyses = auditor.scan_repository()
    
    # Générer le rapport
    print("\n📊 Génération du rapport d'audit...")
    report = auditor.generate_report(analyses)
    
    # Sauvegarder le rapport
    report_file = "AUDIT_CODE_BUSINESS_IMPACT_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Rapport sauvegardé: {report_file}")
    
    # Afficher résumé
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ AUDIT CODE")
    print("=" * 60)
    
    summary = report['summary']
    print(f"📁 Fichiers analysés: {summary['total_files_analyzed']:,}")
    print(f"📝 Lignes de code: {summary['total_lines_of_code']:,}")
    print(f"⚠️  Fichiers avec issues: {summary['files_with_issues']:,}")
    print(f"🔴 Issues totales: {summary['total_issues_found']:,}")
    print(f"💥 Fichiers critiques avec issues: {summary['critical_files_with_issues']:,}")
    
    print("\n📊 DISTRIBUTION IMPACT MÉTIER:")
    for impact, data in report['business_impact_distribution'].items():
        print(f"  {impact}: {data['file_count']} fichiers ({data['percentage']}%)")
    
    print("\n🎯 TOP RECOMMANDATIONS:")
    for i, rec in enumerate(report['recommendations'][:3], 1):
        print(f"  {i}. {rec['priority']} {rec['title']}")
        print(f"     → {rec['action']}")
    
    print(f"\n💰 IMPACT REVENUS ESTIMÉ:")
    revenue = report['revenue_impact_summary']
    print(f"  Modules critiques: {revenue['critical_modules']['estimated_hourly_revenue_impact']}/heure")
    print(f"  Valeur plateforme: {revenue['total_estimated_platform_value']}")
    
    print("\n🎉 AUDIT TERMINÉ AVEC SUCCÈS!")
    print(f"📄 Rapport détaillé disponible: {report_file}")

if __name__ == "__main__":
    main()