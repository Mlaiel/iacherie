#!/usr/bin/env python3
"""
🛡️ ULTRA-SECURE HARMONIZATION ANALYSIS SCRIPT
Expert-level analysis for Ainfluencer platform harmonization

Author: Expert Team (Lead Dev IA + Backend Senior + ML Engineer + DBA + Sécurité + 
        Microservices + Audio + DevOps + IA Prompt Engineer)
"""

import ast
import json
import os
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any, Optional


class UltraSecureHarmonizationAnalyzer:
    """Ultra-secure analyzer for comprehensive codebase harmonization"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.analysis_report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "amateur_naming": [],
            "potential_duplicates": [],
            "import_dependencies": {},
            "class_definitions": {},
            "function_definitions": {},
            "orchestrator_analysis": {},
            "architecture_violations": [],
            "performance_issues": [],
            "security_concerns": [],
            "module_consolidation": {}
        }
    
    def create_secure_backup(self) -> bool:
        """Create ultra-secure backup before any modifications"""
        try:
            # Create backup tag with timestamp
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            backup_tag = f"backup-before-harmonization-{timestamp}"
            
            # Git add all changes
            subprocess.run(["git", "add", "-A"], check=True, cwd=self.base_path)
            
            # Create backup commit
            subprocess.run([
                "git", "commit", "-m", f"BACKUP: État avant analyse harmonisation - {timestamp}"
            ], check=True, cwd=self.base_path)
            
            # Create backup tag
            subprocess.run([
                "git", "tag", backup_tag
            ], check=True, cwd=self.base_path)
            
            print(f"✅ BACKUP CRÉÉ: {backup_tag}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ ERREUR BACKUP: {e}")
            return False
    
    def analyze_amateur_naming(self) -> List[Dict[str, Any]]:
        """Detect amateur naming patterns with professional suggestions"""
        amateur_patterns = [
            "advanced_", "intelligent_", "enhanced_", "enterprise_",
            "smart_", "super_", "mega_", "ultra_", "pro_", "premium_",
            "optimized_", "improved_", "better_", "new_", "v2_"
        ]
        
        amateur_files = []
        
        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            filename = py_file.name
            
            for pattern in amateur_patterns:
                if pattern in filename.lower():
                    professional_name = self._suggest_professional_name(filename, pattern, py_file)
                    amateur_files.append({
                        "file": str(py_file),
                        "pattern": pattern,
                        "suggested_name": professional_name,
                        "module": str(py_file.parent),
                        "priority": self._calculate_naming_priority(py_file)
                    })
        
        return amateur_files
    
    def _suggest_professional_name(self, filename: str, pattern: str, filepath: Path) -> str:
        """Suggest professional name based on context analysis"""
        base_name = filename.replace(pattern, "").replace(".py", "")
        
        # Context-aware mapping
        context_mapping = {
            "audio": "audio_processor.py",
            "video": "video_processor.py",
            "ml": "ml_pipeline.py",
            "ai": "ai_engine.py",
            "security": "security_manager.py",
            "database": "database_manager.py",
            "api": "api_handler.py",
            "service": "service_layer.py",
            "orchestrator": "coordinator.py",
            "workflow": "workflow_engine.py",
            "monitor": "monitor_service.py",
            "cache": "cache_manager.py",
            "config": "configuration.py"
        }
        
        # Check file path context
        path_str = str(filepath).lower()
        for context, professional_name in context_mapping.items():
            if context in path_str or context in base_name.lower():
                return professional_name
        
        # Fallback to cleaned name
        cleaned_name = base_name.replace("_", "_").strip("_")
        return f"{cleaned_name}.py" if cleaned_name else "module.py"
    
    def _calculate_naming_priority(self, filepath: Path) -> int:
        """Calculate priority for renaming (1=highest, 5=lowest)"""
        path_str = str(filepath).lower()
        
        # High priority: core business modules
        if any(module in path_str for module in ["api", "core", "backend", "main"]):
            return 1
        
        # Medium-high: security and infrastructure
        if any(module in path_str for module in ["security", "infrastructure", "database"]):
            return 2
        
        # Medium: processing and ML
        if any(module in path_str for module in ["ml", "processing", "analytics"]):
            return 3
        
        # Medium-low: utilities and services
        if any(module in path_str for module in ["utils", "services", "monitoring"]):
            return 4
        
        # Low priority: examples and tests
        return 5
    
    def analyze_orchestrators(self) -> Dict[str, Any]:
        """Comprehensive orchestrator analysis for consolidation"""
        orchestrator_files = []
        
        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            if "orchestrator" in str(py_file).lower():
                orchestrator_files.append(str(py_file))
        
        # Group orchestrators by function
        orchestrator_groups = {
            "ml_orchestrators": [],
            "api_orchestrators": [],
            "data_orchestrators": [],
            "infrastructure_orchestrators": [],
            "security_orchestrators": [],
            "workflow_orchestrators": []
        }
        
        for orch_file in orchestrator_files:
            file_lower = orch_file.lower()
            
            if any(keyword in file_lower for keyword in ["ml", "ai", "model"]):
                orchestrator_groups["ml_orchestrators"].append(orch_file)
            elif any(keyword in file_lower for keyword in ["api", "service", "endpoint"]):
                orchestrator_groups["api_orchestrators"].append(orch_file)
            elif any(keyword in file_lower for keyword in ["data", "database", "storage"]):
                orchestrator_groups["data_orchestrators"].append(orch_file)
            elif any(keyword in file_lower for keyword in ["infrastructure", "deploy", "cloud"]):
                orchestrator_groups["infrastructure_orchestrators"].append(orch_file)
            elif any(keyword in file_lower for keyword in ["security", "auth", "encrypt"]):
                orchestrator_groups["security_orchestrators"].append(orch_file)
            else:
                orchestrator_groups["workflow_orchestrators"].append(orch_file)
        
        return {
            "total_orchestrators": len(orchestrator_files),
            "files": orchestrator_files,
            "groups": orchestrator_groups,
            "consolidation_needed": len(orchestrator_files) > 10,
            "consolidation_recommendations": self._generate_consolidation_recommendations(orchestrator_groups)
        }
    
    def _generate_consolidation_recommendations(self, groups: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Generate specific consolidation recommendations"""
        recommendations = []
        
        for group_name, files in groups.items():
            if len(files) > 3:  # More than 3 files = consolidation needed
                recommendations.append({
                    "group": group_name,
                    "files_count": len(files),
                    "files": files,
                    "target_name": f"{group_name.replace('_orchestrators', '')}_coordinator.py",
                    "priority": "HIGH" if len(files) > 10 else "MEDIUM"
                })
        
        return recommendations
    
    def analyze_security_posture(self) -> List[Dict[str, Any]]:
        """Analyze security concerns and compliance"""
        security_concerns = []
        
        # Check for hardcoded secrets
        secret_patterns = ["password", "secret", "api_key", "token"]
        
        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for potential security issues
                for pattern in secret_patterns:
                    if f"{pattern} = " in content.lower() and "=" in content:
                        security_concerns.append({
                            "file": str(py_file),
                            "type": "potential_hardcoded_secret",
                            "pattern": pattern,
                            "severity": "HIGH"
                        })
                
                # Check for SQL injection risks
                if "execute(" in content and "%" in content:
                    security_concerns.append({
                        "file": str(py_file),
                        "type": "potential_sql_injection",
                        "severity": "CRITICAL"
                    })
                
            except Exception as e:
                security_concerns.append({
                    "file": str(py_file),
                    "type": "file_read_error",
                    "error": str(e),
                    "severity": "MEDIUM"
                })
        
        return security_concerns
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete ultra-secure analysis"""
        print("🔍 DÉMARRAGE ANALYSE EXHAUSTIVE...")
        
        # Count total files
        total_files = len(list(self.base_path.rglob("*.py")))
        self.analysis_report["total_files"] = total_files
        
        print(f"📊 Fichiers Python détectés: {total_files}")
        
        # Amateur naming analysis
        print("🎯 Analyse nommage amateur...")
        self.analysis_report["amateur_naming"] = self.analyze_amateur_naming()
        
        # Orchestrator analysis
        print("🔧 Analyse orchestrateurs...")
        self.analysis_report["orchestrator_analysis"] = self.analyze_orchestrators()
        
        # Security analysis
        print("🛡️ Analyse sécurité...")
        self.analysis_report["security_concerns"] = self.analyze_security_posture()
        
        # Module consolidation analysis
        print("📦 Analyse consolidation modules...")
        self.analysis_report["module_consolidation"] = self._analyze_module_consolidation()
        
        return self.analysis_report
    
    def _analyze_module_consolidation(self) -> Dict[str, Any]:
        """Analyze opportunities for module consolidation"""
        module_stats = defaultdict(int)
        
        for py_file in self.base_path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue
            
            if len(py_file.parts) > 0:
                module = py_file.parts[0]
                module_stats[module] += 1
        
        # Identify overloaded modules
        overloaded_modules = {
            module: count for module, count in module_stats.items() 
            if count > 100
        }
        
        return {
            "total_modules": len(module_stats),
            "module_file_counts": dict(module_stats),
            "overloaded_modules": overloaded_modules,
            "consolidation_targets": [
                module for module, count in overloaded_modules.items()
                if count > 200
            ]
        }
    
    def save_analysis_report(self, output_file: str = "ANALYSIS_REPORT.json") -> None:
        """Save comprehensive analysis report"""
        output_path = self.base_path / output_file
        
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(self.analysis_report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 RAPPORT SAUVEGARDÉ: {output_path}")
    
    def generate_summary_report(self) -> str:
        """Generate human-readable summary"""
        report = self.analysis_report
        
        summary = f"""
🛡️ RAPPORT ANALYSE HARMONISATION AINFLUENCER
============================================

📊 STATISTIQUES GÉNÉRALES:
- Total fichiers Python: {report['total_files']}
- Nommage amateur détecté: {len(report['amateur_naming'])}
- Orchestrateurs: {report['orchestrator_analysis']['total_orchestrators']}
- Préoccupations sécurité: {len(report['security_concerns'])}

🎯 PRIORITÉS HARMONISATION:
- Fichiers à renommer: {len([f for f in report['amateur_naming'] if f['priority'] <= 2])} (haute priorité)
- Orchestrateurs à consolider: {len(report['orchestrator_analysis']['consolidation_recommendations'])}
- Modules surchargés: {len(report['module_consolidation']['overloaded_modules'])}

🛡️ ÉTAT SÉCURITÉ:
- Problèmes critiques: {len([c for c in report['security_concerns'] if c.get('severity') == 'CRITICAL'])}
- Problèmes haute priorité: {len([c for c in report['security_concerns'] if c.get('severity') == 'HIGH'])}

🚀 RECOMMANDATIONS:
1. Harmoniser nommage par lots de 5 fichiers
2. Consolider orchestrateurs par domaine fonctionnel
3. Résoudre problèmes sécurité critiques en priorité
4. Décomposer modules surchargés (>200 fichiers)
"""
        return summary


def main():
    """Main execution function"""
    analyzer = UltraSecureHarmonizationAnalyzer()
    
    # Create secure backup
    print("🛡️ CRÉATION BACKUP SÉCURISÉ...")
    if not analyzer.create_secure_backup():
        print("❌ BACKUP ÉCHOUÉ - ARRÊT SÉCURISÉ")
        return False
    
    # Run comprehensive analysis
    analysis_report = analyzer.run_comprehensive_analysis()
    
    # Save detailed report
    analyzer.save_analysis_report()
    
    # Display summary
    print(analyzer.generate_summary_report())
    
    print("✅ ANALYSE TERMINÉE AVEC SUCCÈS!")
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)