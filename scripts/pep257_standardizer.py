#!/usr/bin/env python3
"""
Script industriel de standardisation PEP257 et correction syntaxique
Projet Ainflue - Infrastructure Industrielle Ultra-Avancée
"""

import os
import re
import ast
import sys
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DocstringIssue:
    """Issue détectée dans une docstring"""
    file_path: Path
    line_number: int
    issue_type: str
    description: str
    suggestion: str


@dataclass
class SyntaxIssue:
    """Issue de syntaxe détectée"""
    file_path: Path
    line_number: int
    error_type: str
    description: str
    fixable: bool


class PEP257DocstringStandardizer:
    """Standardiseur de docstrings selon PEP257"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.issues: List[DocstringIssue] = []
        self.fixed_files: List[Path] = []
        self.errors: List[str] = []
        
    def is_pep257_compliant(self, docstring: str, context: str) -> Tuple[bool, List[str]]:
        """Vérifie la conformité PEP257 d'une docstring"""
        issues = []
        
        if not docstring:
            return False, ["Missing docstring"]
        
        lines = docstring.split('\n')
        
        # Règle PEP257: La docstring doit commencer et finir par des triple quotes
        if not (docstring.startswith('"""') or docstring.startswith("'''")):
            issues.append("Docstring should start with triple quotes")
        
        # Règle PEP257: Première ligne doit être un résumé concis
        first_line = lines[0].strip().strip('"""').strip("'''").strip()
        if not first_line:
            issues.append("First line should be a concise summary")
        elif not first_line.endswith('.'):
            issues.append("First line should end with a period")
        
        # Règle PEP257: Une ligne docstring pour les fonctions simples
        if len(lines) == 1 and context in ['function', 'method']:
            return len(issues) == 0, issues
        
        # Règle PEP257: Ligne blanche après le résumé si multilignes
        if len(lines) > 1 and lines[1].strip():
            issues.append("Blank line should follow the summary")
        
        return len(issues) == 0, issues
    
    def extract_docstrings(self, file_path: Path) -> List[Tuple[str, int, str]]:
        """Extrait toutes les docstrings d'un fichier avec leur contexte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            docstrings = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if (node.body and isinstance(node.body[0], ast.Expr) 
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0].value.value
                        docstrings.append((docstring, node.lineno, 'function'))
                
                elif isinstance(node, ast.ClassDef):
                    if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                        docstring = node.body[0].value.value
                        docstrings.append((docstring, node.lineno, 'class'))
            
            # Module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
                docstring = tree.body[0].value.value
                docstrings.append((docstring, 1, 'module'))
            
            return docstrings
            
        except Exception as e:
            self.errors.append(f"Error extracting docstrings from {file_path}: {e}")
            return []
    
    def standardize_docstring(self, docstring: str, context: str) -> str:
        """Standardise une docstring selon PEP257"""
        if not docstring:
            return '"""TODO: Add docstring"""'
        
        # Nettoyer et normaliser
        lines = docstring.strip().split('\n')
        if not lines:
            return '"""TODO: Add docstring"""'
        
        # Première ligne - résumé
        summary = lines[0].strip().strip('"""').strip("'''").strip()
        if not summary:
            summary = "TODO: Add description"
        elif not summary.endswith('.'):
            summary += '.'
        
        # Docstring d'une ligne
        if len(lines) <= 1 or all(not line.strip() for line in lines[1:]):
            return f'"""{summary}"""'
        
        # Docstring multiligne
        result_lines = [f'"""{summary}']
        
        # Ajouter ligne blanche après résumé
        result_lines.append('')
        
        # Traiter le reste des lignes
        in_content = False
        for line in lines[1:]:
            clean_line = line.strip().strip('"""').strip("'''")
            if clean_line or in_content:
                result_lines.append(clean_line)
                in_content = True
        
        result_lines.append('"""')
        return '\n'.join(result_lines)
    
    def fix_file_docstrings(self, file_path: Path) -> bool:
        """Corrige les docstrings d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Vérifier la syntaxe avant modification
            try:
                ast.parse(content)
            except SyntaxError:
                # Ignorer les fichiers avec erreurs de syntaxe
                return False
            
            # Patterns de correction pour les docstrings malformées
            patterns = [
                # Docstring sans fermeture suivie de code
                (r'(""")([^"]*?)(""")\s*([A-Za-z_][A-Za-z0-9_]*\s*[=:])', 
                 r'\1\2\3\n    \4'),
                
                # Triple quotes mal fermées
                (r'(""")([^"]*?)(?!""")([\n\s]*[A-Za-z_])', 
                 r'\1\2"""\n\3'),
                
                # Docstrings avec une seule quote
                (r'^(\s*)(")([^"]*?)(")(\s*$)', 
                 r'\1"""\3"""\5'),
            ]
            
            original_content = content
            for pattern, replacement in patterns:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            if content != original_content:
                # Vérifier que les corrections n'ont pas cassé la syntaxe
                try:
                    ast.parse(content)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.fixed_files.append(file_path)
                    return True
                except SyntaxError:
                    # Annuler les changements si la syntaxe est cassée
                    return False
            
            return False
            
        except Exception as e:
            self.errors.append(f"Error fixing {file_path}: {e}")
            return False
    
    def audit_repository(self) -> Dict[str, any]:
        """Audit complet des docstrings du repository"""
        print("🔍 Scanning Python files for docstring issues...")
        
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if not any(ex in str(f) for ex in [
            '__pycache__', '.git', 'venv', 'env', '.pytest_cache', 'build', 'dist'
        ])]
        
        total_files = len(python_files)
        files_with_issues = 0
        total_docstrings = 0
        compliant_docstrings = 0
        
        print(f"Found {total_files} Python files to analyze")
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{total_files} files analyzed")
            
            docstrings = self.extract_docstrings(file_path)
            if not docstrings:
                continue
            
            file_has_issues = False
            for docstring, line_num, context in docstrings:
                total_docstrings += 1
                is_compliant, issues = self.is_pep257_compliant(docstring, context)
                
                if is_compliant:
                    compliant_docstrings += 1
                else:
                    file_has_issues = True
                    for issue in issues:
                        self.issues.append(DocstringIssue(
                            file_path=file_path,
                            line_number=line_num,
                            issue_type="PEP257",
                            description=issue,
                            suggestion=self.standardize_docstring(docstring, context)
                        ))
            
            if file_has_issues:
                files_with_issues += 1
        
        compliance_rate = (compliant_docstrings / total_docstrings * 100) if total_docstrings > 0 else 0
        
        return {
            'total_files': total_files,
            'files_with_issues': files_with_issues,
            'total_docstrings': total_docstrings,
            'compliant_docstrings': compliant_docstrings,
            'compliance_rate': compliance_rate,
            'issues': len(self.issues)
        }
    
    def generate_pep257_report(self) -> str:
        """Génère un rapport PEP257 détaillé"""
        audit_results = self.audit_repository()
        
        report = f"""# Rapport de Conformité PEP257 - Projet Ainflue

## 📊 Statistiques Globales
- **Total fichiers Python**: {audit_results['total_files']:,}
- **Fichiers avec problèmes**: {audit_results['files_with_issues']:,}
- **Total docstrings**: {audit_results['total_docstrings']:,}
- **Docstrings conformes**: {audit_results['compliant_docstrings']:,}
- **Taux de conformité**: {audit_results['compliance_rate']:.1f}%
- **Total problèmes**: {audit_results['issues']:,}

## 🎯 Objectifs de Standardisation
- [{"x" if audit_results['compliance_rate'] >= 90 else " "}] Conformité PEP257 ≥ 90%
- [{"x" if audit_results['compliance_rate'] >= 95 else " "}] Conformité PEP257 ≥ 95%
- [{"x" if audit_results['compliance_rate'] >= 99 else " "}] Conformité PEP257 ≥ 99%

## 📋 Actions Recommandées
"""
        
        if audit_results['compliance_rate'] < 90:
            report += """
### 🔥 Priorité Critique
1. **Correction automatique** - Exécuter le script de standardisation
2. **Validation manuelle** - Réviser les cas complexes
3. **Tests de régression** - Vérifier que les corrections n'impactent pas les fonctionnalités
"""
        
        # Échantillon des problèmes les plus courants
        issue_types = {}
        for issue in self.issues[:50]:  # Limiter à 50 pour le rapport
            if issue.issue_type not in issue_types:
                issue_types[issue.issue_type] = []
            issue_types[issue.issue_type].append(issue)
        
        report += "\n## 🔍 Échantillon des Problèmes Détectés\n"
        for issue_type, issues in issue_types.items():
            report += f"\n### {issue_type}\n"
            for issue in issues[:5]:  # Top 5 par type
                report += f"- `{issue.file_path}:{issue.line_number}` - {issue.description}\n"
        
        return report


class SyntaxErrorValidator:
    """Validateur et correcteur d'erreurs de syntaxe"""
    
    def __init__(self, root_path: Path):
        self.root_path = Path(root_path)
        self.syntax_issues: List[SyntaxIssue] = []
        self.fixed_files: List[Path] = []
        
    def validate_syntax(self, file_path: Path) -> Tuple[bool, Optional[SyntaxIssue]]:
        """Valide la syntaxe d'un fichier Python"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ast.parse(content)
            return True, None
            
        except SyntaxError as e:
            issue = SyntaxIssue(
                file_path=file_path,
                line_number=e.lineno or 0,
                error_type="SyntaxError",
                description=e.msg or "Unknown syntax error",
                fixable=self._is_fixable_syntax_error(e)
            )
            return False, issue
            
        except Exception as e:
            issue = SyntaxIssue(
                file_path=file_path,
                line_number=0,
                error_type="ParsingError",
                description=str(e),
                fixable=False
            )
            return False, issue
    
    def _is_fixable_syntax_error(self, error: SyntaxError) -> bool:
        """Détermine si une erreur de syntaxe est réparable automatiquement"""
        fixable_patterns = [
            "invalid syntax",
            "unexpected indent",
            "unmatched",
            "unterminated string",
            "unterminated triple-quoted string"
        ]
        
        error_msg = error.msg.lower() if error.msg else ""
        return any(pattern in error_msg for pattern in fixable_patterns)
    
    def audit_syntax(self) -> Dict[str, any]:
        """Audit syntaxique complet"""
        print("🔍 Validating Python syntax across repository...")
        
        python_files = list(self.root_path.rglob("*.py"))
        python_files = [f for f in python_files if not any(ex in str(f) for ex in [
            '__pycache__', '.git', 'venv', 'env', '.pytest_cache', 'build', 'dist'
        ])]
        
        valid_files = 0
        invalid_files = 0
        fixable_issues = 0
        
        for i, file_path in enumerate(python_files):
            if i % 100 == 0:
                print(f"Progress: {i}/{len(python_files)} files validated")
            
            is_valid, issue = self.validate_syntax(file_path)
            if is_valid:
                valid_files += 1
            else:
                invalid_files += 1
                self.syntax_issues.append(issue)
                if issue.fixable:
                    fixable_issues += 1
        
        syntax_compliance = (valid_files / len(python_files) * 100) if python_files else 0
        
        return {
            'total_files': len(python_files),
            'valid_files': valid_files,
            'invalid_files': invalid_files,
            'fixable_issues': fixable_issues,
            'syntax_compliance': syntax_compliance
        }


def create_ci_integration():
    """Crée l'intégration CI/CD pour la validation syntaxique"""
    
    ci_syntax_check = '''
# Syntax validation step for CI/CD
- name: 🔍 Python Syntax Validation
  run: |
    python scripts/fix_syntax_errors.py --audit --report
    if [ -f syntax_audit_report.md ]; then
      echo "Syntax issues found. See artifact for details."
      exit 1
    fi

- name: 📄 Upload syntax audit report
  uses: actions/upload-artifact@v3
  if: failure()
  with:
    name: syntax-audit-report
    path: syntax_audit_report.md

- name: 🎯 PEP257 Docstring Validation
  run: |
    python -c "
from scripts.pep257_standardizer import PEP257DocstringStandardizer
from pathlib import Path
standardizer = PEP257DocstringStandardizer(Path('.'))
audit_results = standardizer.audit_repository()
if audit_results['compliance_rate'] < 90:
    print(f'Docstring compliance: {audit_results[\"compliance_rate\"]:.1f}% (target: 90%)')
    exit(1)
print(f'Docstring compliance: {audit_results[\"compliance_rate\"]:.1f}% ✅')
"
'''
    
    return ci_syntax_check


def main():
    """Point d'entrée principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="PEP257 Docstring Standardizer & Syntax Validator")
    parser.add_argument("--audit-docstrings", action="store_true", help="Audit docstring compliance")
    parser.add_argument("--audit-syntax", action="store_true", help="Audit syntax compliance")
    parser.add_argument("--fix-docstrings", action="store_true", help="Fix docstring issues")
    parser.add_argument("--generate-ci", action="store_true", help="Generate CI integration")
    parser.add_argument("--root", default=".", help="Repository root path")
    
    args = parser.parse_args()
    
    if args.generate_ci:
        ci_integration = create_ci_integration()
        with open("ci_syntax_integration.yml", "w") as f:
            f.write(ci_integration)
        print("📄 CI integration generated: ci_syntax_integration.yml")
        return
    
    if args.audit_docstrings:
        standardizer = PEP257DocstringStandardizer(Path(args.root))
        report = standardizer.generate_pep257_report()
        with open("pep257_compliance_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 PEP257 report generated: pep257_compliance_report.md")
    
    if args.audit_syntax:
        validator = SyntaxErrorValidator(Path(args.root))
        results = validator.audit_syntax()
        print(f"\n📊 Syntax Validation Results:")
        print(f"✅ Valid files: {results['valid_files']:,}")
        print(f"❌ Invalid files: {results['invalid_files']:,}")
        print(f"🔧 Fixable issues: {results['fixable_issues']:,}")
        print(f"📈 Syntax compliance: {results['syntax_compliance']:.1f}%")
    
    if args.fix_docstrings:
        standardizer = PEP257DocstringStandardizer(Path(args.root))
        python_files = list(Path(args.root).rglob("*.py"))
        fixed_count = 0
        
        for file_path in python_files[:50]:  # Limiter à 50 fichiers pour le test
            if standardizer.fix_file_docstrings(file_path):
                fixed_count += 1
        
        print(f"🔧 Fixed docstrings in {fixed_count} files")


if __name__ == "__main__":
    main()