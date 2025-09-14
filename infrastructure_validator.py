"""
Infrastructure Validator module
Enterprise implementation for Ainflue platform
"""

#!/usr/bin/env python3
"""
Infrastructure Validation Script
Validates Docker configurations, Kubernetes manifests, and infrastructure readiness
Author: Fahed Mlaiel (mlaiel@live.de) - DevOps Engineer + Infrastructure Expert
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import subprocess

class InfrastructureValidator:
    """Validates infrastructure components"""
    
    def __init__(self) -> None:
        self.root_path = Path('.')
        self.docker_configs = []
        self.k8s_manifests = []
        self.validation_results = {}
        
    def scan_docker_configurations(self) -> Dict[str, Any]:
        """Scan and validate Docker configurations"""
        print("🐳 SCANNING DOCKER CONFIGURATIONS")
        print("=" * 50)
        
        # Find all Docker-related files
        docker_files = {
            'dockerfiles': list(self.root_path.rglob('Dockerfile*')),
            'compose_files': list(self.root_path.rglob('docker-compose*.yml')) + list(self.root_path.rglob('docker-compose*.yaml')),
            'docker_configs': list(self.root_path.rglob('*.docker.yml')) + list(self.root_path.rglob('*.docker.yaml'))
        }
        
        total_docker_files = sum(len(files) for files in docker_files.values())
        
        # Validate Docker Compose files
        valid_compose_files = []
        for compose_file in docker_files['compose_files']:
            try:
                with open(compose_file, 'r') as f:
                    content = yaml.safe_load(f)
                    if content and 'services' in content:
                        valid_compose_files.append(str(compose_file))
            except Exception as e:
                print(f"❌ Invalid compose file {compose_file}: {e}")
        
        # Validate Dockerfiles
        valid_dockerfiles = []
        for dockerfile in docker_files['dockerfiles']:
            try:
                with open(dockerfile, 'r') as f:
                    content = f.read()
                    if 'FROM' in content:
                        valid_dockerfiles.append(str(dockerfile))
            except Exception as e:
                print(f"❌ Invalid Dockerfile {dockerfile}: {e}")
        
        results = {
            'total_docker_files': total_docker_files,
            'dockerfiles': {
                'count': len(docker_files['dockerfiles']),
                'valid': len(valid_dockerfiles),
                'files': valid_dockerfiles
            },
            'compose_files': {
                'count': len(docker_files['compose_files']),
                'valid': len(valid_compose_files),
                'files': valid_compose_files
            },
            'docker_configs': {
                'count': len(docker_files['docker_configs']),
                'files': [str(f) for f in docker_files['docker_configs']]
            }
        }
        
        print(f"📦 Total Docker files: {total_docker_files}")
        print(f"📄 Dockerfiles: {results['dockerfiles']['valid']}/{results['dockerfiles']['count']} valid")
        print(f"🔧 Compose files: {results['compose_files']['valid']}/{results['compose_files']['count']} valid")
        print(f"⚙️ Config files: {results['docker_configs']['count']}")
        
        return results
    
    def scan_kubernetes_manifests(self) -> Dict[str, Any]:
        """Scan and validate Kubernetes manifests"""
        print("\n☸️ SCANNING KUBERNETES MANIFESTS")
        print("=" * 50)
        
        # Find K8s manifest files
        k8s_files = []
        k8s_dirs = ['kubernetes', 'k8s', '.kube']
        
        for k8s_dir in k8s_dirs:
            if Path(k8s_dir).exists():
                k8s_files.extend(list(Path(k8s_dir).rglob('*.yml')))
                k8s_files.extend(list(Path(k8s_dir).rglob('*.yaml')))
        
        # Also check for K8s files in other directories
        k8s_files.extend(list(self.root_path.rglob('*deployment*.yml')))
        k8s_files.extend(list(self.root_path.rglob('*service*.yml')))
        k8s_files.extend(list(self.root_path.rglob('*ingress*.yml')))
        
        # Validate K8s manifests
        valid_manifests = []
        manifest_types = {}
        
        for manifest_file in k8s_files:
            try:
                with open(manifest_file, 'r') as f:
                    content = yaml.safe_load(f)
                    if content and 'apiVersion' in content and 'kind' in content:
                        valid_manifests.append(str(manifest_file))
                        kind = content.get('kind', 'Unknown')
                        manifest_types[kind] = manifest_types.get(kind, 0) + 1
            except Exception as e:
                print(f"❌ Invalid K8s manifest {manifest_file}: {e}")
        
        results = {
            'total_files': len(k8s_files),
            'valid_manifests': len(valid_manifests),
            'manifest_types': manifest_types,
            'files': valid_manifests
        }
        
        print(f"📋 Total K8s files: {len(k8s_files)}")
        print(f"✅ Valid manifests: {len(valid_manifests)}")
        print(f"📊 Manifest types: {manifest_types}")
        
        return results
    
    def validate_monitoring_setup(self) -> Dict[str, Any]:
        """Validate monitoring infrastructure"""
        print("\n📊 VALIDATING MONITORING SETUP")
        print("=" * 50)
        
        monitoring_components = {
            'grafana': False,
            'prometheus': False,
            'alertmanager': False,
            'elasticsearch': False,
            'kibana': False,
            'jaeger': False
        }
        
        # Check for monitoring configurations
        monitoring_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(component in file.lower() for component in monitoring_components.keys()):
                    monitoring_files.append(os.path.join(root, file))
                    
                    # Mark component as found
                    for component in monitoring_components.keys():
                        if component in file.lower():
                            monitoring_components[component] = True
        
        # Check requirements files for monitoring libraries
        monitoring_libs = ['prometheus-client', 'grafana', 'elasticsearch', 'jaeger-client']
        requirements_files = list(self.root_path.rglob('requirements*.txt'))
        
        found_libs = []
        for req_file in requirements_files:
            try:
                with open(req_file, 'r') as f:
                    content = f.read().lower()
                    for lib in monitoring_libs:
                        if lib in content:
                            found_libs.append(lib)
            except Exception:
                continue
        
        results = {
            'monitoring_files': len(monitoring_files),
            'components_found': monitoring_components,
            'components_count': sum(monitoring_components.values()),
            'monitoring_libraries': found_libs,
            'files': monitoring_files
        }
        
        print(f"📁 Monitoring files: {len(monitoring_files)}")
        print(f"🔧 Components found: {sum(monitoring_components.values())}/{len(monitoring_components)}")
        print(f"📚 Libraries: {found_libs}")
        
        return results
    
    def validate_microservices_architecture(self) -> Dict[str, Any]:
        """Validate microservices architecture components"""
        print("\n🔧 VALIDATING MICROSERVICES ARCHITECTURE")
        print("=" * 50)
        
        # Check for microservices directories
        microservices_dirs = []
        if Path('microservices').exists():
            microservices_dirs = [d for d in Path('microservices').iterdir() if d.is_dir()]
        
        # Check for API gateway configurations
        api_gateway_files = []
        gateway_patterns = ['nginx', 'traefik', 'istio', 'gateway', 'ingress']
        
        for pattern in gateway_patterns:
            api_gateway_files.extend(list(self.root_path.rglob(f'*{pattern}*.yml')))
            api_gateway_files.extend(list(self.root_path.rglob(f'*{pattern}*.yaml')))
        
        # Check for service mesh configurations
        service_mesh_files = []
        service_mesh_patterns = ['istio', 'linkerd', 'consul']
        
        for pattern in service_mesh_patterns:
            service_mesh_files.extend(list(self.root_path.rglob(f'*{pattern}*')))
        
        results = {
            'microservices_count': len(microservices_dirs),
            'microservices_dirs': [str(d) for d in microservices_dirs],
            'api_gateway_configs': len(api_gateway_files),
            'service_mesh_configs': len(service_mesh_files),
            'api_gateway_files': [str(f) for f in api_gateway_files[:10]],  # Limit output
            'service_mesh_files': [str(f) for f in service_mesh_files[:10]]
        }
        
        print(f"🔗 Microservices: {len(microservices_dirs)}")
        print(f"🌐 API Gateway configs: {len(api_gateway_files)}")
        print(f"🕸️ Service mesh configs: {len(service_mesh_files)}")
        
        return results
    
    def validate_database_configurations(self) -> Dict[str, Any]:
        """Validate database configurations"""
        print("\n🗄️ VALIDATING DATABASE CONFIGURATIONS")
        print("=" * 50)
        
        # Check for database-related files
        db_patterns = ['postgres', 'mongodb', 'redis', 'elasticsearch', 'mysql', 'sqlite']
        db_files = {}
        
        for pattern in db_patterns:
            files = list(self.root_path.rglob(f'*{pattern}*'))
            if files:
                db_files[pattern] = len(files)
        
        # Check database connection configurations
        config_files = list(self.root_path.rglob('*config*.py')) + list(self.root_path.rglob('*settings*.py'))
        db_connections = []
        
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    content = f.read().lower()
                    for pattern in db_patterns:
                        if pattern in content:
                            db_connections.append(f"{config_file}: {pattern}")
            except Exception:
                continue
        
        # Check for migration files
        migration_dirs = ['alembic', 'migrations', 'migrate']
        migration_files = []
        
        for migration_dir in migration_dirs:
            if Path(migration_dir).exists():
                migration_files.extend(list(Path(migration_dir).rglob('*.py')))
        
        results = {
            'database_files': db_files,
            'total_db_files': sum(db_files.values()),
            'database_connections': db_connections,
            'migration_files': len(migration_files),
            'supported_databases': list(db_files.keys())
        }
        
        print(f"🗃️ Database files: {sum(db_files.values())}")
        print(f"💾 Databases: {list(db_files.keys())}")
        print(f"🔄 Migration files: {len(migration_files)}")
        
        return results
    
    def generate_infrastructure_report(self) -> Dict[str, Any]:
        """Generate comprehensive infrastructure report"""
        print("\n🎯 GENERATING INFRASTRUCTURE VALIDATION REPORT")
        print("=" * 80)
        
        # Run all validations
        docker_results = self.scan_docker_configurations()
        k8s_results = self.scan_kubernetes_manifests()
        monitoring_results = self.validate_monitoring_setup()
        microservices_results = self.validate_microservices_architecture()
        database_results = self.validate_database_configurations()
        
        # Calculate infrastructure score
        infrastructure_score = self._calculate_infrastructure_score(
            docker_results, k8s_results, monitoring_results, 
            microservices_results, database_results
        )
        
        report = {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'validator': 'Fahed Mlaiel - DevOps Engineer + Infrastructure Expert',
                'platform': 'Ainflue Platform Infrastructure Validation',
                'version': '1.0.0'
            },
            'infrastructure_score': infrastructure_score,
            'docker_infrastructure': docker_results,
            'kubernetes_infrastructure': k8s_results,
            'monitoring_infrastructure': monitoring_results,
            'microservices_infrastructure': microservices_results,
            'database_infrastructure': database_results,
            'summary': {
                'total_docker_configs': docker_results['total_docker_files'],
                'total_k8s_manifests': k8s_results['valid_manifests'],
                'monitoring_components': monitoring_results['components_count'],
                'microservices_count': microservices_results['microservices_count'],
                'database_systems': len(database_results['supported_databases']),
                'infrastructure_ready': infrastructure_score > 75,
                'production_ready': infrastructure_score > 90
            }
        }
        
        # Save report
        report_file = f"infrastructure_validation_report_{int(datetime.now().timestamp())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 Infrastructure report saved to: {report_file}")
        return report
    
    def _calculate_infrastructure_score(self, docker_res, k8s_res, monitor_res, micro_res, db_res) -> int:
        """Calculate overall infrastructure readiness score"""
        score = 0
        
        # Docker infrastructure (25 points)
        if docker_res['total_docker_files'] > 0:
            docker_score = min(25, docker_res['total_docker_files'] * 2)
            score += docker_score
        
        # Kubernetes infrastructure (25 points)
        if k8s_res['valid_manifests'] > 0:
            k8s_score = min(25, k8s_res['valid_manifests'] * 3)
            score += k8s_score
        
        # Monitoring infrastructure (20 points)
        monitor_score = monitor_res['components_count'] * 4
        score += min(20, monitor_score)
        
        # Microservices architecture (15 points)
        micro_score = micro_res['microservices_count'] * 2 + micro_res['api_gateway_configs']
        score += min(15, micro_score)
        
        # Database infrastructure (15 points)
        db_score = len(db_res['supported_databases']) * 3 + (1 if db_res['migration_files'] > 0 else 0) * 5
        score += min(15, db_score)
        
        return min(100, score)
    
    def print_summary(self, report -> None: Dict[str, Any]) -> None:
        """Print infrastructure validation summary"""
        summary = report['summary']
        score = report['infrastructure_score']
        
        print(f"\n📊 INFRASTRUCTURE VALIDATION SUMMARY")
        print("=" * 80)
        print(f"🏗️ Infrastructure Score: {score}/100")
        print(f"🐳 Docker Configurations: {summary['total_docker_configs']}")
        print(f"☸️ Kubernetes Manifests: {summary['total_k8s_manifests']}")
        print(f"📊 Monitoring Components: {summary['monitoring_components']}")
        print(f"🔧 Microservices: {summary['microservices_count']}")
        print(f"🗄️ Database Systems: {summary['database_systems']}")
        
        if summary['production_ready']:
            print(f"🚀 STATUS: PRODUCTION READY")
        elif summary['infrastructure_ready']:
            print(f"⚠️ STATUS: INFRASTRUCTURE READY (needs optimization)")
        else:
            print(f"🛠️ STATUS: NEEDS INFRASTRUCTURE DEVELOPMENT")
        
        print("=" * 80)

def main() -> None:
    """Main infrastructure validation"""
    validator = InfrastructureValidator()
    report = validator.generate_infrastructure_report()
    validator.print_summary(report)

if __name__ == "__main__":
    main()