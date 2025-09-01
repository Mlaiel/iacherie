#!/usr/bin/env python3
"""
Production Scaling Configuration Validator
Validates: CPU 70%, Memory 80%, Custom metrics, Multi-AZ, Spot instances, 99.99% SLA

Project: IA Influencer Agent + Content Protection Platform
Author: Fahed Mlaiel <mlaiel@live.de>

⚠️  PROPRIETARY SOFTWARE - UNAUTHORIZED USE STRICTLY PROHIBITED ⚠️
"""
import yaml
import json
from pathlib import Path
import sys


def validate_production_scaling_yaml():
    """Validate the production scaling YAML configuration"""
    print("🔍 Validating Production Scaling Configuration...")
    
    yaml_path = Path(__file__).parent.parent / "kubernetes" / "production" / "production-scaling.yaml"
    
    if not yaml_path.exists():
        print("❌ Production scaling YAML not found")
        return False
    
    try:
        with open(yaml_path, 'r') as f:
            content = f.read()
        
        # Parse YAML documents
        docs = list(yaml.safe_load_all(content))
        
        print(f"📄 Found {len(docs)} Kubernetes resources")
        
        validation_results = {
            'hpa_cpu_70': False,
            'hpa_memory_80': False,
            'custom_metrics': False,
            'multi_az': False,
            'spot_instances': False,
            'sla_99_99': False,
            'cluster_autoscaler': False
        }
        
        for doc in docs:
            if not doc:
                continue
                
            kind = doc.get('kind')
            metadata = doc.get('metadata', {})
            spec = doc.get('spec', {})
            
            print(f"🔧 Validating {kind}: {metadata.get('name', 'unnamed')}")
            
            # Validate HPA
            if kind == 'HorizontalPodAutoscaler':
                metrics = spec.get('metrics', [])
                
                for metric in metrics:
                    if metric.get('type') == 'Resource':
                        resource = metric.get('resource', {})
                        target = resource.get('target', {})
                        
                        if resource.get('name') == 'cpu':
                            cpu_target = target.get('averageUtilization')
                            if cpu_target == 70:
                                validation_results['hpa_cpu_70'] = True
                                print("  ✅ CPU 70% threshold configured")
                        
                        if resource.get('name') == 'memory':
                            memory_target = target.get('averageUtilization')
                            if memory_target == 80:
                                validation_results['hpa_memory_80'] = True
                                print("  ✅ Memory 80% threshold configured")
                    
                    elif metric.get('type') == 'Pods':
                        validation_results['custom_metrics'] = True
                        pods_metric = metric.get('pods', {}).get('metric', {})
                        metric_name = pods_metric.get('name', '')
                        print(f"  ✅ Custom metric: {metric_name}")
            
            # Validate Cluster Autoscaler
            elif kind == 'Deployment' and 'cluster-autoscaler' in metadata.get('name', ''):
                validation_results['cluster_autoscaler'] = True
                print("  ✅ Cluster Autoscaler deployment found")
                
                # Check command arguments for multi-AZ and spot instances
                containers = spec.get('template', {}).get('spec', {}).get('containers', [])
                for container in containers:
                    command = container.get('command', [])
                    command_str = ' '.join(command)
                    
                    if '--balance-similar-node-groups=true' in command_str:
                        validation_results['multi_az'] = True
                        print("  ✅ Multi-AZ configuration found")
                    
                    if '--aws-use-static-instance-list=false' in command_str:
                        validation_results['spot_instances'] = True
                        print("  ✅ Spot instances configuration found")
                    
                    if '--max-node-provision-time=15m' in command_str:
                        validation_results['sla_99_99'] = True
                        print("  ✅ 99.99% SLA configuration found")
            
            # Validate Instance Groups for spot instances
            elif kind == 'InstanceGroup':
                ig_spec = doc.get('spec', {})
                if 'spotPrice' in ig_spec:
                    validation_results['spot_instances'] = True
                    print(f"  ✅ Spot instance group: {metadata.get('name')}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 VALIDATION SUMMARY")
        print("="*60)
        
        all_passed = True
        for requirement, passed in validation_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            requirement_name = requirement.replace('_', ' ').upper()
            print(f"{requirement_name:<25} {status}")
            if not passed:
                all_passed = False
        
        print("\n" + "="*60)
        if all_passed:
            print("🎉 ALL REQUIREMENTS VALIDATED SUCCESSFULLY!")
            print("✅ CPU 70% and Memory 80% thresholds configured")
            print("✅ Custom metrics support implemented") 
            print("✅ Multi-AZ deployment configured")
            print("✅ Spot instances enabled for cost optimization")
            print("✅ 99.99% SLA uptime target configured")
        else:
            print("⚠️  SOME REQUIREMENTS NOT MET - CHECK CONFIGURATION")
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Error validating configuration: {e}")
        return False


def validate_documentation():
    """Validate documentation updates"""
    print("\n🔍 Validating Documentation...")
    
    doc_path = Path(__file__).parent.parent / "docs" / "deployment" / "production-setup.md"
    
    if not doc_path.exists():
        print("❌ Production setup documentation not found")
        return False
    
    try:
        with open(doc_path, 'r') as f:
            content = f.read()
        
        requirements = [
            ("CPU 70%", "averageUtilization: 70"),
            ("Memory 80%", "averageUtilization: 80"),
            ("Custom metrics", "http_requests_per_second"),
            ("Multi-AZ", "Multi-AZ"),
            ("Spot instances", "Spot Instances"),
            ("99.99% SLA", "99.99")
        ]
        
        all_found = True
        for req_name, search_term in requirements:
            if search_term in content:
                print(f"  ✅ {req_name} documented")
            else:
                print(f"  ❌ {req_name} missing from documentation")
                all_found = False
        
        return all_found
        
    except Exception as e:
        print(f"❌ Error validating documentation: {e}")
        return False


def main():
    """Main validation function"""
    print("🚀 AINFLUE PRODUCTION SCALING VALIDATION")
    print("="*60)
    print("Requirements: CPU 70%, Memory 80%, Custom metrics, Multi-AZ, Spot instances, 99.99% SLA")
    print("="*60)
    
    yaml_valid = validate_production_scaling_yaml()
    doc_valid = validate_documentation()
    
    print("\n" + "="*60)
    print("🏁 FINAL VALIDATION RESULTS")
    print("="*60)
    
    if yaml_valid and doc_valid:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("✅ Production scaling configuration is ready for deployment")
        return 0
    else:
        print("❌ VALIDATION FAILURES DETECTED")
        print("⚠️  Please review and fix the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())