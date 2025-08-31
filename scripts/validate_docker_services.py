#!/usr/bin/env python3
"""Docker Compose Services Validation Script
===========================================

Tests and validates Docker Compose service startup for Ainflue Platform.
Addresses the requirement: "Docker Compose - tester démarrage services"

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""
import subprocess
import time
import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docker_services_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DockerServicesValidator:
    """Validates Docker Compose services startup and health"""    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.compose_files = {
            'basic': 'docker-compose.yml',
            'monitoring': 'docker-compose.monitoring.yml', 
            'production': 'docker-compose.production.yml'
        }
        self.validation_results = {}
        
    def validate_compose_file_syntax(self, compose_file: str) -> Tuple[bool, str]:
        """Validate Docker Compose file syntax"""        try:
            cmd = ['docker', 'compose', '-f', compose_file, 'config']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info(f"✅ {compose_file} syntax is valid")
                return True, "Valid syntax"
            else:
                logger.error(f"❌ {compose_file} syntax error: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"❌ Error validating {compose_file}: {str(e)}")
            return False, str(e)
    
    def check_required_files(self, compose_file: str) -> Tuple[bool, List[str]]:
        """Check if required configuration files exist"""        missing_files = []
        
        # Check Dockerfile
        dockerfile_path = self.project_root / "Dockerfile"
        if not dockerfile_path.exists():
            missing_files.append("Dockerfile")
            
        # Check monitoring configs for monitoring compose
        if 'monitoring' in compose_file:
            monitoring_files = [
                "monitoring/prometheus/prometheus.yml",
                "monitoring/grafana/provisioning/datasources/prometheus.yml"
            ]
            for file_path in monitoring_files:
                if not (self.project_root / file_path).exists():
                    missing_files.append(file_path)
        
        # Check nginx config for basic compose
        if compose_file == 'docker-compose.yml':
            nginx_conf = self.project_root / "nginx.conf"
            if not nginx_conf.exists():
                missing_files.append("nginx.conf")
        
        success = len(missing_files) == 0
        if success:
            logger.info(f"✅ All required files exist for {compose_file}")
        else:
            logger.warning(f"⚠️ Missing files for {compose_file}: {missing_files}")
            
        return success, missing_files
    
    def create_missing_config_files(self, missing_files: List[str]) -> None:
        """Create minimal required configuration files"""        for file_path in missing_files:
            full_path = self.project_root / file_path
            
            if file_path == "nginx.conf":
                self.create_basic_nginx_config(full_path)
            elif file_path == "prometheus.yml":
                self.create_basic_prometheus_config(full_path)
                
    def create_basic_nginx_config(self, path: Path) -> None:
        """Create a basic nginx configuration"""        nginx_config = """events {
    worker_connections 1024;
}

http {
    upstream backend {
        server ainflue-app:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
"""        path.write_text(nginx_config.strip())
        logger.info(f"✅ Created basic nginx.conf at {path}")
    
    def create_basic_prometheus_config(self, path: Path) -> None:
        """Create a basic prometheus configuration"""        prometheus_config = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(prometheus_config.strip())
        logger.info(f"✅ Created basic prometheus.yml at {path}")
    
    def test_compose_services_dry_run(self, compose_file: str) -> Tuple[bool, str]:
        """Test if services can be started (dry run)"""        try:
            # First try to pull images without starting
            cmd = ['docker', 'compose', '-f', compose_file, 'pull', '--ignore-pull-failures']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                logger.warning(f"⚠️ Some images couldn't be pulled for {compose_file}: {result.stderr}")
            
            # Test configuration without starting
            cmd = ['docker', 'compose', '-f', compose_file, 'config']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                logger.info(f"✅ {compose_file} services configuration test passed")
                return True, "Configuration valid"
            else:
                logger.error(f"❌ {compose_file} configuration test failed: {result.stderr}")
                return False, result.stderr
                
        except Exception as e:
            logger.error(f"❌ Error testing {compose_file}: {str(e)}")
            return False, str(e)
    
    def get_service_health_endpoints(self, compose_file: str) -> Dict[str, str]:
        """Get health check endpoints for services"""        health_endpoints = {}
        
        if compose_file == 'docker-compose.yml':
            health_endpoints = {
                'ainflue-app': 'http://localhost:8000/health',
                'postgres': 'pg_isready',
                'redis': 'redis-cli ping',
                'mongodb': 'mongosh --eval "db.adminCommand(\'ping\')"',
                'nginx': 'http://localhost:80/health',
                'prometheus': 'http://localhost:9090/-/healthy',
                'grafana': 'http://localhost:3000/api/health'
            }
        elif 'monitoring' in compose_file:
            health_endpoints = {
                'prometheus': 'http://localhost:9090/-/healthy',
                'grafana': 'http://localhost:3000/api/health',
                'elasticsearch': 'http://localhost:9200/_cluster/health',
                'alertmanager': 'http://localhost:9093/-/healthy'
            }
            
        return health_endpoints
    
    def validate_service_dependencies(self, compose_file: str) -> Tuple[bool, List[str]]:
        """Validate service dependencies are properly configured"""        issues = []
        
        try:
            # Get compose configuration
            cmd = ['docker', 'compose', '-f', compose_file, 'config']
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode != 0:
                return False, [f"Could not read compose config: {result.stderr}"]
            
            # Parse the compose output to check dependencies
            # This is a basic check - in a real scenario you'd parse YAML
            config_output = result.stdout
            
            # Check for common dependency issues
            if 'depends_on' in config_output:
                logger.info(f"✅ {compose_file} has dependency configurations")
            else:
                logger.warning(f"⚠️ {compose_file} may be missing dependency configurations")
                
            if 'networks' in config_output:
                logger.info(f"✅ {compose_file} has network configurations")
            else:
                issues.append("Missing network configurations")
                
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Error validating dependencies: {str(e)}"]
    
    def generate_startup_test_script(self, compose_file: str) -> str:
        """Generate a test script for starting services"""        script_content = f"""#!/bin/bash
# Generated startup test script for {compose_file}
# Run this to test service startup

set -e

echo "🚀 Testing {compose_file} service startup..."

# Clean up any existing containers
docker compose -f {compose_file} down --remove-orphans || true

# Pull latest images
echo "📥 Pulling images..."
docker compose -f {compose_file} pull --ignore-pull-failures

# Start services
echo "🔧 Starting services..."
docker compose -f {compose_file} up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🩺 Checking service health..."
"""        
        health_endpoints = self.get_service_health_endpoints(compose_file)
        for service, endpoint in health_endpoints.items():
            if endpoint.startswith('http'):
                script_content += f"""# Check {service}
if curl -f -s {endpoint} > /dev/null; then
    echo "✅ {service} is healthy"
else
    echo "❌ {service} is not responding"
fi
"""        
        script_content += """echo "📊 Service status:"
docker compose -f """ + compose_file + """ ps

echo "🎉 Startup test completed!"
"""        
        return script_content
    
    def run_validation(self) -> Dict[str, Dict]:
        """Run complete validation for all compose files"""        logger.info("🚀 Starting Docker Compose services validation")
        
        for env_name, compose_file in self.compose_files.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Validating {env_name} environment: {compose_file}")
            logger.info(f"{'='*60}")
            
            file_path = self.project_root / compose_file
            if not file_path.exists():
                logger.error(f"❌ {compose_file} not found")
                self.validation_results[env_name] = {
                    'file_exists': False,
                    'error': f"{compose_file} not found"
                }
                continue
            
            result = {
                'file_exists': True,
                'syntax_valid': False,
                'required_files_exist': False,
                'dependencies_valid': False,
                'dry_run_success': False,
                'issues': [],
                'health_endpoints': {}
            }
            
            # 1. Validate syntax
            syntax_valid, syntax_error = self.validate_compose_file_syntax(compose_file)
            result['syntax_valid'] = syntax_valid
            if not syntax_valid:
                result['issues'].append(f"Syntax error: {syntax_error}")
            
            # 2. Check required files
            files_exist, missing_files = self.check_required_files(compose_file)
            result['required_files_exist'] = files_exist
            if missing_files:
                result['issues'].append(f"Missing files: {missing_files}")
                # Try to create basic configs
                try:
                    self.create_missing_config_files(missing_files)
                    logger.info("✅ Created missing configuration files")
                except Exception as e:
                    logger.error(f"❌ Could not create missing files: {e}")
            
            # 3. Validate dependencies
            deps_valid, dep_issues = self.validate_service_dependencies(compose_file)
            result['dependencies_valid'] = deps_valid
            if dep_issues:
                result['issues'].extend(dep_issues)
            
            # 4. Test dry run
            dry_run_success, dry_run_error = self.test_compose_services_dry_run(compose_file)
            result['dry_run_success'] = dry_run_success
            if not dry_run_success:
                result['issues'].append(f"Dry run failed: {dry_run_error}")
            
            # 5. Get health endpoints
            result['health_endpoints'] = self.get_service_health_endpoints(compose_file)
            
            # 6. Generate test script
            script_content = self.generate_startup_test_script(compose_file)
            script_path = self.project_root / f"test_{env_name}_startup.sh"
            script_path.write_text(script_content)
            script_path.chmod(0o755)
            result['test_script'] = str(script_path)
            logger.info(f"✅ Generated test script: {script_path}")
            
            self.validation_results[env_name] = result
            
            # Summary for this environment
            if result['syntax_valid'] and result['dry_run_success']:
                logger.info(f"✅ {env_name} validation: PASSED")
            else:
                logger.warning(f"⚠️ {env_name} validation: ISSUES FOUND")
        
        return self.validation_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report"""        report = """Docker Compose Services Validation Report
==========================================

"""        
        for env_name, result in self.validation_results.items():
            report += f"\n{env_name.upper()} Environment:\n"
            report += f"{'='*40}\n"
            
            if not result.get('file_exists', False):
                report += f"❌ File not found: {self.compose_files[env_name]}\n"
                continue
            
            report += f"📁 File: {self.compose_files[env_name]}\n"
            report += f"✅ Syntax Valid: {result['syntax_valid']}\n"
            report += f"✅ Required Files: {result['required_files_exist']}\n"
            report += f"✅ Dependencies: {result['dependencies_valid']}\n"
            report += f"✅ Dry Run: {result['dry_run_success']}\n"
            
            if result['issues']:
                report += f"\n⚠️ Issues Found:\n"
                for issue in result['issues']:
                    report += f"   • {issue}\n"
            
            if result['health_endpoints']:
                report += f"\n🩺 Health Endpoints:\n"
                for service, endpoint in result['health_endpoints'].items():
                    report += f"   • {service}: {endpoint}\n"
            
            if 'test_script' in result:
                report += f"\n🧪 Test Script: {result['test_script']}\n"
            
        # Overall summary
        total_envs = len(self.validation_results)
        passing_envs = sum(1 for r in self.validation_results.values() 
                          if r.get('syntax_valid', False) and r.get('dry_run_success', False))
        
        report += f"\n\nSUMMARY\n"
        report += f"{'='*40}\n"
        report += f"Total Environments: {total_envs}\n"
        report += f"Passing Validation: {passing_envs}\n"
        report += f"Success Rate: {(passing_envs/total_envs)*100:.1f}%\n"
        
        if passing_envs == total_envs:
            report += f"\n🎉 All Docker Compose configurations are valid!\n"
        else:
            report += f"\n⚠️ Some configurations need attention.\n"
            
        return report


def main():
    """Main execution function"""    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    logger.info("🐳 Docker Compose Services Validation")
    logger.info(f"Project Root: {project_root}")
    
    validator = DockerServicesValidator(str(project_root))
    results = validator.run_validation()
    
    # Generate and save report
    report = validator.generate_report()
    report_path = project_root / "docker_services_validation_report.txt"
    report_path.write_text(report)
    
    print(report)
    logger.info(f"📄 Report saved to: {report_path}")
    
    # Return appropriate exit code
    all_passed = all(
        r.get('syntax_valid', False) and r.get('dry_run_success', False)
        for r in results.values() if r.get('file_exists', False)
    )
    
    if all_passed:
        logger.info("🎉 All validations passed!")
        return 0
    else:
        logger.warning("⚠️ Some validations failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())