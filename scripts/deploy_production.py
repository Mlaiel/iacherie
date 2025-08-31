#!/usr/bin/env python3
"""
Production Kubernetes Deployment Orchestrator
Comprehensive deployment and management for Ainflue microservices infrastructure
"""

import os
import yaml
import subprocess
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DeploymentPhase(Enum):
    INFRASTRUCTURE = "infrastructure"
    DATABASES = "databases"
    MICROSERVICES = "microservices"
    INGRESS = "ingress"
    MONITORING = "monitoring"
    VALIDATION = "validation"

@dataclass
class DeploymentStatus:
    phase: DeploymentPhase
    service: str
    status: str
    message: str
    timestamp: float

class ProductionDeploymentOrchestrator:
    """Orchestrate production deployment of Ainflue microservices"""
    
    def __init__(self, region: str = "us-east-1", dry_run: bool = False):
        self.region = region
        self.dry_run = dry_run
        self.base_path = "/home/runner/work/Ainflue/Ainflue/kubernetes"
        self.deployment_history: List[DeploymentStatus] = []
        
        # Define deployment order
        self.deployment_phases = {
            DeploymentPhase.INFRASTRUCTURE: [
                "namespace.yaml",
                "secrets-template.yaml", 
                "region-config.yaml"
            ],
            DeploymentPhase.DATABASES: [
                "postgres-deployment.yaml",
                "redis-deployment.yaml",
                "mongodb-deployment.yaml"
            ],
            DeploymentPhase.MICROSERVICES: [
                "api-gateway/deployment.yaml",
                "user-service/deployment.yaml", 
                "content-service/deployment.yaml",
                "ai-service/deployment.yaml",
                "protection-service/deployment.yaml",
                "collaboration-service/deployment.yaml",
                "payment-service/deployment.yaml",
                "notification-service/deployment.yaml",
                "analytics-service/deployment.yaml"
            ],
            DeploymentPhase.INGRESS: [
                "istio-config.yaml",
                "ingress.yaml"
            ],
            DeploymentPhase.MONITORING: [
                "monitoring.yaml",
                "cluster-autoscaler.yaml"
            ]
        }
    
    def log_status(self, phase: DeploymentPhase, service: str, status: str, message: str = ""):
        """Log deployment status"""
        status_entry = DeploymentStatus(
            phase=phase,
            service=service,
            status=status,
            message=message,
            timestamp=time.time()
        )
        self.deployment_history.append(status_entry)
        print(f"[{phase.value.upper()}] {service}: {status} - {message}")
    
    def run_kubectl(self, command: str, manifest_file: str) -> tuple[bool, str]:
        """Run kubectl command"""
        if self.dry_run:
            cmd = f"kubectl {command} --dry-run=client -f {manifest_file}"
        else:
            cmd = f"kubectl {command} -f {manifest_file}"
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def wait_for_deployment(self, deployment_name: str, namespace: str = "production", timeout: int = 300) -> bool:
        """Wait for deployment to be ready"""
        if self.dry_run:
            return True
            
        cmd = f"kubectl wait --for=condition=available --timeout={timeout}s deployment/{deployment_name} -n {namespace}"
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            return result.returncode == 0
        except:
            return False
    
    def validate_deployment(self, service_name: str, namespace: str = "production") -> bool:
        """Validate deployment is working"""
        if self.dry_run:
            return True
            
        # Check if pods are running
        cmd = f"kubectl get pods -n {namespace} -l app={service_name} -o jsonpath='{{.items[*].status.phase}}'"
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                phases = result.stdout.strip().split()
                return all(phase == "Running" for phase in phases)
        except:
            pass
        return False
    
    def deploy_phase(self, phase: DeploymentPhase) -> bool:
        """Deploy a specific phase"""
        self.log_status(phase, "PHASE", "STARTING", f"Beginning {phase.value} deployment")
        
        phase_success = True
        manifests = self.deployment_phases.get(phase, [])
        
        for manifest in manifests:
            service_name = manifest.split('/')[0] if '/' in manifest else manifest.replace('.yaml', '')
            
            # Determine manifest file path
            if phase == DeploymentPhase.INFRASTRUCTURE:
                manifest_path = os.path.join(self.base_path, "microservices", manifest)
            elif phase == DeploymentPhase.DATABASES:
                manifest_path = os.path.join(self.base_path, "database", manifest)
            elif phase == DeploymentPhase.MICROSERVICES:
                manifest_path = os.path.join(self.base_path, "microservices", manifest)
            elif phase in [DeploymentPhase.INGRESS, DeploymentPhase.MONITORING]:
                if '/' in manifest:
                    manifest_path = os.path.join(self.base_path, "multi-region", self.region, manifest)
                else:
                    manifest_path = os.path.join(self.base_path, "microservices", manifest)
            else:
                manifest_path = os.path.join(self.base_path, manifest)
            
            # Skip if manifest doesn't exist
            if not os.path.exists(manifest_path):
                self.log_status(phase, service_name, "SKIPPED", f"Manifest not found: {manifest_path}")
                continue
            
            # Deploy the manifest
            self.log_status(phase, service_name, "DEPLOYING", f"Applying {manifest}")
            success, output = self.run_kubectl("apply", manifest_path)
            
            if success:
                self.log_status(phase, service_name, "APPLIED", "Manifest applied successfully")
                
                # Wait for deployments to be ready (only for microservices)
                if phase == DeploymentPhase.MICROSERVICES and 'deployment.yaml' in manifest:
                    deployment_name = service_name
                    if self.wait_for_deployment(deployment_name):
                        self.log_status(phase, service_name, "READY", "Deployment is ready")
                        
                        # Validate deployment
                        if self.validate_deployment(service_name):
                            self.log_status(phase, service_name, "VALIDATED", "Deployment validated successfully")
                        else:
                            self.log_status(phase, service_name, "WARNING", "Deployment validation failed")
                    else:
                        self.log_status(phase, service_name, "TIMEOUT", "Deployment did not become ready in time")
                        phase_success = False
            else:
                self.log_status(phase, service_name, "FAILED", f"Failed to apply manifest: {output}")
                phase_success = False
        
        status = "COMPLETED" if phase_success else "FAILED"
        self.log_status(phase, "PHASE", status, f"Phase {phase.value} {status.lower()}")
        return phase_success
    
    def deploy_hpa_configs(self) -> bool:
        """Deploy HPA configurations for all microservices"""
        self.log_status(DeploymentPhase.MICROSERVICES, "HPA", "STARTING", "Deploying HPA configurations")
        
        hpa_success = True
        microservices = [
            "api-gateway", "user-service", "content-service", "ai-service",
            "protection-service", "collaboration-service", "payment-service",
            "notification-service", "analytics-service"
        ]
        
        for service in microservices:
            hpa_path = os.path.join(self.base_path, "microservices", service, "hpa.yaml")
            if os.path.exists(hpa_path):
                success, output = self.run_kubectl("apply", hpa_path)
                if success:
                    self.log_status(DeploymentPhase.MICROSERVICES, f"{service}-hpa", "APPLIED", "HPA applied")
                else:
                    self.log_status(DeploymentPhase.MICROSERVICES, f"{service}-hpa", "FAILED", f"HPA failed: {output}")
                    hpa_success = False
        
        return hpa_success
    
    def run_full_deployment(self) -> bool:
        """Run full production deployment"""
        print(f"Starting Ainflue production deployment in region: {self.region}")
        print(f"Dry run mode: {self.dry_run}")
        print("=" * 60)
        
        overall_success = True
        
        # Deploy each phase in order
        for phase in DeploymentPhase:
            if phase == DeploymentPhase.VALIDATION:
                continue  # Skip validation phase for now
                
            success = self.deploy_phase(phase)
            if not success:
                overall_success = False
                if phase in [DeploymentPhase.INFRASTRUCTURE, DeploymentPhase.DATABASES]:
                    print(f"Critical phase {phase.value} failed. Stopping deployment.")
                    break
        
        # Deploy HPA configurations
        if overall_success:
            hpa_success = self.deploy_hpa_configs()
            overall_success = overall_success and hpa_success
        
        # Final validation
        if overall_success and not self.dry_run:
            self.run_final_validation()
        
        self.print_deployment_summary()
        return overall_success
    
    def run_final_validation(self):
        """Run final deployment validation"""
        self.log_status(DeploymentPhase.VALIDATION, "SYSTEM", "STARTING", "Running final validation")
        
        # Check all services are running
        microservices = [
            "api-gateway", "user-service", "content-service", "ai-service", 
            "protection-service", "collaboration-service", "payment-service",
            "notification-service", "analytics-service"
        ]
        
        all_healthy = True
        for service in microservices:
            if self.validate_deployment(service):
                self.log_status(DeploymentPhase.VALIDATION, service, "HEALTHY", "Service is healthy")
            else:
                self.log_status(DeploymentPhase.VALIDATION, service, "UNHEALTHY", "Service validation failed")
                all_healthy = False
        
        if all_healthy:
            self.log_status(DeploymentPhase.VALIDATION, "SYSTEM", "HEALTHY", "All services are healthy")
        else:
            self.log_status(DeploymentPhase.VALIDATION, "SYSTEM", "DEGRADED", "Some services are unhealthy")
    
    def print_deployment_summary(self):
        """Print deployment summary"""
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUMMARY")
        print("=" * 60)
        
        phase_summary = {}
        for entry in self.deployment_history:
            if entry.phase not in phase_summary:
                phase_summary[entry.phase] = {"success": 0, "failed": 0, "warning": 0}
            
            if entry.status in ["APPLIED", "READY", "VALIDATED", "HEALTHY", "COMPLETED"]:
                phase_summary[entry.phase]["success"] += 1
            elif entry.status in ["FAILED", "TIMEOUT", "UNHEALTHY"]:
                phase_summary[entry.phase]["failed"] += 1
            elif entry.status in ["WARNING", "SKIPPED", "DEGRADED"]:
                phase_summary[entry.phase]["warning"] += 1
        
        for phase, counts in phase_summary.items():
            total = sum(counts.values())
            print(f"{phase.value.upper()}: {counts['success']}/{total} successful, {counts['failed']} failed, {counts['warning']} warnings")
        
        # Print any failures
        failures = [entry for entry in self.deployment_history if entry.status in ["FAILED", "TIMEOUT", "UNHEALTHY"]]
        if failures:
            print("\nFAILURES:")
            for failure in failures:
                print(f"  - {failure.phase.value}/{failure.service}: {failure.message}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Ainflue microservices to production")
    parser.add_argument("--region", default="us-east-1", help="AWS region to deploy to")
    parser.add_argument("--dry-run", action="store_true", help="Run in dry-run mode")
    parser.add_argument("--phase", choices=[p.value for p in DeploymentPhase], help="Deploy specific phase only")
    
    args = parser.parse_args()
    
    orchestrator = ProductionDeploymentOrchestrator(region=args.region, dry_run=args.dry_run)
    
    if args.phase:
        phase = DeploymentPhase(args.phase)
        success = orchestrator.deploy_phase(phase)
    else:
        success = orchestrator.run_full_deployment()
    
    exit(0 if success else 1)

if __name__ == "__main__":
    main()