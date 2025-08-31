#!/usr/bin/env python3
"""
 TODO Business Impact Analyzer - AINFLUE Project
Author: Fahed Mlaiel <mlaiel@live.de>
Copyright (c) 2025 Fahed Mlaiel. All rights reserved.

Analyser intelligent pour scanner et prioriser les implémentations par impact métier.
Catégorise le code critique vs optionnel, business vs utilitaires, APIs externes vs logique interne.
"""

import os
import re
import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import argparse
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BusinessImpact(Enum):
    """Niveaux d'impact business pour la priorisation"""
    CRITICAL = "critical"          # Bloquant production - fonctionnalités core métier
    HIGH = "high"                 # Impact fort sur fonctionnalités business
    MEDIUM = "medium"             # Fonctionnalités importantes mais non bloquantes
    LOW = "low"                   # Utilitaires et améliorations
    MINIMAL = "minimal"           # Tests, documentation, configs


class CodeType(Enum):
    """Types de code identifiés"""
    BUSINESS_CORE = "business_core"        # Logique métier centrale
    AI_AGENTS = "ai_agents"               # Agents IA spécialisés
    API_EXTERNAL = "api_external"         # APIs et interfaces externes
    CRAWLERS = "crawlers"                 # Collecteurs de données
    SECURITY = "security"                 # Sécurité et protection
    INFRASTRUCTURE = "infrastructure"      # Infrastructure et configuration
    UTILITIES = "utilities"               # Utilitaires génériques
    TESTS = "tests"                       # Tests et validation
    DOCS = "docs"                         # Documentation


@dataclass
class TodoAnalysis:
    """Analyse détaillée d'un fichier avec TODOs"""
    file_path: str
    code_type: CodeType
    business_impact: BusinessImpact
    todo_count: int
    empty_methods: int
    not_implemented_errors: int
    total_lines: int
    implementation_percentage: float
    critical_methods: List[str]
    external_apis: List[str]
    dependencies: List[str]
    complexity_score: float
    priority_score: float


class TodoBusinessImpactAnalyzer:
    """Analyseur intelligent des TODOs par impact métier"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.analysis_results: List[TodoAnalysis] = []
        
        # Patterns pour identifier les types de code
        self.business_patterns = {
            CodeType.BUSINESS_CORE: [
                "business_logic", "core", "main.py", "config.py", "licensing", 
                "monetization", "revenue", "billing", "payment"
            ],
            CodeType.AI_AGENTS: [
                "ai_agents", "agents", "fingerprinting", "content_strategist", 
                "collaboration_matcher", "music_producer", "audience_developer"
            ],
            CodeType.API_EXTERNAL: [
                "api", "endpoints", "routes", "external", "integrations", 
                "platforms", "spotify", "youtube", "instagram", "tiktok"
            ],
            CodeType.CRAWLERS: [
                "crawlers", "scrapers", "data_collection", "platform_crawler"
            ],
            CodeType.SECURITY: [
                "security", "protection", "auth", "encryption", "fingerprinting",
                "rights_management", "copyright", "dmca"
            ],
            CodeType.INFRASTRUCTURE: [
                "infrastructure", "monitoring", "docker", "k8s", "deployment",
                "database", "cache", "redis", "postgres"
            ],
            CodeType.UTILITIES: [
                "utils", "helpers", "tools", "common", "shared"
            ],
            CodeType.TESTS: [
                "test", "tests", "conftest", "pytest"
            ],
            CodeType.DOCS: [
                "docs", "documentation", "examples", "demo"
            ]
        }
        
        # Patterns d'APIs externes critiques
        self.external_api_patterns = [
            "spotify", "youtube", "instagram", "tiktok", "facebook",
            "twitter", "linkedin", "api_client", "requests", "aiohttp"
        ]
        
        # Méthodes critiques business
        self.critical_business_methods = [
            "process", "execute", "analyze", "detect", "generate", "create",
            "monetize", "protect", "fingerprint", "match", "recommend"
        ]

    def analyze_file(self, file_path: Path) -> Optional[TodoAnalysis]:
        """Analyser un fichier Python pour les TODOs et impact business"""



        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Compter les patterns TODO
            todo_count = len(re.findall(r'TODO|todo|FIXME|fixme', content, re.IGNORECASE))
            empty_methods = len(re.findall(r'def\s+\w+.*?:\s*pass\s*$', content, re.MULTILINE))
            not_implemented_errors = len(re.findall(r'raise\s+NotImplementedError', content))
            
            # Analyser l'AST pour plus de détails
            try:
                tree = ast.parse(content)
                critical_methods = self._find_critical_methods(tree)
                external_apis = self._find_external_apis(content)
                dependencies = self._find_dependencies(tree)
            except SyntaxError:
                critical_methods = []
                external_apis = []
                dependencies = []
            
            # Calculer les métriques
            total_lines = len(content.splitlines())
            implementation_gaps = todo_count + empty_methods + not_implemented_errors
            implementation_percentage = max(0, 100 - (implementation_gaps / max(total_lines, 1)) * 100)
            
            # Déterminer le type de code et l'impact business
            code_type = self._determine_code_type(file_path)
            business_impact = self._determine_business_impact(file_path, code_type, critical_methods, external_apis)
            
            # Calculer les scores de complexité et priorité
            complexity_score = self._calculate_complexity_score(
                total_lines, len(critical_methods), len(external_apis), len(dependencies)
            )
            priority_score = self._calculate_priority_score(
                business_impact, implementation_percentage, complexity_score, todo_count
            )
            
            return TodoAnalysis(
                file_path=str(file_path.relative_to(self.project_root)),
                code_type=code_type,
                business_impact=business_impact,
                todo_count=todo_count,
                empty_methods=empty_methods,
                not_implemented_errors=not_implemented_errors,
                total_lines=total_lines,
                implementation_percentage=implementation_percentage,
                critical_methods=critical_methods,
                external_apis=external_apis,
                dependencies=dependencies,
                complexity_score=complexity_score,
                priority_score=priority_score
            )
            
        except Exception as e:
            logger.warning(f"Erreur lors de l'analyse de {file_path}: {e}")
            return None

    def _determine_code_type(self, file_path: Path) -> CodeType:
        """Déterminer le type de code basé sur le chemin et contenu"""
        path_str = str(file_path).lower()
        
        for code_type, patterns in self.business_patterns.items():
            if any(pattern in path_str for pattern in patterns):
                return code_type
        
        return CodeType.UTILITIES

    def _determine_business_impact(self, file_path: Path, code_type: CodeType, 
                                  critical_methods: List[str], external_apis: List[str]) -> BusinessImpact:
        """Déterminer l'impact business du fichier"""
        path_str = str(file_path).lower()
        
        # Impact critique pour les modules core business
        if code_type == CodeType.BUSINESS_CORE or "main.py" in path_str or "core" in path_str:
            return BusinessImpact.CRITICAL
        
        # Impact élevé pour les agents IA et APIs externes
        if code_type in [CodeType.AI_AGENTS, CodeType.API_EXTERNAL] or external_apis:
            return BusinessImpact.HIGH
        
        # Impact élevé pour la sécurité et les crawlers avec APIs
        if code_type in [CodeType.SECURITY, CodeType.CRAWLERS] and external_apis:
            return BusinessImpact.HIGH
        
        # Impact moyen pour les crawlers et sécurité sans APIs
        if code_type in [CodeType.CRAWLERS, CodeType.SECURITY]:
            return BusinessImpact.MEDIUM
        
        # Impact faible pour l'infrastructure et utilitaires
        if code_type in [CodeType.INFRASTRUCTURE, CodeType.UTILITIES]:
            return BusinessImpact.LOW
        
        # Impact minimal pour les tests et docs
        if code_type in [CodeType.TESTS, CodeType.DOCS]:
            return BusinessImpact.MINIMAL
        
        # Par défaut, impact moyen
        return BusinessImpact.MEDIUM

    def _find_critical_methods(self, tree: ast.AST) -> List[str]:
        """Identifier les méthodes critiques business"""
        critical_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                method_name = node.name.lower()
                if any(pattern in method_name for pattern in self.critical_business_methods):
                    critical_methods.append(node.name)
        
        return critical_methods

    def _find_external_apis(self, content: str) -> List[str]:
        """Identifier les APIs externes utilisées"""
        external_apis = []
        content_lower = content.lower()
        
        for pattern in self.external_api_patterns:
            if pattern in content_lower:
                external_apis.append(pattern)
        
        return list(set(external_apis))

    def _find_dependencies(self, tree: ast.AST) -> List[str]:
        """Identifier les dépendances importantes"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
        
        return list(set(dependencies))

    def _calculate_complexity_score(self, total_lines: int, critical_methods: int, 
                                   external_apis: int, dependencies: int) -> float:
        """Calculer le score de complexité (0-100)"""
        line_score = min(50, total_lines / 20)  # Max 50 points pour les lignes
        method_score = critical_methods * 10   # 10 points par méthode critique
        api_score = external_apis * 15         # 15 points par API externe
        dep_score = min(25, dependencies * 2)  # Max 25 points pour les dépendances
        
        return min(100, line_score + method_score + api_score + dep_score)

    def _calculate_priority_score(self, business_impact: BusinessImpact, 
                                 implementation_percentage: float, complexity_score: float, 
                                 todo_count: int) -> float:
        """Calculer le score de priorité (0-100)"""
        # Poids par impact business
        impact_weights = {
            BusinessImpact.CRITICAL: 40,
            BusinessImpact.HIGH: 30,
            BusinessImpact.MEDIUM: 20,
            BusinessImpact.LOW: 10,
            BusinessImpact.MINIMAL: 5
        }
        
        impact_score = impact_weights[business_impact]
        
        # Score basé sur l'incomplétude (plus c'est incomplet, plus c'est prioritaire)
        incompleteness_score = (100 - implementation_percentage) * 0.3
        
        # Score de complexité normalisé
        complexity_normalized = complexity_score * 0.2
        
        # Boost pour les nombreux TODOs
        todo_boost = min(10, todo_count * 2)
        
        return min(100, impact_score + incompleteness_score + complexity_normalized + todo_boost)

    def scan_repository(self) -> None:
        """Scanner tout le repository pour les TODOs"""
        logger.info(f" Scanning repository: {self.project_root}")
        
        python_files = list(self.project_root.rglob("*.py"))
        logger.info(f" Found {len(python_files)} Python files")
        
        for file_path in python_files:
            # Ignorer certains fichiers
            if any(skip in str(file_path) for skip in ['.git', '__pycache__', '.pytest_cache']):
                continue
                
            analysis = self.analyze_file(file_path)
            if analysis and (analysis.todo_count > 0 or analysis.empty_methods > 0 or analysis.not_implemented_errors > 0):
                self.analysis_results.append(analysis)
        
        logger.info(f" Analyzed {len(self.analysis_results)} files with implementation gaps")

    def generate_summary_report(self) -> Dict:
        """Générer un rapport de synthèse"""
        if not self.analysis_results:
            return {}
        
        # Statistiques générales
        total_files = len(self.analysis_results)
        total_todos = sum(a.todo_count for a in self.analysis_results)
        total_empty_methods = sum(a.empty_methods for a in self.analysis_results)
        total_not_implemented = sum(a.not_implemented_errors for a in self.analysis_results)
        
        # Répartition par type de code
        by_code_type = defaultdict(list)
        for analysis in self.analysis_results:
            by_code_type[analysis.code_type].append(analysis)
        
        # Répartition par impact business
        by_business_impact = defaultdict(list)
        for analysis in self.analysis_results:
            by_business_impact[analysis.business_impact].append(analysis)
        
        # Top priorités
        top_priority = sorted(self.analysis_results, key=lambda x: x.priority_score, reverse=True)[:20]
        
        # Critiques avec implémentation faible
        critical_low_impl = [
            a for a in self.analysis_results 
            if a.business_impact == BusinessImpact.CRITICAL and a.implementation_percentage < 50
        ]
        
        # Convertir les enums pour JSON
        top_priority_json = []
        for analysis in top_priority:
            analysis_dict = asdict(analysis)
            analysis_dict['code_type'] = analysis.code_type.value
            analysis_dict['business_impact'] = analysis.business_impact.value
            top_priority_json.append(analysis_dict)
        
        critical_low_impl_json = []
        for analysis in critical_low_impl:
            analysis_dict = asdict(analysis)
            analysis_dict['code_type'] = analysis.code_type.value
            analysis_dict['business_impact'] = analysis.business_impact.value
            critical_low_impl_json.append(analysis_dict)
        
        return {
            "scan_date": datetime.now().isoformat(),
            "statistics": {
                "total_files_with_gaps": total_files,
                "total_todos": total_todos,
                "total_empty_methods": total_empty_methods,
                "total_not_implemented": total_not_implemented,
                "total_implementation_gaps": total_todos + total_empty_methods + total_not_implemented
            },
            "by_code_type": {
                code_type.value: {
                    "count": len(analyses),
                    "avg_priority": sum(a.priority_score for a in analyses) / len(analyses) if analyses else 0,
                    "avg_implementation": sum(a.implementation_percentage for a in analyses) / len(analyses) if analyses else 0
                }
                for code_type, analyses in by_code_type.items()
            },
            "by_business_impact": {
                impact.value: {
                    "count": len(analyses),
                    "avg_priority": sum(a.priority_score for a in analyses) / len(analyses) if analyses else 0,
                    "total_gaps": sum(a.todo_count + a.empty_methods + a.not_implemented_errors for a in analyses)
                }
                for impact, analyses in by_business_impact.items()
            },
            "top_priorities": top_priority_json,
            "critical_low_implementation": critical_low_impl_json
        }

    def save_detailed_report(self, output_file: str = "todo_business_impact_analysis.json") -> None:
        """Sauvegarder le rapport détaillé"""
        # Convertir les enums en strings pour la sérialisation JSON
        detailed_analysis = []
        for analysis in self.analysis_results:
            analysis_dict = asdict(analysis)
            analysis_dict['code_type'] = analysis.code_type.value
            analysis_dict['business_impact'] = analysis.business_impact.value
            detailed_analysis.append(analysis_dict)
        
        report = {
            "summary": self.generate_summary_report(),
            "detailed_analysis": detailed_analysis
        }
        
        output_path = self.project_root / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f" Rapport détaillé sauvegardé: {output_path}")

    def generate_markdown_report(self) -> str:
        """Générer un rapport Markdown lisible"""
        summary = self.generate_summary_report()
        
        if not summary:
            return "#  Aucune analyse disponible\n\nAucun fichier avec des gaps d'implémentation trouvé."
        
        # En-tête du rapport
        report = f"""#  ANALYSE BUSINESS IMPACT - IMPLÉMENTATIONS TODO

**Date d'analyse**: {summary['scan_date'][:19]}  
**Repository**: Ainflue IA Influencer Agent Platform

---

##  STATISTIQUES GÉNÉRALES

| Métrique | Valeur |
|----------|--------|
| **Fichiers avec gaps** | {summary['statistics']['total_files_with_gaps']:,} |
| **TODOs totaux** | {summary['statistics']['total_todos']:,} |
| **Méthodes vides** | {summary['statistics']['total_empty_methods']:,} |
| **NotImplementedError** | {summary['statistics']['total_not_implemented']:,} |
| ** TOTAL GAPS** | **{summary['statistics']['total_implementation_gaps']:,}** |

---

##  RÉPARTITION PAR IMPACT BUSINESS

"""
        
        # Répartition par impact business
        impact_order = [BusinessImpact.CRITICAL, BusinessImpact.HIGH, BusinessImpact.MEDIUM, BusinessImpact.LOW, BusinessImpact.MINIMAL]
        impact_icons = {
            BusinessImpact.CRITICAL: "",
            BusinessImpact.HIGH: "🟠", 
            BusinessImpact.MEDIUM: "🟡",
            BusinessImpact.LOW: "",
            BusinessImpact.MINIMAL: ""
        }
        
        for impact in impact_order:
            if impact.value in summary['by_business_impact']:
                data = summary['by_business_impact'][impact.value]
                report += f"""### {impact_icons[impact]} **{impact.value.upper()}**
- **Fichiers**: {data['count']}
- **Priorité moyenne**: {data['avg_priority']:.1f}/100
- **Gaps totaux**: {data['total_gaps']}

"""
        
        # Répartition par type de code
        report += """---

##  RÉPARTITION PAR TYPE DE CODE

"""
        
        type_icons = {
            CodeType.BUSINESS_CORE: "",
            CodeType.AI_AGENTS: "🤖",
            CodeType.API_EXTERNAL: "",
            CodeType.CRAWLERS: "",
            CodeType.SECURITY: "",
            CodeType.INFRASTRUCTURE: "",
            CodeType.UTILITIES: "",
            CodeType.TESTS: "🧪",
            CodeType.DOCS: ""
        }
        
        for code_type_str, data in summary['by_code_type'].items():
            code_type = CodeType(code_type_str)
            icon = type_icons.get(code_type, "")
            report += f"""### {icon} **{code_type_str.upper()}**
- **Fichiers**: {data['count']}
- **Priorité moyenne**: {data['avg_priority']:.1f}/100
- **Implémentation moyenne**: {data['avg_implementation']:.1f}%

"""
        
        # Top priorités critiques
        report += """---

##  TOP PRIORITÉS CRITIQUES

"""
        
        critical_files = [a for a in summary['top_priorities'] if a['business_impact'] == 'critical'][:10]
        
        if critical_files:
            report += "| Fichier | Score | Implem. % | TODOs | Type |\n"
            report += "|---------|-------|-----------|-------|------|\n"
            
            for file_analysis in critical_files:
                report += f"| `{file_analysis['file_path']}` | {file_analysis['priority_score']:.1f} | {file_analysis['implementation_percentage']:.1f}% | {file_analysis['todo_count']} | {file_analysis['code_type']} |\n"
        else:
            report += "*Aucun fichier critique avec faible implémentation trouvé.*\n"
        
        # Recommandations d'actions
        report += """

---

##  RECOMMANDATIONS D'ACTIONS

###  **ACTIONS CRITIQUES** (Impact Business CRITICAL)
"""
        
        critical_files_all = [a for a in summary['critical_low_implementation']]
        if critical_files_all:
            for i, file_analysis in enumerate(critical_files_all[:5], 1):
                report += f"""
{i}. **`{file_analysis['file_path']}`**
   - **Impact**: {file_analysis['business_impact'].upper()}
   - **Implémentation**: {file_analysis['implementation_percentage']:.1f}%
   - **TODOs**: {file_analysis['todo_count']} 
   - **Méthodes critiques**: {', '.join(file_analysis['critical_methods'][:3])}
   - **APIs externes**: {', '.join(file_analysis['external_apis'][:3])}
"""
        else:
            report += "\n *Tous les fichiers critiques ont une implémentation acceptable.*\n"
        
        # Actions par type
        report += """
### 🟠 **ACTIONS PAR DOMAINE**

"""
        
        domain_priorities = {
            'ai_agents': "🤖 **Agents IA**: Finaliser les agents de fingerprinting, monétisation et collaboration",
            'business_core': " **Business Logic**: Compléter les modules de licensing et revenue management", 
            'api_external': " **APIs Externes**: Implémenter les connecteurs Spotify, YouTube, Instagram",
            'crawlers': " **Crawlers**: Développer les crawlers de contenu avec gestion des APIs",
            'security': " **Sécurité**: Finaliser la protection de contenu et gestion des droits"
        }
        
        for domain, description in domain_priorities.items():
            if domain in summary['by_code_type'] and summary['by_code_type'][domain]['count'] > 0:
                data = summary['by_code_type'][domain]
                report += f"- {description}\n  - Fichiers: {data['count']}, Priorité: {data['avg_priority']:.1f}/100\n\n"
        
        report += """---

##  PROCHAINES ÉTAPES

1. **Phase 1 - Critique**: Compléter tous les fichiers CRITICAL (impact business bloquant)
2. **Phase 2 - Business**: Finaliser les modules HIGH impact (fonctionnalités business)
3. **Phase 3 - Support**: Développer les modules MEDIUM (fonctionnalités support)
4. **Phase 4 - Optimisation**: Améliorer les modules LOW/MINIMAL

---

* Rapport généré automatiquement par TODO Business Impact Analyzer*  
* Pour une analyse détaillée, consultez le fichier JSON complet*
"""



        
        return report


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(description=" TODO Business Impact Analyzer for Ainflue")
    parser.add_argument("--project-root", default=".", help="Chemin vers la racine du projet")
    parser.add_argument("--output-json", default="todo_business_impact_analysis.json", 
                       help="Fichier de sortie JSON")
    parser.add_argument("--output-md", default="TODO_BUSINESS_IMPACT_ANALYSIS.md",
                       help="Fichier de sortie Markdown")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbose")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialiser l'analyseur
    analyzer = TodoBusinessImpactAnalyzer(args.project_root)
    
    # Scanner le repository
    analyzer.scan_repository()
    
    # Générer les rapports
    analyzer.save_detailed_report(args.output_json)
    
    # Sauvegarder le rapport Markdown
    markdown_report = analyzer.generate_markdown_report()
    output_md_path = Path(args.project_root) / args.output_md
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.write(markdown_report)
    
    logger.info(f" Rapport Markdown sauvegardé: {output_md_path}")
    
    # Afficher le résumé
    summary = analyzer.generate_summary_report()
    if summary:
        stats = summary['statistics']
        print(f"\n RÉSUMÉ DE L'ANALYSE:")
        print(f"    Fichiers avec gaps: {stats['total_files_with_gaps']:,}")
        print(f"    Total gaps: {stats['total_implementation_gaps']:,}")
        print(f"    Rapports générés: {args.output_json}, {args.output_md}")
    else:
        print("\n Aucun gap d'implémentation trouvé!")


if __name__ == "__main__":
    main()