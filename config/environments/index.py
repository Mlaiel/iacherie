"""
 Configuration Environments Index - IA-Influencer-Agent
==================================================================
Lead Dev IA: Fahed Mlaiel <mlaiel@live.de>
Experts: DevOps + Backend Senior + ML Engineer + DBA + Security
Date: 2025-08-15

PROPRIÉTAIRE EXCLUSIF: Fahed Mlaiel
  AVERTISSEMENT LÉGAL STRICT:
Toute tentative de copie, vol, réutilisation sans autorisation
écrite explicite du propriétaire constitue une violation grave
des droits d'auteur et sera poursuivie selon la loi allemande.
Contact: mlaiel@live.de

Point d'entrée principal pour le système de configuration d'environnements.
Fournit des fonctions utilitaires et des raccourcis pour l'utilisation quotidienne.
==================================================================
"""

import os
import sys
from typing import Dict, Any, Optional, List
from enum import Enum
import json
from pathlib import Path

# Import du système complet
from . import (
    get_default_config,
    create_config_from_env,
    validate_all_configurations,
    EnvironmentManagerFactory,
    EnvironmentType,
    DeploymentType,
    CloudProvider,
    BaseEnvironmentConfigManager
)


class ConfigurationManager:
    """
    Gestionnaire principal de configuration pour simplifier l'utilisation.
    Fournit une interface unifiée pour toutes les opérations de configuration.
    """
    
    def __init__(self):
        self._current_config: Optional[BaseEnvironmentConfigManager] = None
        self._config_cache: Dict[str, BaseEnvironmentConfigManager] = {}
        
    def get_config(
        self, 
        env_type: Optional[EnvironmentType] = None,
        deployment_type: Optional[DeploymentType] = None,
        cloud_provider: Optional[CloudProvider] = None,
        force_reload: bool = False
    ) -> BaseEnvironmentConfigManager:
        """
        Récupère ou crée une configuration avec mise en cache.
        
        Args:
            env_type: Type d'environnement
            deployment_type: Type de déploiement  
            cloud_provider: Provider cloud
            force_reload: Force le rechargement même si en cache
            
        Returns:
            Instance de configuration
        """
        # Génération clé cache
        cache_key = f"{env_type}_{deployment_type}_{cloud_provider}"
        
        # Vérification cache
        if not force_reload and cache_key in self._config_cache:
            return self._config_cache[cache_key]
            
        # Création nouvelle configuration
        config = EnvironmentManagerFactory.create_manager(
            env_type=env_type,
            deployment_type=deployment_type,
            cloud_provider=cloud_provider,
            auto_detect=True
        )
        
        # Mise en cache
        self._config_cache[cache_key] = config
        self._current_config = config
        
        return config
        
    def get_current_config(self) -> BaseEnvironmentConfigManager:
        """Retourne la configuration actuellement active"""
        if self._current_config is None:
            self._current_config = get_default_config()
        return self._current_config
        
    def switch_environment(self, env_type: EnvironmentType) -> None:
        """Change d'environnement actuel"""
        self._current_config = self.get_config(env_type=env_type)
        
    def export_config(
        self, 
        format_type: str = "json",
        include_secrets: bool = False
    ) -> str:
        """
        Exporte la configuration actuelle.
        
        Args:
            format_type: Format d'export ("json", "yaml", "env")
            include_secrets: Inclure les données sensibles
            
        Returns:
            Configuration exportée sous forme de string
        """
        config = self.get_current_config()
        config_dict = config.export_to_dict()
        
        # Masquage des secrets si nécessaire
        if not include_secrets:
            config_dict = self._mask_secrets(config_dict)
            
        if format_type.lower() == "json":
            return json.dumps(config_dict, indent=2, default=str)
        elif format_type.lower() == "yaml":
            import yaml
            return yaml.dump(config_dict, default_flow_style=False)
        elif format_type.lower() == "env":
            return self._to_env_format(config_dict)
        else:
            raise ValueError(f"Format non supporté: {format_type}")
            
    def _mask_secrets(self, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Masque les données sensibles dans la configuration"""
        sensitive_keys = [
            "password", "secret", "key", "token", "auth", "credential",
            "jwt_secret_key", "oauth2_secret_key", "encryption_key",
            "aws_secret_access_key", "database_password", "redis_password"
        ]
        
        def mask_dict(d):
            if isinstance(d, dict):
                return {
                    k: "***MASKED***" if any(sens in k.lower() for sens in sensitive_keys)
                    else mask_dict(v) for k, v in d.items()
                }
            elif isinstance(d, list):
                return [mask_dict(item) for item in d]
            else:
                return d
                
        return mask_dict(config_dict)
        
    def _to_env_format(self, config_dict: Dict[str, Any]) -> str:
        """Convertit la configuration en format .env"""
        env_lines = []
        
        def flatten_dict(d, prefix=""):
            for k, v in d.items():
                key = f"{prefix}{k.upper()}" if prefix else k.upper()
                if isinstance(v, dict):
                    flatten_dict(v, f"{key}_")
                elif isinstance(v, (list, tuple)):
                    env_lines.append(f"{key}={','.join(map(str, v))}")
                else:
                    env_lines.append(f"{key}={v}")
                    
        flatten_dict(config_dict)
        return "\n".join(env_lines)
        
    def validate_current_config(self) -> Dict[str, Any]:
        """Valide la configuration actuelle avec détails"""
        config = self.get_current_config()
        
        validation_result = {
            "is_valid": False,
            "config_type": type(config).__name__,
            "environment": config.environment.value,
            "errors": [],
            "warnings": [],
            "checks": {}
        }
        
        try:
            # Validation générale
            validation_result["is_valid"] = config.validate_configuration()
            
            # Vérifications détaillées
            checks = {
                "database_config": config.database_config is not None,
                "redis_config": config.redis_config is not None,
                "security_config": config.security_config is not None,
                "ai_config": config.ai_config is not None,
                "storage_config": config.storage_config is not None
            }
            
            validation_result["checks"] = checks
            
            # Vérifications spécifiques
            if config.database_config:
                try:
                    db_url = config.get_database_url()
                    validation_result["checks"]["database_url_format"] = bool(db_url)
                except Exception as e:
                    validation_result["errors"].append(f"Database URL error: {e}")
                    
            if config.redis_config:
                try:
                    redis_url = config.get_redis_url()
                    validation_result["checks"]["redis_url_format"] = bool(redis_url)
                except Exception as e:
                    validation_result["errors"].append(f"Redis URL error: {e}")
                    
        except Exception as e:
            validation_result["errors"].append(f"Validation error: {e}")
            
        return validation_result
        
    def get_health_status(self) -> Dict[str, Any]:
        """Retourne le statut de santé de la configuration"""
        config = self.get_current_config()
        
        return {
            "status": "healthy" if config.validate_configuration() else "unhealthy",
            "environment": config.environment.value,
            "debug_mode": config.debug,
            "host": config.host,
            "port": config.port,
            "workers": config.workers,
            "version": config.app_version,
            "timestamp": __import__("datetime").datetime.now().isoformat()
        }
        
    def clear_cache(self) -> None:
        """Vide le cache des configurations"""
        self._config_cache.clear()
        self._current_config = None


# Instance globale du gestionnaire
config_manager = ConfigurationManager()


def get_config_manager() -> ConfigurationManager:
    """Retourne l'instance globale du gestionnaire de configuration"""



    return config_manager


def quick_setup(environment: str = "auto") -> BaseEnvironmentConfigManager:
    """
    Configuration rapide pour démarrage.
    
    Args:
        environment: "auto", "dev", "prod", "staging", "test", "docker", "k8s"
        
    Returns:
        Configuration prête à utiliser
    """
    if environment == "auto":
        return get_default_config()
    
    env_mapping = {
        "dev": EnvironmentType.DEVELOPMENT,
        "development": EnvironmentType.DEVELOPMENT,
        "prod": EnvironmentType.PRODUCTION,
        "production": EnvironmentType.PRODUCTION,
        "staging": EnvironmentType.STAGING,
        "test": EnvironmentType.TESTING,
        "testing": EnvironmentType.TESTING
    }
    
    deployment_mapping = {
        "docker": DeploymentType.DOCKER,
        "k8s": DeploymentType.KUBERNETES,
        "kubernetes": DeploymentType.KUBERNETES,
        "cloud": DeploymentType.CLOUD
    }
    
    if environment in env_mapping:
        return config_manager.get_config(env_type=env_mapping[environment])
    elif environment in deployment_mapping:
        return config_manager.get_config(deployment_type=deployment_mapping[environment])
    else:
        raise ValueError(f"Environnement non reconnu: {environment}")


def print_config_summary() -> None:
    """Affiche un résumé de la configuration actuelle"""
    config = config_manager.get_current_config()
    
    print(" Configuration IA-Influencer-Agent")
    print("=" * 50)
    print(f"Environment: {config.environment.value}")
    print(f"Debug Mode: {config.debug}")
    print(f"Host:Port: {config.host}:{config.port}")
    print(f"Workers: {config.workers}")
    print(f"Version: {config.app_version}")
    print()
    
    # Statut des composants
    components = {
        "Database": config.database_config is not None,
        "Redis": config.redis_config is not None,
        "Security": config.security_config is not None,
        "AI Config": config.ai_config is not None,
        "Storage": config.storage_config is not None,
        "Monitoring": config.monitoring_config is not None
    }
    
    print(" Components Status:")
    for component, status in components.items():
        icon = "" if status else ""
        print(f"  {icon} {component}")
    print()
    
    # Validation
    is_valid = config.validate_configuration()
    validation_icon = "" if is_valid else ""
    print(f" Validation: {validation_icon} {'PASSED' if is_valid else 'FAILED'}")


def run_diagnostics() -> Dict[str, Any]:
    """Exécute un diagnostic complet du système de configuration"""
    print(" Running IA-Influencer-Agent Configuration Diagnostics...")
    print("=" * 60)
    
    # Test de toutes les configurations
    validation_results = validate_all_configurations()
    
    # Résumé
    total_configs = len(validation_results)
    passed_configs = sum(1 for result in validation_results.values() if result)
    
    print(f"\n Diagnostic Results:")
    print(f"Total Configurations: {total_configs}")
    print(f"Passed: {passed_configs}")
    print(f"Failed: {total_configs - passed_configs}")
    
    # Détail par configuration
    print(f"\n Detailed Results:")
    for config_name, result in validation_results.items():
        icon = "" if result else ""
        print(f"  {icon} {config_name}")
        
    # Configuration actuelle
    print(f"\n Current Configuration:")
    current_validation = config_manager.validate_current_config()
    print(f"  Type: {current_validation['config_type']}")
    print(f"  Environment: {current_validation['environment']}")
    print(f"  Valid: {'' if current_validation['is_valid'] else ''}")
    
    if current_validation['errors']:
        print(f"  Errors: {len(current_validation['errors'])}")
        for error in current_validation['errors']:
            print(f"    - {error}")
            
    return {
        "summary": {
            "total": total_configs,
            "passed": passed_configs,
            "failed": total_configs - passed_configs
        },
        "results": validation_results,
        "current_config": current_validation
    }


def main():
    """Fonction principale pour exécution en CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="IA-Influencer-Agent Configuration Manager")
    parser.add_argument("--env", default="auto", help="Environment to use")
    parser.add_argument("--summary", action="store_true", help="Show configuration summary")
    parser.add_argument("--diagnostics", action="store_true", help="Run full diagnostics")
    parser.add_argument("--export", choices=["json", "yaml", "env"], help="Export configuration")
    parser.add_argument("--validate", action="store_true", help="Validate current configuration")
    
    args = parser.parse_args()
    
    # Configuration de l'environnement
    config = quick_setup(args.env)
    
    if args.summary:
        print_config_summary()
    elif args.diagnostics:
        run_diagnostics()
    elif args.export:
        exported = config_manager.export_config(format_type=args.export)
        print(exported)
    elif args.validate:
        result = config_manager.validate_current_config()
        print(json.dumps(result, indent=2))
    else:
        print_config_summary()


if __name__ == "__main__":
    main()
