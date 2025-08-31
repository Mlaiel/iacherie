#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IA-Influencer-Agent Core System Validation
================================================================================
Module: backend/core/validation.py
Author: Fahed Mlaiel (mlaiel@live.de)
Architecture: Production-Ready Enterprise Validation System
Created: 2025-08-20
Team: Lead Dev IA + Backend Senior + ML Engineer + DBA + Security + Microservices
================================================================================

  PROPRIÉTÉ INTELLECTUELLE EXCLUSIVE - FAHED MLAIEL 
© 2025 Fahed Mlaiel. Tous droits réservés.
Usage non autorisé strictement interdit et passible de poursuites judiciaires.
Contact: mlaiel@live.de

MISSION: Validation complète du système core pour déploiement production
"""

import os
import sys
import importlib
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CoreSystemValidator:
    """
    Validateur complet du système core IA-Influencer-Agent
    
    Effectue des vérifications exhaustives de tous les modules core
    pour garantir un déploiement production sans erreur.
    """
    
    def __init__(self):
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "modules": {},
            "dependencies": {},
            "performance": {},
            "security": {},
            "summary": {
                "total_modules": 0,
                "valid_modules": 0,
                "warning_modules": 0,
                "failed_modules": 0,
                "overall_status": "unknown"
            }
        }
        
        self.core_modules = [
            "adaptation", "adapters", "algorithms", "analytics", "cache",
            "classification", "collaboration", "content", "coordination", "crawlers",
            "discovery", "distribution", "engines", "events", "fingerprinting",
            "intelligence", "interfaces", "licensing", "managers", "matching",
            "monetization", "multimedia", "optimization", "orchestration", "pipeline",
            "platforms", "processors", "protection", "quality", "revenue",
            "rights", "security"
        ]
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Obtient les informations système"""



        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "path": sys.path[:3],  # Premier 3 chemins seulement
            "cwd": os.getcwd()
        }
    
    def validate_module_import(self, module_name: str) -> Dict[str, Any]:
        """
        Valide l'importation d'un module core
        
        Args:
            module_name: Nom du module à valider
            
        Returns:
            Dict avec résultats de validation
        """
        result = {
            "name": module_name,
            "status": "unknown",
            "import_success": False,
            "has_init": False,
            "has_index": False,
            "exports_count": 0,
            "error": None,
            "warnings": []
        }
        
        try:
            # Vérifier si le module a un __init__.py
            module_path = f"backend.core.{module_name}"
            init_path = f"/workspaces/Achiri/IA-Influencer-Agent/backend/core/{module_name}/__init__.py"
            index_path = f"/workspaces/Achiri/IA-Influencer-Agent/backend/core/{module_name}/index.py"
            
            result["has_init"] = os.path.exists(init_path)
            result["has_index"] = os.path.exists(index_path)
            
            if not result["has_init"]:
                result["warnings"].append("Module missing __init__.py")
            
            # Tenter l'importation
            module = importlib.import_module(module_path)
            result["import_success"] = True
            
            # Vérifier les exports
            if hasattr(module, '__all__'):
                result["exports_count"] = len(module.__all__)
            
            # Vérifier les métadonnées
            metadata_checks = ['__version__', '__author__', '__email__']
            for check in metadata_checks:
                if not hasattr(module, check):
                    result["warnings"].append(f"Missing {check} metadata")
            
            # Déterminer le statut final
            if result["import_success"] and result["has_init"]:
                if result["warnings"]:
                    result["status"] = "warning"
                else:
                    result["status"] = "valid"
            else:
                result["status"] = "failed"
                
        except ImportError as e:
            result["status"] = "failed"
            result["error"] = f"Import error: {str(e)}"
        except Exception as e:
            result["status"] = "failed"
            result["error"] = f"Unexpected error: {str(e)}"
        
        return result
    
    def validate_all_modules(self) -> Dict[str, Any]:
        """Valide tous les modules core"""
        logger.info(" Début validation complète des modules core...")
        
        for module_name in self.core_modules:
            logger.info(f"   Validation module: {module_name}")
            module_result = self.validate_module_import(module_name)
            self.validation_results["modules"][module_name] = module_result
            
            # Mettre à jour le résumé
            self.validation_results["summary"]["total_modules"] += 1
            
            if module_result["status"] == "valid":
                self.validation_results["summary"]["valid_modules"] += 1
            elif module_result["status"] == "warning":
                self.validation_results["summary"]["warning_modules"] += 1
            else:
                self.validation_results["summary"]["failed_modules"] += 1
        
        # Déterminer le statut global
        total = self.validation_results["summary"]["total_modules"]
        valid = self.validation_results["summary"]["valid_modules"]
        warning = self.validation_results["summary"]["warning_modules"]
        failed = self.validation_results["summary"]["failed_modules"]
        
        if failed == 0:
            if warning == 0:
                self.validation_results["summary"]["overall_status"] = "excellent"
            elif warning <= total * 0.2:  # Moins de 20% d'avertissements
                self.validation_results["summary"]["overall_status"] = "good"
            else:
                self.validation_results["summary"]["overall_status"] = "acceptable"
        elif failed <= total * 0.1:  # Moins de 10% d'échecs
            self.validation_results["summary"]["overall_status"] = "degraded"
        else:
            self.validation_results["summary"]["overall_status"] = "critical"
        
        return self.validation_results
    
    def validate_core_dependencies(self) -> Dict[str, Any]:
        """Valide les dépendances core essentielles"""
        dependencies_to_check = [
            ("fastapi", "Framework web"),
            ("pydantic", "Validation données"),
            ("sqlalchemy", "ORM base de données"),
            ("redis", "Cache et queue"),
            ("celery", "Tâches asynchrones"),
            ("jwt", "Authentification"),
            ("asyncio", "Programmation asynchrone"),
            ("typing", "Annotations type"),
            ("dataclasses", "Classes de données"),
            ("enum", "Énumérations"),
            ("logging", "Journalisation"),
            ("datetime", "Gestion dates"),
            ("json", "Sérialisation JSON"),
            ("hashlib", "Fonctions hash"),
            ("uuid", "Identifiants uniques")
        ]
        
        dependency_results = {}
        
        for dep_name, description in dependencies_to_check:
            try:
                importlib.import_module(dep_name)
                dependency_results[dep_name] = {
                    "status": "available",
                    "description": description,
                    "error": None
                }
            except ImportError as e:
                dependency_results[dep_name] = {
                    "status": "missing",
                    "description": description,
                    "error": str(e)
                }
        
        self.validation_results["dependencies"] = dependency_results
        return dependency_results
    
    async def validate_core_performance(self) -> Dict[str, Any]:
        """Valide les performances de base"""
        performance_results = {
            "import_time": 0,
            "memory_usage": 0,
            "initialization_time": 0
        }
        
        try:
            # Mesurer le temps d'importation
            start_time = datetime.now()
            
            from . import index
            from . import algorithms
            from . import managers
            
            import_time = (datetime.now() - start_time).total_seconds()
            performance_results["import_time"] = import_time
            
            # Mesurer le temps d'initialisation
            start_init = datetime.now()
            core_status = index.get_core_status()
            init_time = (datetime.now() - start_init).total_seconds()
            performance_results["initialization_time"] = init_time
            
            # Évaluer les performances
            performance_results["status"] = "good"
            if import_time > 5.0:
                performance_results["status"] = "slow"
                performance_results["warnings"] = ["Import time > 5 seconds"]
            elif import_time > 2.0:
                performance_results["status"] = "acceptable"
                performance_results["warnings"] = ["Import time > 2 seconds"]
            
        except Exception as e:
            performance_results["status"] = "failed"
            performance_results["error"] = str(e)
        
        self.validation_results["performance"] = performance_results
        return performance_results
    
    def validate_security_modules(self) -> Dict[str, Any]:
        """Valide les modules de sécurité critiques"""
        security_modules = ["security", "protection", "fingerprinting", "rights"]
        security_results = {}
        
        for module_name in security_modules:
            try:
                module_path = f"backend.core.{module_name}"
                module = importlib.import_module(module_path)
                
                security_results[module_name] = {
                    "status": "available",
                    "has_encryption": hasattr(module, 'encryption') or 'encrypt' in str(dir(module)),
                    "has_authentication": hasattr(module, 'auth') or 'auth' in str(dir(module)),
                    "has_validation": hasattr(module, 'valid') or 'valid' in str(dir(module))
                }
                
            except ImportError:
                security_results[module_name] = {
                    "status": "missing",
                    "critical": True
                }
        
        self.validation_results["security"] = security_results
        return security_results
    
    async def run_complete_validation(self) -> Dict[str, Any]:
        """
        Exécute une validation complète du système core
        
        Returns:
            Dict avec résultats complets de validation
        """
        logger.info(" Début validation complète IA-Influencer-Agent Core System")
        
        # 1. Validation modules
        logger.info(" Validation des modules...")
        self.validate_all_modules()
        
        # 2. Validation dépendances
        logger.info(" Validation des dépendances...")
        self.validate_core_dependencies()
        
        # 3. Validation performance
        logger.info(" Validation des performances...")
        await self.validate_core_performance()
        
        # 4. Validation sécurité
        logger.info(" Validation de la sécurité...")
        self.validate_security_modules()
        
        # 5. Rapport final
        total_modules = len(self.core_modules)
        valid_modules = self.validation_results["summary"]["valid_modules"]
        warning_modules = self.validation_results["summary"]["warning_modules"]
        failed_modules = self.validation_results["summary"]["failed_modules"]
        
        logger.info(" Résultats validation:")
        logger.info(f"    Modules valides: {valid_modules}/{total_modules}")
        logger.info(f"     Avertissements: {warning_modules}")
        logger.info(f"    Échecs: {failed_modules}")
        logger.info(f"    Statut global: {self.validation_results['summary']['overall_status']}")
        
        return self.validation_results
    
    def generate_validation_report(self) -> str:
        """Génère un rapport de validation lisible"""
        report_lines = [
            "=" * 80,
            " RAPPORT VALIDATION IA-INFLUENCER-AGENT CORE SYSTEM",
            "=" * 80,
            f" Date: {self.validation_results['timestamp']}",
            f"‍ Auteur: Fahed Mlaiel (mlaiel@live.de)",
            f" Statut global: {self.validation_results['summary']['overall_status'].upper()}",
            "",
            " RÉSUMÉ:",
            f"   Total modules: {self.validation_results['summary']['total_modules']}",
            f"    Valides: {self.validation_results['summary']['valid_modules']}",
            f"     Avertissements: {self.validation_results['summary']['warning_modules']}",
            f"    Échecs: {self.validation_results['summary']['failed_modules']}",
            "",
        ]
        
        # Détail des modules
        if self.validation_results.get("modules"):
            report_lines.extend([
                " DÉTAIL MODULES:",
                ""
            ])
            
            for module_name, module_info in self.validation_results["modules"].items():
                status_icon = "" if module_info["status"] == "valid" else "" if module_info["status"] == "warning" else ""
                report_lines.append(f"   {status_icon} {module_name}: {module_info['status']}")
                
                if module_info.get("warnings"):
                    for warning in module_info["warnings"]:
                        report_lines.append(f"       {warning}")
                
                if module_info.get("error"):
                    report_lines.append(f"       {module_info['error']}")
            
            report_lines.append("")
        
        # Performances
        if self.validation_results.get("performance"):
            perf = self.validation_results["performance"]
            report_lines.extend([
                " PERFORMANCES:",
                f"   Import time: {perf.get('import_time', 'N/A')}s",
                f"   Init time: {perf.get('initialization_time', 'N/A')}s",
                f"   Status: {perf.get('status', 'unknown')}",
                ""
            ])
        
        report_lines.extend([
            "=" * 80,
            "© 2025 Fahed Mlaiel - IA-Influencer-Agent Core System",
            "=" * 80
        ])
        
        return "\n".join(report_lines)

# Fonctions utilitaires globales
async def validate_core_system() -> Dict[str, Any]:
    """
    Valide complètement le système core
    
    Returns:
        Dict avec résultats de validation
    """
    validator = CoreSystemValidator()
    return await validator.run_complete_validation()

def quick_validate_core() -> bool:
    """
    Validation rapide du système core
    
    Returns:
        bool: True si système valide
    """



    try:
        # Test importation modules critiques
        from . import index, algorithms, managers, security
        
        # Test statut système
        status = index.get_core_status()
        
        return status.get("status") != "failed"
        
    except Exception:
        return False

def print_validation_report():
    """Affiche un rapport de validation formaté"""
    async def _run_and_print():
        validator = CoreSystemValidator()
        await validator.run_complete_validation()
        print(validator.generate_validation_report())
    
    asyncio.run(_run_and_print())

# Export des fonctions principales
__all__ = [
    "CoreSystemValidator",
    "validate_core_system",
    "quick_validate_core", 
    "print_validation_report"
]
