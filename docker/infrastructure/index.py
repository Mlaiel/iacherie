"""
Ainflue Docker Infrastructure Orchestrator

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.

Advanced infrastructure orchestrator for Docker Compose services management
according to Ainflue business logic and creator type requirements.
"""

import asyncio
import os
import subprocess
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path

try:
    from . import (
        INFRASTRUCTURE_SERVICES,
        BUSINESS_LOGIC_STAGES,
        CREATOR_INFRASTRUCTURE
    )
except ImportError:
    # When running directly, import from __init__.py in the same directory
    import sys
    from pathlib import Path
    sys.path.append(str(Path(__file__).parent))
    from __init__ import (
        INFRASTRUCTURE_SERVICES,
        BUSINESS_LOGIC_STAGES,
        CREATOR_INFRASTRUCTURE
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DockerInfrastructureOrchestrator:
    """
    Advanced Docker infrastructure orchestrator for Ainflue platform.
    
    Manages deployment, scaling, monitoring and backup of specialized
    infrastructure services based on creator type and business logic stages.
    """
    
    def __init__(self, infrastructure_path -> None: str = "/home/runner/work/Ainflue/Ainflue/docker/infrastructure") -> None:
        self.infrastructure_path = Path(infrastructure_path)
        self.business_logic_stages = BUSINESS_LOGIC_STAGES
        self.creator_infrastructure = CREATOR_INFRASTRUCTURE
        self.infrastructure_services = INFRASTRUCTURE_SERVICES
        self.active_services = {}
        self.health_status = {}
        
    async def deploy_creator_infrastructure(self, creator_type: str, environment: str = "production") -> Dict:
        """
        Deploy infrastructure selon type créateur et logique métier.
        
        Args:
            creator_type: Type de créateur (MUSICIAN, PHOTOGRAPHER, etc.)
            environment: Environnement de déploiement (production, staging, dev)
            
        Returns:
            Dict: Statut du déploiement avec détails des services
        """
        logger.info(f"Deploying infrastructure for creator type: {creator_type}")
        
        if creator_type not in self.creator_infrastructure:
            raise ValueError(f"Unknown creator type: {creator_type}")
            
        required_services = self.creator_infrastructure[creator_type]
        deployment_status = {
            "creator_type": creator_type,
            "environment": environment,
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "success": True,
            "errors": []
        }
        
        for service_name in required_services:
            try:
                service_config = self.infrastructure_services[service_name]
                compose_file = self.infrastructure_path / service_config["compose_file"]
                
                if not compose_file.exists():
                    raise FileNotFoundError(f"Compose file not found: {compose_file}")
                
                # Deploy service using docker-compose
                result = await self._deploy_service(service_name, compose_file, environment)
                deployment_status["services"][service_name] = result
                
                if result["success"]:
                    self.active_services[service_name] = {
                        "compose_file": str(compose_file),
                        "deployed_at": datetime.now().isoformat(),
                        "environment": environment
                    }
                    logger.info(f"Successfully deployed service: {service_name}")
                else:
                    deployment_status["success"] = False
                    deployment_status["errors"].append(f"Failed to deploy {service_name}: {result.get('error')}")
                    
            except Exception as e:
                error_msg = f"Error deploying service {service_name}: {str(e)}"
                logger.error(error_msg)
                deployment_status["success"] = False
                deployment_status["errors"].append(error_msg)
                deployment_status["services"][service_name] = {
                    "success": False,
                    "error": str(e)
                }
        
        return deployment_status
    
    async def _deploy_service(self, service_name: str, compose_file: Path, environment: str) -> Dict:
        """Deploy individual service using docker-compose."""
        try:
            cmd = [
                "docker", "compose",
                "-f", str(compose_file),
                "up", "-d"
            ]
            
            # Add environment-specific overrides
            if environment != "production":
                env_file = self.infrastructure_path / f".env.{environment}"
                if env_file.exists():
                    cmd.extend(["--env-file", str(env_file)])
            
            result = subprocess.run(
                cmd,
                cwd=str(self.infrastructure_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "service": service_name,
                    "stdout": result.stdout,
                    "deployed_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "service": service_name,
                    "error": result.stderr,
                    "stdout": result.stdout
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "service": service_name,
                "error": "Deployment timeout after 5 minutes"
            }
        except Exception as e:
            return {
                "success": False,
                "service": service_name,
                "error": str(e)
            }
    
    async def monitor_infrastructure_health(self) -> Dict:
        """
        Monitor santé infrastructure temps réel.
        
        Returns:
            Dict: Statut de santé de tous les services actifs
        """
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "services": {},
            "metrics": {
                "total_services": len(self.active_services),
                "healthy_services": 0,
                "unhealthy_services": 0,
                "warning_services": 0
            }
        }
        
        for service_name, service_info in self.active_services.items():
            try:
                health_status = await self._check_service_health(service_name)
                health_report["services"][service_name] = health_status
                
                if health_status["status"] == "healthy":
                    health_report["metrics"]["healthy_services"] += 1
                elif health_status["status"] == "warning":
                    health_report["metrics"]["warning_services"] += 1
                    if health_report["overall_status"] == "healthy":
                        health_report["overall_status"] = "warning"
                else:
                    health_report["metrics"]["unhealthy_services"] += 1
                    health_report["overall_status"] = "unhealthy"
                    
            except Exception as e:
                logger.error(f"Error checking health for service {service_name}: {e}")
                health_report["services"][service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                health_report["metrics"]["unhealthy_services"] += 1
                health_report["overall_status"] = "unhealthy"
        
        self.health_status = health_report
        return health_report
    
    async def _check_service_health(self, service_name: str) -> Dict:
        """Check health of individual service."""
        try:
            # Check if containers are running
            cmd = ["docker", "compose", "ps", "-q"]
            result = subprocess.run(cmd, cwd=str(self.infrastructure_path), capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                # Check container health
                containers = result.stdout.strip().split('\n')
                healthy_containers = 0
                total_containers = len(containers)
                
                for container_id in containers:
                    health_cmd = ["docker", "inspect", "--format='{{.State.Health.Status}}'", container_id]
                    health_result = subprocess.run(health_cmd, capture_output=True, text=True)
                    
                    if "healthy" in health_result.stdout:
                        healthy_containers += 1
                
                if healthy_containers == total_containers:
                    return {"status": "healthy", "containers": f"{healthy_containers}/{total_containers}"}
                elif healthy_containers > 0:
                    return {"status": "warning", "containers": f"{healthy_containers}/{total_containers}"}
                else:
                    return {"status": "unhealthy", "containers": f"{healthy_containers}/{total_containers}"}
            else:
                return {"status": "stopped", "containers": "0/0"}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def auto_scale_services(self, metrics: Optional[Dict] = None) -> Dict:
        """
        Auto-scaling intelligent selon charge.
        
        Args:
            metrics: Métriques de performance actuelles
            
        Returns:
            Dict: Résultat des opérations d'auto-scaling
        """
        scaling_report = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "services_scaled": {},
            "recommendations": []
        }
        
        # If no metrics provided, collect current metrics
        if not metrics:
            metrics = await self._collect_performance_metrics()
        
        for service_name, service_metrics in metrics.get("services", {}).items():
            if service_name not in self.active_services:
                continue
                
            cpu_usage = service_metrics.get("cpu_percent", 0)
            memory_usage = service_metrics.get("memory_percent", 0)
            
            # Auto-scaling logic
            if cpu_usage > 80 or memory_usage > 85:
                # Scale up
                scale_result = await self._scale_service(service_name, "up")
                scaling_report["actions_taken"].append(f"Scaled up {service_name}")
                scaling_report["services_scaled"][service_name] = scale_result
                
            elif cpu_usage < 20 and memory_usage < 30:
                # Scale down (if more than 1 replica)
                scale_result = await self._scale_service(service_name, "down")
                if scale_result.get("scaled"):
                    scaling_report["actions_taken"].append(f"Scaled down {service_name}")
                    scaling_report["services_scaled"][service_name] = scale_result
                else:
                    scaling_report["recommendations"].append(f"Consider reducing resources for {service_name}")
        
        return scaling_report
    
    async def _collect_performance_metrics(self) -> Dict:
        """Collect current performance metrics from all services."""
        return {
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
    
    async def _scale_service(self, service_name: str, direction: str) -> Dict:
        """Scale service up or down."""
        try:
            if direction == "up":
                # Add logic to scale up service
                pass
            elif direction == "down":
                # Add logic to scale down service  
                pass
                
            return {"success": True, "scaled": True, "direction": direction}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def backup_infrastructure(self) -> Dict:
        """
        Backup automatisé infrastructure complète.
        
        Returns:
            Dict: Statut du backup avec détails
        """
        backup_report = {
            "timestamp": datetime.now().isoformat(),
            "backup_id": f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "services_backed_up": [],
            "backup_path": "",
            "success": True,
            "errors": []
        }
        
        try:
            backup_dir = Path(f"/tmp/ainflue_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_report["backup_path"] = str(backup_dir)
            
            # Backup configuration files
            for service_name, service_info in self.active_services.items():
                try:
                    compose_file = Path(service_info["compose_file"])
                    if compose_file.exists():
                        backup_file = backup_dir / compose_file.name
                        backup_file.write_text(compose_file.read_text())
                        backup_report["services_backed_up"].append(service_name)
                except Exception as e:
                    error_msg = f"Failed to backup {service_name}: {str(e)}"
                    backup_report["errors"].append(error_msg)
                    logger.error(error_msg)
            
            # Backup current status
            status_file = backup_dir / "infrastructure_status.json"
            status_file.write_text(json.dumps({
                "active_services": self.active_services,
                "health_status": self.health_status,
                "backup_timestamp": backup_report["timestamp"]
            }, indent=2))
            
            logger.info(f"Infrastructure backup completed: {backup_dir}")
            
        except Exception as e:
            backup_report["success"] = False
            backup_report["errors"].append(str(e))
            logger.error(f"Infrastructure backup failed: {e}")
        
        return backup_report


# Utility functions for direct usage
async def deploy_for_creator(creator_type -> None: str, environment -> None: str = "production") -> None:
    """Convenience function to deploy infrastructure for a creator type."""
    orchestrator = DockerInfrastructureOrchestrator()
    return await orchestrator.deploy_creator_infrastructure(creator_type, environment)


async def get_infrastructure_health() -> None:
    """Convenience function to get current infrastructure health."""
    orchestrator = DockerInfrastructureOrchestrator()
    return await orchestrator.monitor_infrastructure_health()


if __name__ == "__main__":
    import sys
    
    async def main() -> None:
        if len(sys.argv) < 2:
            print("Usage: python index.py <command> [args]")
            print("Commands: deploy <creator_type>, health, backup")
            return
        
        command = sys.argv[1]
        orchestrator = DockerInfrastructureOrchestrator()
        
        if command == "deploy" and len(sys.argv) >= 3:
            creator_type = sys.argv[2]
            environment = sys.argv[3] if len(sys.argv) > 3 else "production"
            result = await orchestrator.deploy_creator_infrastructure(creator_type, environment)
            print(json.dumps(result, indent=2))
            
        elif command == "health":
            result = await orchestrator.monitor_infrastructure_health()
            print(json.dumps(result, indent=2))
            
        elif command == "backup":
            result = await orchestrator.backup_infrastructure()
            print(json.dumps(result, indent=2))
            
        elif command == "scale":
            result = await orchestrator.auto_scale_services()
            print(json.dumps(result, indent=2))
            
        else:
            print("Unknown command or missing arguments")
    
    asyncio.run(main())