#!/usr/bin/env python3
"""
Comprehensive Infrastructure Validation Script
===============================================

Validates all infrastructure components for Ainflue Platform:
- Docker Compose services startup
- Monitoring Grafana/Prometheus configuration  
- Database schemas and migrations

Addresses the full requirement: "INFRASTRUCTURE - Docker Compose, Monitoring, Database"

Author: Fahed Mlaiel (mlaiel@live.de)
Copyright: (c) 2025 Fahed Mlaiel. All rights reserved.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('infrastructure_validation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class InfrastructureValidator:
    """Comprehensive infrastructure validation for Ainflue Platform"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts"
        self.validation_results = {}
        
    def run_docker_validation(self) -> Tuple[bool, Dict]:
        """Run Docker Compose services validation"""
        logger.info("🐳 Running Docker Compose Services Validation...")
        
        try:
            # Run Docker services validation script
            result = subprocess.run([
                sys.executable, 
                str(self.scripts_dir / "validate_docker_services.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Error running Docker validation: {str(e)}")
            return False, {'success': False, 'error': str(e)}
    
    def run_monitoring_validation(self) -> Tuple[bool, Dict]:
        """Run monitoring configuration validation"""
        logger.info("📊 Running Monitoring Configuration Validation...")
        
        try:
            # Run monitoring validation script
            result = subprocess.run([
                sys.executable, 
                str(self.scripts_dir / "validate_monitoring_config.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Error running monitoring validation: {str(e)}")
            return False, {'success': False, 'error': str(e)}
    
    def run_database_validation(self) -> Tuple[bool, Dict]:
        """Run database schema and migration validation"""
        logger.info("🗄️ Running Database Schema and Migration Validation...")
        
        try:
            # Run database validation script
            result = subprocess.run([
                sys.executable, 
                str(self.scripts_dir / "validate_database_schema.py")
            ], capture_output=True, text=True, cwd=self.project_root)
            
            success = result.returncode == 0
            
            return success, {
                'success': success,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr
            }
            
        except Exception as e:
            logger.error(f"❌ Error running database validation: {str(e)}")
            return False, {'success': False, 'error': str(e)}
    
    def check_prerequisites(self) -> Tuple[bool, List[str]]:
        """Check if all prerequisite tools are available"""
        issues = []
        
        # Check Docker
        try:
            subprocess.run(['docker', '--version'], capture_output=True, check=True)
            logger.info("✅ Docker is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Docker is not available")
        
        # Check Docker Compose
        try:
            subprocess.run(['docker', 'compose', 'version'], capture_output=True, check=True)
            logger.info("✅ Docker Compose is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            issues.append("Docker Compose is not available")
        
        # Check Python
        try:
            import yaml
            logger.info("✅ PyYAML is available")
        except ImportError:
            issues.append("PyYAML is not available (run: pip install pyyaml)")
        
        try:
            import requests
            logger.info("✅ Requests is available")
        except ImportError:
            issues.append("Requests is not available (run: pip install requests)")
        
        return len(issues) == 0, issues
    
    def generate_infrastructure_startup_guide(self) -> str:
        """Generate comprehensive startup guide"""
        guide = """
# 🚀 Ainflue Platform Infrastructure Startup Guide

## Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- Python 3.8+
- At least 8GB RAM available

## Quick Start

### 1. Start Basic Services
```bash
# Start basic platform services
docker compose up -d

# Check service health
docker compose ps
```

### 2. Start Monitoring Stack
```bash
# Start monitoring services
docker compose -f docker-compose.monitoring.yml up -d

# Access monitoring interfaces:
# - Prometheus: http://localhost:9090
# - Grafana: http://localhost:3000 (admin/admin123)
# - AlertManager: http://localhost:9093
```

### 3. Initialize Database
```bash
# Run database migrations
bash test_database_migrations.sh
```

### 4. Production Deployment
```bash
# Copy environment template
cp .env.production.example .env.production

# Edit .env.production with your configuration
# Then start production services:
docker compose -f docker-compose.production.yml --env-file .env.production up -d
```

## Health Checks

### Service Health
```bash
# Check all services
docker compose ps

# Check specific service logs
docker compose logs -f [service-name]
```

### Monitoring Health
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Check Grafana health
curl http://localhost:3000/api/health
```

### Database Health
```bash
# Check PostgreSQL
docker exec [postgres-container] pg_isready

# Check Redis
docker exec [redis-container] redis-cli ping
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check if ports 3000, 5432, 6379, 9090 are free
   - Stop conflicting services or change ports in compose files

2. **Memory Issues**
   - Ensure at least 8GB RAM available
   - Reduce replica counts in production compose file

3. **Network Issues**
   - Check Docker network configuration
   - Ensure proper DNS resolution between containers

### Getting Help

- Check logs: `docker compose logs [service]`
- View resource usage: `docker stats`
- Network debugging: `docker network ls`

For support: mlaiel@live.de
"""
        return guide
    
    def run_comprehensive_validation(self) -> Dict:
        """Run all infrastructure validations"""
        logger.info("🏗️ Starting Comprehensive Infrastructure Validation")
        logger.info("="*80)
        
        start_time = time.time()
        
        # Check prerequisites
        logger.info("\n📋 Checking Prerequisites...")
        prereq_success, prereq_issues = self.check_prerequisites()
        
        if not prereq_success:
            logger.error("❌ Prerequisites check failed:")
            for issue in prereq_issues:
                logger.error(f"   • {issue}")
            return {
                'overall_success': False,
                'prerequisites': {'success': False, 'issues': prereq_issues},
                'message': 'Prerequisites not met'
            }
        
        logger.info("✅ Prerequisites check passed")
        
        # Run individual validations
        validations = {}
        
        # 1. Docker Compose Services
        docker_success, docker_results = self.run_docker_validation()
        validations['docker'] = docker_results
        
        # 2. Monitoring Configuration
        monitoring_success, monitoring_results = self.run_monitoring_validation()
        validations['monitoring'] = monitoring_results
        
        # 3. Database Schema and Migrations
        database_success, database_results = self.run_database_validation()
        validations['database'] = database_results
        
        # Overall assessment
        overall_success = docker_success and monitoring_success and database_success
        
        # Generate startup guide
        startup_guide = self.generate_infrastructure_startup_guide()
        startup_guide_path = self.project_root / "INFRASTRUCTURE_STARTUP_GUIDE.md"
        startup_guide_path.write_text(startup_guide)
        
        end_time = time.time()
        duration = end_time - start_time
        
        self.validation_results = {
            'overall_success': overall_success,
            'duration': duration,
            'prerequisites': {'success': prereq_success, 'issues': prereq_issues},
            'validations': validations,
            'startup_guide': str(startup_guide_path)
        }
        
        return self.validation_results
    
    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive infrastructure validation report"""
        if not self.validation_results:
            return "No validation results available."
        
        results = self.validation_results
        
        report = f"""
AINFLUE PLATFORM - INFRASTRUCTURE VALIDATION REPORT
====================================================

Validation completed in {results['duration']:.2f} seconds

OVERALL STATUS: {'✅ PASSED' if results['overall_success'] else '❌ FAILED'}

COMPONENT VALIDATION RESULTS:
============================

"""
        
        # Prerequisites
        prereq = results['prerequisites']
        report += f"📋 Prerequisites: {'✅ PASSED' if prereq['success'] else '❌ FAILED'}\n"
        if prereq.get('issues'):
            for issue in prereq['issues']:
                report += f"   • {issue}\n"
        report += "\n"
        
        # Individual validations
        validations = results['validations']
        
        components = [
            ('docker', '🐳 Docker Compose Services'),
            ('monitoring', '📊 Monitoring Configuration'),
            ('database', '🗄️ Database Schema & Migrations')
        ]
        
        for component_key, component_name in components:
            if component_key in validations:
                validation = validations[component_key]
                status = '✅ PASSED' if validation['success'] else '❌ FAILED'
                report += f"{component_name}: {status}\n"
                
                if not validation['success']:
                    if 'error' in validation:
                        report += f"   Error: {validation['error']}\n"
                    if validation.get('stderr'):
                        # Show only last few lines of stderr
                        stderr_lines = validation['stderr'].strip().split('\n')[-3:]
                        for line in stderr_lines:
                            if line.strip():
                                report += f"   {line}\n"
                report += "\n"
        
        # Generated files and scripts
        report += "GENERATED FILES:\n"
        report += "===============\n"
        
        generated_files = [
            "docker_services_validation_report.txt",
            "monitoring_validation_report.txt", 
            "database_validation_report.txt",
            "test_basic_startup.sh",
            "test_monitoring_startup.sh",
            "test_production_startup.sh",
            "start_monitoring_stack.sh",
            "test_database_migrations.sh",
            "INFRASTRUCTURE_STARTUP_GUIDE.md"
        ]
        
        for file_name in generated_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                report += f"✅ {file_name}\n"
            else:
                report += f"⚠️ {file_name} (not found)\n"
        
        report += f"\n📖 Startup Guide: {results['startup_guide']}\n"
        
        # Summary and next steps
        report += "\nSUMMARY & NEXT STEPS:\n"
        report += "====================\n"
        
        if results['overall_success']:
            report += """
🎉 All infrastructure components are validated and ready!

✅ Docker Compose configurations are valid
✅ Monitoring stack is properly configured  
✅ Database schema and migrations are set up

NEXT STEPS:
1. Start basic services: docker compose up -d
2. Start monitoring: bash start_monitoring_stack.sh
3. Initialize database: bash test_database_migrations.sh
4. Follow the startup guide for detailed instructions

"""
        else:
            report += """
⚠️ Some infrastructure components need attention.

Please review the individual component reports for details:
- docker_services_validation_report.txt
- monitoring_validation_report.txt  
- database_validation_report.txt

Fix the reported issues and re-run this validation.

"""
        
        report += f"""
SUPPORT:
========
For technical support and deployment assistance:
📧 Email: mlaiel@live.de
📖 Documentation: See generated reports and startup guide

© 2025 Fahed Mlaiel. All rights reserved.
"""
        
        return report


def main():
    """Main execution function"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("""
🏗️ AINFLUE PLATFORM - INFRASTRUCTURE VALIDATION
===============================================
Validating Docker Compose, Monitoring, and Database components...
""")
    
    validator = InfrastructureValidator(str(project_root))
    results = validator.run_comprehensive_validation()
    
    # Generate and save comprehensive report
    report = validator.generate_comprehensive_report()
    report_path = project_root / "INFRASTRUCTURE_VALIDATION_REPORT.txt"
    report_path.write_text(report)
    
    print(report)
    logger.info(f"📄 Comprehensive report saved to: {report_path}")
    
    # Return appropriate exit code
    if results['overall_success']:
        logger.info("🎉 All infrastructure validation passed!")
        print("\n🚀 Your Ainflue Platform infrastructure is ready for deployment!")
        return 0
    else:
        logger.warning("⚠️ Some infrastructure validation failed!")
        print("\n⚠️ Please review the issues above and fix before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())